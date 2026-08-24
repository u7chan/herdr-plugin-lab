#!/usr/bin/env python3
"""A small, read-only file browser for a Herdr split pane.

The process cwd is the plugin root, so the launch context is the only reliable source for the
directory the user wants to browse.  The context is resolved once before curses starts; the tree
never follows a later focus change.
"""

from __future__ import annotations

import curses
import json
import os
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


# These are common Nerd Font glyphs (Font Awesome).  They are display-only; no file operation is
# associated with selecting an entry or pressing Enter on a file.
FOLDER_ICON = "\uf07b"
OPEN_FOLDER_ICON = "\uf07c"
FILE_ICON = "\uf15b"

ENTER_KEYS = {10, 13, getattr(curses, "KEY_ENTER", -1)}


def safe_text(value: str) -> str:
    """Return a single terminal-safe representation of a filesystem-controlled string."""

    # A filename may contain control characters (including a newline), and undecodable Unix
    # bytes may be represented by surrogate code points.  Neither should be allowed to affect the
    # curses layout or the terminal.  Private-use code points are retained for Nerd Font icons.
    # Replacing rather than dropping keeps a malformed name recognizable.
    return "".join(
        char
        if (
            (char.isprintable() or _is_private_use(char))
            and not (0xD800 <= ord(char) <= 0xDFFF)
        )
        else "�"
        for char in value
    )


def _is_private_use(char: str) -> bool:
    codepoint = ord(char)
    return (
        0xE000 <= codepoint <= 0xF8FF
        or 0xF0000 <= codepoint <= 0xFFFFD
        or 0x100000 <= codepoint <= 0x10FFFD
    )


def character_width(char: str) -> int:
    """Return a conservative terminal cell width for one printable character."""

    if unicodedata.combining(char):
        return 0
    if unicodedata.east_asian_width(char) in {"W", "F"}:
        return 2
    return 1


def clip_text(value: str, width: int) -> str:
    """Clip *value* to ``width`` terminal cells, adding an ellipsis when it is shortened."""

    if width <= 0:
        return ""
    if sum(character_width(char) for char in value) <= width:
        return value
    if width == 1:
        return "…"

    result: list[str] = []
    used = 0
    for char in value:
        char_width = character_width(char)
        if used + char_width > width - 1:
            break
        result.append(char)
        used += char_width
    return "".join(result) + "…"


def _candidate_path(value: Any) -> Optional[Path]:
    """Convert a non-empty context value to a path, or return ``None`` for bad input."""

    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return Path(value).expanduser()
    except (OSError, RuntimeError, ValueError):
        return None


def resolve_starting_directory(
    context_json: Optional[str], fallback_cwd: Optional[os.PathLike[str] | str] = None
) -> Path:
    """Resolve the fixed browser root from Herdr's launch context.

    ``focused_pane_cwd`` is intentionally preferred over all fallbacks.  The additional context
    fallbacks make a hand-launched pane degrade usefully while preserving the same precedence as
    Herdr's workspace context.  This function is pure with respect to environment variables: the
    caller supplies the raw JSON and the fallback path explicitly.
    """

    fallback = Path(fallback_cwd) if fallback_cwd is not None else Path.cwd()
    if not context_json:
        return fallback

    try:
        context = json.loads(context_json)
    except (TypeError, ValueError):
        return fallback
    if not isinstance(context, dict):
        return fallback

    for key in ("focused_pane_cwd", "workspace_cwd", "cwd"):
        candidate = _candidate_path(context.get(key))
        if candidate is not None:
            return candidate
    return fallback


@dataclass
class FileEntry:
    """One filesystem entry and its lazily populated child list."""

    path: Path
    is_dir: bool
    children: Optional[list["FileEntry"]] = None
    expanded: bool = False
    load_error: Optional[str] = None

    def load_children(self) -> list["FileEntry"]:
        """Read immediate children once, on first expansion.

        ``follow_symlinks=False`` keeps a symlink from turning the browser into an escape hatch
        from the selected root.  Symlinks and other non-directory entries are still shown with the
        file icon, so browsing remains useful without following them.
        """

        if self.children is not None:
            return self.children
        if not self.is_dir:
            self.children = []
            return self.children

        entries: list[FileEntry] = []
        try:
            with os.scandir(self.path) as directory:
                for item in directory:
                    try:
                        is_dir = item.is_dir(follow_symlinks=False)
                    except OSError:
                        # Keep an unreadable entry visible rather than dropping it from the tree.
                        is_dir = False
                    entries.append(FileEntry(Path(item.path), is_dir))
        except OSError as error:
            reason = error.strerror or str(error)
            self.load_error = safe_text(reason)

        entries.sort(key=_entry_sort_key)
        self.children = entries
        return entries


