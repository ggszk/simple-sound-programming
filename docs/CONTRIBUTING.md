# Simple Sound Programming への貢献

このプロジェクトへの貢献をご検討いただき、ありがとうございます！

## プロジェクトの目標

**サウンドプログラミング初心者の教育**を目的としたライブラリです。
高度な最適化よりも理解しやすさを重視しています。

## 貢献の方法

### Issue の報告

バグ報告や機能要求は [Issues](https://github.com/ggszk/simple-sound-programming/issues) でお願いします。

### プルリクエスト

1. リポジトリをフォーク
2. フィーチャーブランチを作成: `git checkout -b feature/amazing-feature`
3. 変更をコミット・プッシュ
4. プルリクエストを作成

## コーディング規約

- **教育性を優先**: 理解しやすさ > パフォーマンス
- **日本語コメント**: 教育目的のため、コメントは日本語
- **型ヒント**: 関数の引数と戻り値には型ヒントを使用
- **lint/フォーマット**: `uv run ruff check .` / `uv run ruff format .`

### API設計の原則

- **波形生成・エンベロープ**: 関数（状態なし）→ `AudioSignal` を返す
- **フィルター・エフェクト・楽器・シーケンサー**: オブジェクト（状態あり）→ `.process()` や `.play_note()` で `AudioSignal` を返す

```python
# 関数の例
from audio_lib import sine_wave, adsr

signal = sine_wave(440, 1.0)          # AudioSignal を返す
envelope = adsr(1.0, attack=0.1)      # AudioSignal を返す
result = signal * envelope             # 演算子で合成
```

## テスト

```bash
uv run pytest          # 全テスト実行
uv run ruff check .    # lint
```

## 質問・相談

不明な点があれば、お気軽に Issue を作成してください。
