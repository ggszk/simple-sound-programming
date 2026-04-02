# Examples vs Tests の使い分け

## examples/ ディレクトリ
**目的**: 教育・学習・手動デバッグ

### 特徴:
- 実行すると音声ファイルや画像が生成される
- 詳細な説明メッセージが出力される  
- 学習者が「見て・聞いて」理解できる
- 開発者の手動デバッグに最適

### ファイル一覧:
- `debug_oscillators.py` - オシレーター動作確認
- `debug_envelopes.py` - エンベロープ動作確認  
- `debug_instruments.py` - 楽器クラス動作確認
- `debug_all.py` - 全機能統合確認
- `basic_examples.py` - 基本的な使用例
- `educational_tutorial.py` - 教育用チュートリアル

### 実行方法:
```bash
# 個別実行
uv run python examples/debug_oscillators.py

# 全体確認
uv run python examples/debug_all.py
```

## tests/ ディレクトリ
**目的**: 自動テスト・品質保証

### 特徴:
- CI/CDで自動実行される
- アサーションによる正確な検証
- 回帰テストによる品質保証
- pytestフレームワーク使用

### 実行方法:
```bash
# pytest実行
uv run pytest tests/

# カバレッジ付き
uv run pytest tests/ --cov=audio_lib
```

## 使い分けガイドライン

### examples/ を使用する場合:
- ✅ 新機能の動作を確認したい
- ✅ 学習者向けにデモを見せたい  
- ✅ 音声出力や波形を実際に確認したい
- ✅ インタラクティブなデバッグをしたい

### tests/ を使用する場合:  
- ✅ CI/CDでの自動テスト
- ✅ 単体テストによる正確な検証
- ✅ 回帰テストによる品質保証
- ✅ プルリクエスト時の自動チェック

## 結論
**教育ライブラリの特性上、`examples/`での手動確認が主体となり、`tests/`は補完的な役割を果たす。**
