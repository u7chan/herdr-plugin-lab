# Herdr Plugin Lab

Herdrプラグインをローカルで試すためのサンプルです。

## 使い方

```bash
herdr plugin link "$PWD"
herdr plugin pane open \
  --plugin dev.u7chan.plugin-lab \
  --entrypoint welcome
```

絵文字入りのポップアップが開きます。何かキーを押すと閉じます。

実行コンテキストを確認する場合は、`hello` Actionを呼び出します。

```bash
herdr plugin action invoke dev.u7chan.plugin-lab.hello
herdr plugin log list --plugin dev.u7chan.plugin-lab --limit 10
```

## 構成

- `herdr-plugin.toml`: Actionとペインの定義
- `scripts/welcome.sh`: ポップアップの表示
- `scripts/hello.sh`: 実行コンテキストの出力

## 参考資料

- [Plugins - Herdr](https://herdr.dev/docs/plugins/)
- [CLI reference - Herdr](https://herdr.dev/docs/cli-reference/)
