# Herdr Plugin Lab

Herdr プラグインの仕組みを、小さく動かしながら学ぶための個人用リポジトリ。
現時点では Marketplace への公開を目的としない。

## 最初に理解すること

Herdr プラグインは、専用 SDK を使うライブラリではない。
次のものを置いたディレクトリを Herdr に登録すると、プラグインとして動く。

1. 契約を宣言する `herdr-plugin.toml`
2. Herdr が起動できる任意のコマンド（Bash、Node.js、Rust など）

Herdr は manifest の検証、アクションやペインの登録、実行コンテキストの注入、
ログ記録を担当する。プラグインから Herdr を操作するときは、原則として
環境変数 `HERDR_BIN_PATH` が指す CLI を呼ぶ。

## このリポジトリの最小プラグイン

```text
.
├── herdr-plugin.toml   # プラグインの宣言
└── scripts/
    └── hello.sh        # action から実行されるコマンド
```

`hello` action は、Herdr から注入された実行時情報を出力するだけの実験用コマンド。

## ローカルで動かす

リポジトリのルートで実行する。

```bash
# 作業ディレクトリをローカルプラグインとして登録
herdr plugin link "$PWD"

# まずはこれ：絵文字入りのポップアップを表示
herdr plugin pane open --plugin dev.u7chan.plugin-lab --entrypoint welcome
```

何かキーを押すとポップアップが閉じる。

ローカル設定でキーを割り当てた場合は、`prefix+e` でも表示できる。
現在の prefix が `Ctrl+Q` なら、`Ctrl+Q` を押して離し、続けて `e` を押す。

実行コンテキストを確認する従来の `hello` action も利用できる。

```bash

# 登録内容と action を確認
herdr plugin list --plugin dev.u7chan.plugin-lab
herdr plugin action list --plugin dev.u7chan.plugin-lab

# action を実行
herdr plugin action invoke dev.u7chan.plugin-lab.hello

# 標準出力・標準エラーを含む実行ログを確認
herdr plugin log list --plugin dev.u7chan.plugin-lab --limit 10
```

ソースコードはリンクされたままなので、通常の編集では再インストール不要。
`herdr-plugin.toml` を変更した場合は、確実に反映するためリンクし直す。

```bash
herdr plugin unlink dev.u7chan.plugin-lab
herdr plugin link "$PWD"
```

`plugin link` は `[[build]]` を実行しない。将来ビルドが必要な言語を使う場合、
ローカル開発中は自分でビルドしてからリンクする。

## 個人利用での位置づけ

GitHub から複製して Herdr 管理下へ置く `plugin install` は不要。
このリポジトリを `plugin link` すれば、現在ユーザーの全 Herdr セッションで使える。
Marketplace 登録に必要な GitHub topic `herdr-plugin` も付ける必要はない。

設定や秘密情報はリポジトリに置かず、次で得られる config directory に置く。

```bash
herdr plugin config-dir dev.u7chan.plugin-lab
```

永続的な実行状態は `HERDR_PLUGIN_STATE_DIR` に保存する。

## 次に試す候補

- action から `"$HERDR_BIN_PATH" workspace list` を呼ぶ
- `[[panes]]` で一時的な popup / split を開く
- `[[events]]` で `worktree.created` に反応する
- `HERDR_PLUGIN_CONTEXT_JSON` を `jq` で読んで、選択中の workspace/pane を使う
- `[[keys.command]]` を Herdr 設定に追加し、action にキーを割り当てる

学習した事実や疑問は [`docs/learning-log.md`](docs/learning-log.md) に追記する。

## 参考資料

- [Plugins - Herdr](https://herdr.dev/docs/plugins/)
- [CLI reference - Herdr](https://herdr.dev/docs/cli-reference/)
- [herdr-plugin-examples](https://github.com/ogulcancelik/herdr-plugin-examples)
