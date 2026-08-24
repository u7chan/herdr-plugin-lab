# Herdr Plugin Lab

Herdrプラグインで何ができるかを、小さな独立サンプルとして研究するための
リポジトリです。ルート自体はプラグインではありません。各サンプルを個別に
linkして試します。

## サンプル

| サンプル | 内容 | 状態 |
| --- | --- | --- |
| [`samples/hello`](samples/hello/) | Action、ペイン、実行コンテキストの基本 | 実装済み |
| [`samples/file-browser`](samples/file-browser/) | 起動ディレクトリ基準の読み取り専用ファイルブラウザ（Issue [#8](https://github.com/u7chan/herdr-plugin-lab/issues/8)） | 実装済み |
| `samples/safe-close-pane` | 最後のペインを閉じる前の確認（Issue [#3](https://github.com/u7chan/herdr-plugin-lab/issues/3)） | 実装予定 |
| `samples/copy-cwd` | フォーカス中ペインのパスを Windows クリップボードへコピー（Issue [#4](https://github.com/u7chan/herdr-plugin-lab/issues/4)） | 実装予定 |

各サンプルは、研究が終わった時点でディレクトリ単位で別リポジトリへ切り出せる
ように、manifest・スクリプト・固有ドキュメントを自己完結させます。

## hello を試す

```bash
herdr plugin link "$PWD/samples/hello"
herdr plugin pane open \
  --plugin dev.u7chan.plugin-lab.hello \
  --entrypoint welcome
```

絵文字入りのポップアップが開きます。何かキーを押すと閉じます。

実行コンテキストを確認する場合は、`hello` Actionを呼び出します。

```bash
herdr plugin action invoke dev.u7chan.plugin-lab.hello.hello
herdr plugin log list --plugin dev.u7chan.plugin-lab.hello --limit 10
```

## 参考資料

- [Plugins - Herdr](https://herdr.dev/docs/plugins/)
- [CLI reference - Herdr](https://herdr.dev/docs/cli-reference/)
- [学習記録](docs/learning-log/)
