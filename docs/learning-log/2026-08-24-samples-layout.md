# 2026-08-24: サンプル単位に分離する

## 今回の判断

- ルートはプラグインではなく、複数のサンプルを管理するリポジトリにする。
- 各サンプルを `samples/<name>/` に置き、独自の `herdr-plugin.toml` を持たせる。
- プラグイン ID は `dev.u7chan.plugin-lab.<sample>` とする。
- 既存の Action・ペインの基本例は `samples/hello/` にまとめる。
- サンプル固有の説明と検証結果は各サンプルの README に、横断的な知見は `docs/learning-log/` に記録する。

## 今後の配置

- Issue #3 の `safe-close-pane` は `samples/safe-close-pane/` で実装する。
- Issue #4 の `copy-cwd` は `samples/copy-cwd/` で実装する。
- 研究完了後は、各サンプルのディレクトリを単位として別リポジトリへ切り出す。
