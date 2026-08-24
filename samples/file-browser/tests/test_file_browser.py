import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import file_browser  # noqa: E402


class ContextTests(unittest.TestCase):
    def test_terminal_sanitizing_keeps_nerd_font_glyphs(self):
        value = f"before\x1b[2J{file_browser.FILE_ICON}after"
        sanitized = file_browser.safe_text(value)
        self.assertNotIn("\x1b", sanitized)
        self.assertIn(file_browser.FILE_ICON, sanitized)

    def test_focused_pane_cwd_has_priority_and_is_resolved_once(self):
        focused = Path("/focused")
        raw = json.dumps(
            {"workspace_cwd": "/workspace", "focused_pane_cwd": str(focused)}
        )
        self.assertEqual(
            file_browser.resolve_starting_directory(raw, "/fallback"), focused
        )

    def test_invalid_context_uses_the_supplied_fallback(self):
        fallback = Path("/fallback")
        for raw in (None, "not json", "[]", '{"focused_pane_cwd": ""}'):
            self.assertEqual(
                file_browser.resolve_starting_directory(raw, fallback), fallback
            )


class BrowserTests(unittest.TestCase):
    def test_startup_lists_only_direct_children_including_hidden_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "z-file.txt").touch()
            (root / ".hidden").touch()
            (root / "a-folder").mkdir()
            (root / "a-folder" / "deep.txt").touch()

            browser = file_browser.FileBrowser(root)
            rows = browser.visible_entries()

            self.assertEqual(
                [entry.path.name for entry, _ in rows], ["a-folder", ".hidden", "z-file.txt"]
            )
            self.assertTrue(all(depth == 0 for _, depth in rows))
            folder = rows[0][0]
            self.assertIsNone(folder.children, "a collapsed folder is not read at startup")

    def test_enter_lazily_loads_and_toggles_a_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "folder"
            folder.mkdir()
            (folder / "deep.txt").touch()
            browser = file_browser.FileBrowser(root)

            self.assertTrue(browser.handle_key(10))
            self.assertTrue(folder.exists())
            entry = browser.visible_entries()[0][0]
            self.assertTrue(entry.expanded)
            self.assertIsNotNone(entry.children)
            self.assertEqual(browser.visible_entries()[1][0].path.name, "deep.txt")

            self.assertTrue(browser.handle_key(10))
            self.assertFalse(entry.expanded)
            self.assertEqual(len(browser.visible_entries()), 1)

    def test_enter_on_a_file_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            file_path = root / "file.txt"
            file_path.touch()
            browser = file_browser.FileBrowser(root)
            before = (browser.selected_index, browser.scroll_offset, browser.status)

            self.assertTrue(browser.handle_key(10))
            self.assertEqual(
                (browser.selected_index, browser.scroll_offset, browser.status), before
            )
            self.assertIsNone(browser.visible_entries()[0][0].children)

    def test_selection_and_scroll_stay_in_bounds(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(8):
                (root / f"file-{number}.txt").touch()
            browser = file_browser.FileBrowser(root)

            for _ in range(20):
                browser.handle_key(file_browser.curses.KEY_DOWN)
            self.assertEqual(browser.selected_index, 7)
            browser.ensure_selection_visible(3)
            self.assertEqual(browser.scroll_offset, 5)

            for _ in range(20):
                browser.handle_key(file_browser.curses.KEY_UP)
            browser.ensure_selection_visible(3)
            self.assertEqual(browser.selected_index, 0)
            self.assertEqual(browser.scroll_offset, 0)

    def test_mouse_click_selects_the_clicked_visible_row(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(5):
                (root / f"file-{number}.txt").touch()
            browser = file_browser.FileBrowser(root)
            browser.scroll_offset = 1

            browser.handle_mouse(
                (0, 4, 2, 0, file_browser.curses.BUTTON1_PRESSED), viewport_height=3
            )

            self.assertEqual(browser.selected_index, 2)

    def test_mouse_double_click_toggles_a_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "folder"
            folder.mkdir()
            (folder / "deep.txt").touch()
            browser = file_browser.FileBrowser(root)

            browser.handle_mouse(
                (0, 2, 1, 0, file_browser.curses.BUTTON1_PRESSED),
                viewport_height=3,
            )
            browser.handle_mouse(
                (0, 2, 1, 0, file_browser.curses.BUTTON1_PRESSED),
                viewport_height=3,
            )

            self.assertTrue(browser.visible_entries()[0][0].expanded)
            self.assertEqual(browser.visible_entries()[1][0].path.name, "deep.txt")

    def test_mouse_wheel_moves_the_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(8):
                (root / f"file-{number}.txt").touch()
            browser = file_browser.FileBrowser(root)

            browser.handle_mouse(
                (0, 0, 0, 0, file_browser.curses.BUTTON5_PRESSED), viewport_height=3
            )
            self.assertEqual(browser.selected_index, file_browser.MOUSE_WHEEL_STEP)
            browser.handle_mouse(
                (0, 0, 0, 0, file_browser.curses.BUTTON4_PRESSED), viewport_height=3
            )
            self.assertEqual(browser.selected_index, 0)

    def test_footer_controls_keep_a_stable_right_edge(self):
        width = 80
        expanded = file_browser.FileBrowser.footer_text(
            "Expanded samples (2 entries)", width
        )
        collapsed = file_browser.FileBrowser.footer_text("Collapsed samples", width)
        controls = file_browser.FOOTER_CONTROLS

        self.assertTrue(expanded.endswith(controls))
        self.assertTrue(collapsed.endswith(controls))
        self.assertEqual(
            expanded.index(controls),
            collapsed.index(controls),
        )

    def test_row_text_contains_the_appropriate_nerd_font_icon(self):
        directory = file_browser.FileEntry(Path("folder"), True)
        regular_file = file_browser.FileEntry(Path("file.txt"), False)
        self.assertIn(file_browser.FOLDER_ICON, file_browser.FileBrowser.row_text(directory, 0))
        self.assertIn(file_browser.FILE_ICON, file_browser.FileBrowser.row_text(regular_file, 0))


if __name__ == "__main__":
    unittest.main()
