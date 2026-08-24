# hello

Herdrプラグインの基本サンプルです。Action、ペイン、実行コンテキストの受け渡しを
ひとつの小さなプラグインで確認できます。

## プラグイン ID

```text
dev.u7chan.plugin-lab.hello
```

## 試し方

```bash
herdr plugin link "$PWD/samples/hello"
herdr plugin pane open \
  --plugin dev.u7chan.plugin-lab.hello \
  --entrypoint welcome
```

`hello` Actionを呼び出すと、Herdrから渡された実行コンテキストを出力します。

```bash
herdr plugin action invoke dev.u7chan.plugin-lab.hello.hello
herdr plugin log list --plugin dev.u7chan.plugin-lab.hello --limit 10
```

## 構成

- `herdr-plugin.toml`: Actionとペインの定義
- `scripts/hello.sh`: 実行コンテキストの出力
- `scripts/open-welcome.sh`: welcome paneを開くAction
- `scripts/welcome.sh`: ポップアップの表示

このディレクトリは、研究完了後に単独のリポジトリへ移せるよう自己完結させています。
