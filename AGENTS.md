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

```bash
herdr plugin link "$PWD"
```

通常のソース変更はリンク先へ即時反映される。`herdr-plugin.toml`を変更した場合は再リンクする。

```bash
herdr plugin unlink dev.u7chan.plugin-lab
herdr plugin link "$PWD"
```

`plugin link`は`[[build]]`を実行しない。ビルド工程を追加した場合は、リンク前に手動で実行する。

シェルスクリプトの構文確認:

```bash
bash -n scripts/*.sh
```
