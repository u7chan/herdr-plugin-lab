# file-browser

フォーカス中ペインの起動時ディレクトリを起点に、ファイルとフォルダを閲覧する
読み取り専用のTUIサンプルです。Pythonの標準ライブラリだけで実装しており、
ファイルの内容にはアクセスしません。

## プラグイン ID

```text
dev.u7chan.plugin-lab.file-browser
```

## 試し方

```bash
herdr plugin link "$PWD/samples/file-browser"
herdr plugin pane open \
  --plugin dev.u7chan.plugin-lab.file-browser \
  --entrypoint browser \
  --placement split \
  --direction right
```

`placement = "split"`でフォーカス中ペインの右側に表示されます。起動時の
`HERDR_PLUGIN_CONTEXT_JSON.focused_pane_cwd`を一度だけ読み取り、起動後のフォーカス移動には
追従しません。コンテキストが取得できない場合は、プロセスの作業ディレクトリを使います。

## 操作

| キー | 操作 |
| --- | --- |
| `↑` / `k` | 上へ移動 |
| `↓` / `j` | 下へ移動 |
| `PageUp` / `PageDown` | 画面単位で移動 |
| `Home` / `End` | 先頭／末尾へ移動 |
| `Enter` | フォルダを展開／折りたたみ（ファイルでは何もしない） |
| 左クリック | 行を選択 |
| ダブルクリック | フォルダを展開／折りたたみ（ファイルでは何もしない） |
| マウスホイール | 上下へ移動 |
| `q` / `Esc` | ペインを終了 |

起動時は起点ディレクトリの直下だけを表示します。フォルダの中身は最初に展開した
タイミングで読み込み、隠しファイル・隠しフォルダも表示します。

## 構成

- `herdr-plugin.toml`: `browser`ペインの定義
- `scripts/file_browser.py`: `curses`によるツリー表示とキーボード操作

このディレクトリは、研究完了後に単独のリポジトリへ移せるよう自己完結させています。