def _entry_name(entry: FileEntry) -> str:
    name = entry.path.name
    return safe_text(name if name else str(entry.path))


def _entry_sort_key(entry: FileEntry) -> tuple[bool, str, str]:
    # Directories first, then a stable case-insensitive alphabetical order.  The original name is
    # the final tie breaker so filesystems with case-sensitive names remain deterministic.
    name = _entry_name(entry)
    return (not entry.is_dir, name.casefold(), name)


class FileBrowser:
    """In-memory tree and input state for the curses presenter."""

    def __init__(self, root: os.PathLike[str] | str):
        self.root = Path(root)
        self.root_entry = FileEntry(self.root, is_dir=True)
        # The root is not itself a row, but its direct children are available at startup.  No
        # descendant is read until its directory row is expanded.
        self.root_entry.load_children()
        self.selected_index = 0
        self.scroll_offset = 0
        self.status: Optional[str] = self.root_entry.load_error

    def visible_entries(self) -> list[tuple[FileEntry, int]]:
        """Return visible rows as ``(entry, depth)`` pairs without opening collapsed folders."""

        rows: list[tuple[FileEntry, int]] = []

        def visit(entries: list[FileEntry], depth: int) -> None:
            for entry in entries:
                rows.append((entry, depth))
                if entry.is_dir and entry.expanded:
                    visit(entry.load_children(), depth + 1)

        visit(self.root_entry.children or [], 0)
        return rows

    def selected_entry(self) -> Optional[FileEntry]:
        rows = self.visible_entries()
        if not rows:
            return None
        self._clamp_selection(len(rows))
        return rows[self.selected_index][0]

    def _clamp_selection(self, row_count: Optional[int] = None) -> None:
        count = len(self.visible_entries()) if row_count is None else row_count
        if count == 0:
            self.selected_index = 0
            self.scroll_offset = 0
            return
        self.selected_index = min(self.selected_index, count - 1)
        self.scroll_offset = min(self.scroll_offset, count - 1)

    def ensure_selection_visible(self, viewport_height: int) -> None:
        """Adjust the vertical scroll so the selected row is inside the viewport."""

        rows = self.visible_entries()
        if not rows:
            self.selected_index = 0
            self.scroll_offset = 0
            return

        self._clamp_selection(len(rows))
        viewport = max(1, viewport_height)
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + viewport:
            self.scroll_offset = self.selected_index - viewport + 1
        self.scroll_offset = min(self.scroll_offset, max(0, len(rows) - viewport))

    def move_selection(self, delta: int) -> None:
        rows = self.visible_entries()
        if not rows:
            self.selected_index = 0
            return
        self.selected_index = max(0, min(self.selected_index + delta, len(rows) - 1))

    def toggle_selected(self) -> bool:
        """Toggle the selected directory; return ``False`` for a selected file."""

        rows = self.visible_entries()
        if not rows:
            return False
        self._clamp_selection(len(rows))
        entry = rows[self.selected_index][0]
        if not entry.is_dir:
            # Enter on a file is deliberately a no-op: this sample never opens or previews files.
            return False

        if entry.expanded:
            entry.expanded = False
            self.status = f"Collapsed {_entry_name(entry)}"
        else:
            children = entry.load_children()
            entry.expanded = True
            if entry.load_error:
                self.status = f"{_entry_name(entry)}: {entry.load_error}"
            else:
                self.status = f"Expanded {_entry_name(entry)} ({len(children)} entries)"
        self._clamp_selection()
        return True

    def handle_key(self, key: int, viewport_height: int = 1) -> bool:
        """Handle one curses key code.  Return ``False`` when the pane should close."""

        if key in (ord("q"), 27, 3):  # q, Escape, Ctrl-C
            return False
        if key in (getattr(curses, "KEY_UP", -1001), ord("k")):
            self.move_selection(-1)
        elif key in (getattr(curses, "KEY_DOWN", -1002), ord("j")):
            self.move_selection(1)
        elif key in (getattr(curses, "KEY_PPAGE", -1003),):
            self.move_selection(-max(1, viewport_height - 1))
        elif key in (getattr(curses, "KEY_NPAGE", -1004), ord(" ")):
            self.move_selection(max(1, viewport_height - 1))
        elif key == getattr(curses, "KEY_HOME", -1005):
            self.selected_index = 0
        elif key == getattr(curses, "KEY_END", -1006):
            rows = self.visible_entries()
            self.selected_index = max(0, len(rows) - 1)
        elif key in ENTER_KEYS:
            self.toggle_selected()
        return True

    def handle_mouse(
        self, mouse_event: tuple[int, int, int, int, int], viewport_height: int
    ) -> None:
        """Handle a curses mouse event without performing any filesystem operation."""

        _, _, y, _, button_state = mouse_event
        wheel_up = getattr(curses, "BUTTON4_PRESSED", 0)
        wheel_down = getattr(curses, "BUTTON5_PRESSED", 0)
        if wheel_up and button_state & wheel_up:
            self.move_selection(-3)
            return
        if wheel_down and button_state & wheel_down:
            self.move_selection(3)
            return

        double_click = getattr(curses, "BUTTON1_DOUBLE_CLICKED", 0)
        single_click = getattr(curses, "BUTTON1_CLICKED", 0) | getattr(
            curses, "BUTTON1_PRESSED", 0
        )
        if not button_state & (double_click | single_click):
            return

        # Row zero is the header.  The viewport starts at row one and excludes the footer.
        visible_row = y - 1
        if visible_row < 0 or visible_row >= max(0, viewport_height):
            return
        row_index = self.scroll_offset + visible_row
        if row_index >= len(self.visible_entries()):
            return

        self.selected_index = row_index
        if double_click and button_state & double_click:
            self.toggle_selected()

    @staticmethod
    def row_text(entry: FileEntry, depth: int) -> str:
        """Build one display row with an expansion marker, Nerd Font icon, and name."""

        if entry.is_dir:
            marker = "▾" if entry.expanded else "▸"
            icon = OPEN_FOLDER_ICON if entry.expanded else FOLDER_ICON
        else:
            marker = " "
            icon = FILE_ICON
        return f"{'  ' * depth}{marker} {icon} {_entry_name(entry)}"

    @staticmethod
    def _add_line(screen: Any, row: int, text: str, width: int, attribute: int = 0) -> None:
        if row < 0 or width <= 0:
            return
        clipped = clip_text(safe_text(text), width)
        try:
            screen.addnstr(row, 0, clipped, width, attribute)
        except curses.error:
            # A resize can make a curses write race the terminal's new dimensions.  The next
            # frame will redraw it, so this is intentionally harmless.
            pass

    def draw(self, screen: Any) -> None:
        """Render the current tree to a curses window."""

        height, width = screen.getmaxyx()
        screen.erase()
        if height <= 0 or width <= 0:
            return

        header = f"{OPEN_FOLDER_ICON} Files: {self.root}"
        self._add_line(screen, 0, header, width, curses.A_BOLD)

        viewport_height = max(0, height - 2)
        self.ensure_selection_visible(viewport_height)
        rows = self.visible_entries()
        for visible_row, (entry, depth) in enumerate(
            rows[self.scroll_offset : self.scroll_offset + viewport_height], start=1
        ):
            row_index = self.scroll_offset + visible_row - 1
            attribute = curses.A_BOLD if entry.is_dir else 0
            if row_index == self.selected_index:
                attribute |= curses.A_REVERSE
            self._add_line(screen, visible_row, self.row_text(entry, depth), width, attribute)

        if self.status:
            footer = f"{self.status} · ↑↓/jk move · Enter expand/collapse · q/Esc quit"
        else:
            footer = "↑↓/jk move · PgUp/PgDn scroll · Enter expand/collapse · q/Esc quit"
        self._add_line(screen, height - 1, footer, width, curses.A_DIM)
        try:
            screen.refresh()
        except curses.error:
            pass

    def run(self, screen: Any) -> None:
        """Run the event loop until the user closes the pane."""

        screen.keypad(True)
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            curses.mouseinterval(250)
        except curses.error:
            # Keyboard operation remains available when the terminal has no mouse support.
            pass
        try:
            curses.curs_set(0)
        except curses.error:
            pass

        while True:
            height, _ = screen.getmaxyx()
            self.draw(screen)
            key = screen.getch()
            if key == getattr(curses, "KEY_MOUSE", -1):
                try:
                    self.handle_mouse(curses.getmouse(), max(1, height - 2))
                except curses.error:
                    pass
                continue
            if not self.handle_key(key, max(1, height - 2)):
                return


def main() -> int:
    # Resolve this exactly once.  In particular, do not read the context from inside the curses
    # loop: moving focus to another Herdr pane must not move the browser's root.
    root = resolve_starting_directory(
        os.environ.get("HERDR_PLUGIN_CONTEXT_JSON"), Path.cwd()
    )
    browser = FileBrowser(root)
    try:
        curses.wrapper(browser.run)
    except KeyboardInterrupt:
        # Ctrl-C is also handled as a key when curses delivers it, but this keeps direct terminal
        # launches tidy if the interrupt arrives while curses is restoring the screen.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
