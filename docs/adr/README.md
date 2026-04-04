# Architecture Decision Records (ADR)

このディレクトリには、プロジェクトの設計上の重要な決定とその経緯を記録します。

## 一覧

| ADR | タイトル | ステータス |
|-----|---------|-----------|
| [0001](0001-introduce-audio-signal.md) | AudioSignalクラスの導入とAudioConfig廃止 | 採用済み |
| [0002](0002-livesession-sonic-pi-style-api.md) | Sonic Pi風の逐次記述API（LiveSession） | 提案 |

## ADRの書き方

新しい設計決定を記録する場合、次の連番で `NNNN-タイトル.md` を作成してください。

```markdown
# ADR-NNNN: タイトル

- **日付:** YYYY-MM-DD
- **ステータス:** 提案 / 採用済み / 廃止

## 背景
なぜこの決定が必要になったか。

## 決定
何をどうすることにしたか。

## 影響
この決定によって何が変わるか。
```

参考: [MADR (Markdown Any Decision Records)](https://adr.github.io/madr/)
