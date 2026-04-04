# ADR-0002: Sonic Pi風の逐次記述API（LiveSession）

- **日付:** 2026-04-04
- **ステータス:** 提案
- **関連:** [Issue #7](https://github.com/ggszk/simple-sound-programming/issues/7)

## 背景

[music-programming-book](../../../music-programming-book) は「Python と Sonic Pi で学ぶ音の科学とライブコーディング」の教科書（15回構成）であり、本プロジェクトの `audio_lib` を Python パートで活用することを検討中。

Sonic Pi は `play` + `sleep` による**逐次記述**が基本:

```ruby
# Sonic Pi
use_synth :saw
play :C4, attack: 0.1, release: 0.5
sleep 0.5
play :E4
sleep 0.5
```

一方、現在の audio_lib は DAW的な**配置モデル**:

```python
# 現在の audio_lib
track = Track("melody", instrument=SimpleSynthesizer("sawtooth"))
track.add_note("C4", velocity=100, start_time=0.0, duration=0.5)
track.add_note("E4", velocity=100, start_time=0.5, duration=0.5)
audio = track.render()
```

book 側で「Sonic Pi ではこう書く、Python ではこう書く」の対比を行うにあたり、逐次記述スタイルの薄いレイヤーがあると対比が明確になる。

## 決定（案）

既存の Track/Instrument をそのまま活用し、**逐次記述のフロントエンドとなる `LiveSession` クラス**を追加する。

### API設計案

```python
from audio_lib import LiveSession

s = LiveSession(bpm=120)

# 音色選択（内部で SimpleSynthesizer を生成）
s.use_synth("saw")

# 逐次記述: play → sleep → play → sleep ...
s.play("C4", attack=0.1, release=0.5)
s.sleep(0.5)                              # 秒単位
s.play("E4")
s.sleep(0.5)

# スケール・コード（既存の create_scale を活用）
s.play_chord(["C4", "E4", "G4"], release=0.8)
s.sleep(1.0)

# レンダリング
audio = s.render()
```

### 内部実装の方針

```
LiveSession
├── current_time: float     # sleep() で進むカーソル
├── synth_type: str          # use_synth() で設定
├── track: Track             # 内部で Note を蓄積
├── instrument: Instrument   # synth_type に対応
└── effects: list[Effect]    # エフェクトチェーン（オプション）
```

- `play()` は内部で `Track.add_note(note, start_time=current_time, ...)` を呼ぶ
- `sleep()` は `current_time += seconds`
- `render()` は `Track.render()` を呼ぶ
- 実装量は100行程度の見込み

### Sonic Pi に寄せる点

| Sonic Pi | LiveSession | 備考 |
|----------|-------------|------|
| `play :C4` | `s.play("C4")` | Ruby シンボル → Python 文字列 |
| `sleep 0.5` | `s.sleep(0.5)` | 同じセマンティクス |
| `use_synth :saw` | `s.use_synth("saw")` | 文字列で音色指定 |
| `attack:`, `release:` | `attack=`, `release=` | ADSR パラメータ名は既に一致 |

### Sonic Pi に寄せない点

| Sonic Pi | audio_lib の方針 | 理由 |
|----------|-----------------|------|
| `live_loop` | Track で代替 | リアルタイム実行は教育スコープ外 |
| `with_fx :reverb do ... end` | エフェクト = 関数/オブジェクトとして適用 | Python らしい信号処理の学びを優先 |
| `:C4`（シンボル） | `"C4"`（文字列） | Python の自然な表現 |
| `ring` / `tick` | リスト + インデックス | Python の基本データ構造で十分 |

## 未決定事項

### 1. book側カリキュラムとの対応関係

book の15回構成のどの回で LiveSession を導入し、どこまで使うかが未整理。これが固まらないと API の最終スコープが決まらない。

**次のステップ:** book 側のカリキュラム構成を確認し、各回で必要な API 要素を洗い出す。

### 2. 本プロジェクトにレッスンを追加するか

- **案A:** 本プロジェクトに「Sonic Pi対比」レッスンを1つ追加
- **案B:** レッスンは book 側にのみ置き、本プロジェクトでは API だけ提供
- **案C:** 既存レッスン（lesson_06 or 07 あたり）の発展として軽く紹介

### 3. エフェクトの扱い

Sonic Pi の `with_fx` ブロックは採用しないが、LiveSession 上でエフェクトをどう適用するかの具体的 API は未定。

```python
# 案1: render 後に適用（現行の方式と同じ）
audio = s.render()
reverb = Reverb()
audio = reverb.process(audio)

# 案2: セッションにチェーンとして登録
s.add_effect(Reverb(room_size=0.8))
audio = s.render()  # エフェクト適用済み
```

## 影響

- `audio_lib/` に `live_session.py`（新規ファイル1つ）を追加
- 既存の API には変更なし（純粋な追加）
- `__init__.py` に `LiveSession` のエクスポートを追加
