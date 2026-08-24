# 学習記録

## 2026-08-22: 最小構成を作る

### 分かったこと

- プラグインの実体は `herdr-plugin.toml` と、ローカルで実行できるコマンド。
- 専用 SDK はなく、Herdr CLI 全体がプラグイン API になっている。
- 開発中は `herdr plugin link <path>` で作業ディレクトリを直接登録できる。
- link したプラグインは現在ユーザーに対してグローバルで、全セッションから使える。
- Herdr はコマンドの working directory をプラグインルートにする。
- Herdr は `HERDR_BIN_PATH`、各種 ID、config/state directory、JSON context を環境変数で渡す。
- manifest の `command` は argv 配列であり、暗黙には shell を経由しない。
- プラグインは通常ユーザーの権限で動き、sandbox されない。
- Marketplace 公開は任意。個人利用ならローカル link だけでよい。

### 今回の判断

- まずは依存を増やさず Bash で action を 1 つ作る。
- config と state はリポジトリ内へ保存しない。
- 対応プラットフォームは、Bash を前提に Linux/macOS とする。

### 次の疑問

- action の出力を対話的に見せたい場合、log、popup、overlay のどれが適切か。
- 実際に作りたいワークフローには、action、pane、event のどれが合うか。
- Herdr CLI の JSON 出力を Bash で扱うか、早い段階で別言語へ移るか。

## 2026-08-24: サンプル単位に分離する

### 今回の判断

- ルートはプラグインではなく、複数のサンプルを管理するリポジトリにする。
- 各サンプルを `samples/<name>/` に置き、独自の `herdr-plugin.toml` を持たせる。
- プラグイン ID は `dev.u7chan.plugin-lab.<sample>` とする。
- 既存の Action・ペインの基本例は `samples/hello/` にまとめる。
- サンプル固有の説明と検証結果は各サンプルの README に、横断的な知見はこのファイルに記録する。

### 今後の配置

- Issue #3 の `safe-close-pane` は `samples/safe-close-pane/` で実装する。
- Issue #4 の `copy-cwd` は `samples/copy-cwd/` で実装する。
- 研究完了後は、各サンプルのディレクトリを単位として別リポジトリへ切り出す。
