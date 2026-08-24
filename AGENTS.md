# AGENTS.md

## リポジトリの目的

Herdrプラグインの仕組みを、小さく動かしながら学ぶための個人用リポジトリ。
Marketplaceへの公開は目的としない。

## プラグインの前提

- `herdr-plugin.toml`がプラグインの契約を定義する。
- Herdrはmanifestを検証し、Action、ペイン、実行コンテキスト、ログを管理する。
- コマンドはプラグインルートを作業ディレクトリとして実行される。
- Herdr CLIを呼ぶ場合は、原則として`HERDR_BIN_PATH`を使用する。
- 設定や秘密情報は`HERDR_PLUGIN_CONFIG_DIR`、永続的な状態は`HERDR_PLUGIN_STATE_DIR`に保存する。
- `HERDR_PLUGIN_CONTEXT_JSON`と各種`HERDR_*_ID`から実行コンテキストを取得できる。

## ローカル開発

サンプルごとに独立したプラグインとして link する。以下は `hello` の例。

```bash
herdr plugin link "$PWD/samples/hello"
```

通常のソース変更はリンク先へ即時反映される。`herdr-plugin.toml`を変更した場合は再リンクする。

```bash
herdr plugin unlink dev.u7chan.plugin-lab.hello
herdr plugin link "$PWD/samples/hello"
```

`plugin link`は`[[build]]`を実行しない。ビルド工程を追加した場合は、リンク前に手動で実行する。

シェルスクリプトの構文確認:

```bash
find samples -type f -path '*/scripts/*.sh' -exec bash -n {} +
```

## 設定変更の禁止事項

- `~/.config/herdr/config.toml`など、chezmoi管理（u7chan/workstation-config）下のファイルを直接編集・追記しない。
- 動作確認はキーバインド登録なしで行う。アクションは`herdr plugin action invoke <plugin>.<action>`で実行できる。
- キーバインド等の恒久変更が必要な場合はユーザーに相談し、workstation-configリポジトリの`home/dot_config/herdr/config.toml`を修正して`chezmoi apply && herdr server reload-config`で反映する。
