# CLAUDE.md

## Project overview

サウンドプログラミング学習用の教育的Pythonライブラリ。Google Colabのノートブック（`colab_lessons/`）を通じて音響合成を学ぶ教材。

## Commands

- `uv sync --group dev` — 依存関係のインストール
- `uv run pytest` — 全テスト実行
- `uv run pytest tests/test_oscillators.py -v` — 特定ファイルのテスト
- `uv run pytest -k "test_name"` — 特定テストのみ実行
- `uv run ruff check .` — lint
- `uv run ruff format .` — フォーマット

## Structure

- `audio_lib/` — メインライブラリ（core, synthesis, effects, instruments, sequencer）
- `colab_lessons/` — Google Colab用レッスンノートブック（lesson_01〜07）
- `examples/` — 使用例・デバッグツール
- `tests/` — テストコード
- `docs/` — ドキュメント

## Style

- lint/フォーマット: ruff (line-length=127, 設定は `pyproject.toml`)
- 型チェック: mypy (strict)
- コミットメッセージ: 日本語
