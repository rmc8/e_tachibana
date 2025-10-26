# Repository Guidelines

## プロジェクト目的と参照資料
`e_tachibana` は `/Users/rmc-8.com/Code/Lib/e_tachibana/docs/md/mfds_json_api_reference.md` に記載された MFDS JSON API 仕様をもとに、Python ライブラリとして各機能を順次実装することを目的としています。実装順を問わず、常に同ファイルを一次資料として参照し、`docs/src/` 配下に API クライアントやパーサーを追加しながら、`docs/tests/` に対となるテストを整備してください。

## プロジェクト構成とモジュール配置
リポジトリ直下の `pyproject.toml` と `uv.lock` が uv ワークスペースと共有依存を定義します。実装は `docs/` 以下にまとまり、`main.py` がスクレイピングと変換のエントリーポイントです。共通ロジックは `docs/src/` に切り出し、CLI や公開 API は `docs/main.py` に集約してください。フィクスチャや HTML テンプレートは `docs/assets/`、テストは `docs/tests/` に配置し、ソース構造をミラーさせると保守しやすくなります。例えば HTML パーサーは `docs/src/parser_city.py`、対応テストは `docs/tests/test_parser_city.py` のように対で管理し、命名と import が直感的になるよう揃えてください。

## ビルド・テスト・開発コマンド
- `uv sync` – Python 3.12 環境とロック済み依存（Playwright, BeautifulSoup, html-to-markdown, lxml）を再現します。
- `uv run python docs/main.py` – スクレイパー/トランスフォーマーを通しで実行します。必要に応じて環境変数で URL などを上書きしてください。
- `uv run playwright install` – Playwright に必要なブラウザバイナリを取得します。
- `uv run pytest docs/tests -q` – テストスイートを高速に実行します。PR ごとに必須です。
CLI オプションを追加したら `uv run python docs/main.py --help` でドキュメントを更新し、`README.md` と `AGENTS.md` の説明を同期させてください。

## コーディングスタイルと命名規約
インデントは 4 スペース、モジュールと関数は `snake_case`、クラスは `PascalCase` を使用します。公開関数には型ヒントと短い docstring で副作用（ネットワーク・ファイル書き込みなど）を明示してください。責務ごとにファイルを分割し、パーサーは `parser_*.py`、通信周りは `client_*.py` のように接頭辞で分類します。プッシュ前に `uv run ruff check docs && uv run ruff format docs` を実行し、スタイルと静的解析を揃えます（未導入なら `uv tool install ruff` で追加）。型安全性が必要な箇所は `TypedDict` や `Protocol` を `docs/src/types.py` にまとめ、`uv run pyright docs` で破壊的変更を検出してください。

## テスト方針
ユニットテストは `docs/tests/test_<module>.py` という命名で追加し、外部 HTTP とファイル書き込みはフィクスチャでモックします。実際のエンドポイントを叩く統合テストは `pytest.mark.network` を付与して opt-in にしてください。重要なパーサーでは分岐カバレッジ 85% 以上を目標とし、スキーマ変更時は `uv run pytest docs/tests/test_export.py --update-golden` でゴールデンファイルを再生成します。データ変換ロジックは `pytest.mark.parametrize` で多様な入力を網羅し、例外ハンドリングは `with pytest.raises(...)` で明示的に検証します。

## コミットと PR ガイドライン
履歴が少ないため Conventional Commits（例: `feat: add playwright bootstrap`, `fix: guard empty html`）を採用してください。コミットは単一の論点と対応するテストに絞り、PR には目的・実行した検証コマンド・テスト結果・関連 Issue を明記します。スクレイピング結果が変わる場合はレンダリング前後のスニペットやスクリーンショットを添付するとレビュアーが判断しやすくなります。PR テンプレートが未整備の場合は説明欄の冒頭にチェックリスト（tests, docs, screenshots）を追記し、レビューフィードバックを `git commit --fixup` で積み上げてください。

## セキュリティと設定のヒント
資格情報やセッショントークンをハードコードせず、`.env`（git 管理外）に置いて `os.environ` 経由で参照してください。共有が必要なキーは `.env.example` にプレースホルダとして記載し、`direnv` や `uv run dotenv -- bash` など好みのツールで読み込んでください。新しいスクレイピング対象は使い捨てトークンでローカル検証し、収集した個人情報がフィクスチャやログに残らないかコミット前に確認します。Playwright 設定や API キーを変更した場合は README や PR に手順を追記し、再現性を確保してください。

## アーキテクチャと運用メモ
スクレイピングは単一 URL を処理するシンプルな構造ですが、Playwright の非同期 API を活用する場合は `asyncio.run(main())` 形式に切り替え、I/O を `async with` で明示してください。将来的に複数サイトを扱う場合は `docs/src/pipelines/` にワークフローを追加し、各パイプラインを `Registry` オブジェクトで登録するとエージェントや CI からの再利用が容易になります。
