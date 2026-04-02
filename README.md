# Simple Audio Programming

音響プログラミング初心者のための教育的Pythonライブラリです。
数式がそのままコードになる透明な設計で、デジタル信号処理と音響合成の基礎を学べます。

## セットアップ

```bash
# Python 3.10以上が必要
git clone https://github.com/ggszk/simple-audio-programming.git
cd simple-audio-programming

# uvがない場合: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

## 使い方

### 基本: サイン波の生成と保存

```python
from audio_lib import sine_wave, adsr, save_audio

# 440Hz（ラ音）のサイン波を1秒間生成
signal = sine_wave(440, 1.0)

# エンベロープを適用して自然な音に
envelope = adsr(1.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3)
sound = signal * envelope

# WAVファイルとして保存
save_audio("my_sound.wav", sound)
```

### 楽器を使う

```python
from audio_lib import Piano, note_name_to_number

piano = Piano()
note = note_name_to_number("C4")  # 中央のド
sound = piano.play_note(note, velocity=100, duration=2.0)
sound.save("piano_c4.wav")
```

### シーケンサーで楽曲制作

```python
from audio_lib import Sequencer, Piano, Guitar, note_name_to_number

sequencer = Sequencer()
piano_track = sequencer.add_track(Piano(), "Piano")
guitar_track = sequencer.add_track(Guitar(), "Guitar")

piano_track.add_note(note_name_to_number("C4"), 100, 0.0, 1.0)
guitar_track.add_note(note_name_to_number("E4"), 90, 1.0, 0.5)

result = sequencer.render()
result.save("my_song.wav")
```

## レッスン（Google Colab）

以下のリンクからColabで直接開けます。「ドライブにコピー」で自分用に保存してください。

| レッスン | 内容 | Colab |
|---------|------|-------|
| Lesson 01 | 基礎とサイン波 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_01_basics_and_sine_waves.ipynb) |
| Lesson 02 | エンベロープとADSR | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_02_envelopes_and_adsr.ipynb) |
| Lesson 03 | フィルターと音響設計 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_03_filters_and_sound_design.ipynb) |
| Lesson 04 | オーディオエフェクト | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_04_audio_effects_and_dynamics.ipynb) |
| Lesson 05 | MIDIとシーケンサー | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_05_midi_and_sequencer.ipynb) |
| Lesson 06 | サンプリングと分析 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_06_sampling_and_analysis.ipynb) |
| Lesson 07 | 最終プロジェクト | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_07_final_project_and_performance.ipynb) |

## API一覧

### 波形生成（関数）

| 関数 | 説明 |
|------|------|
| `sine_wave(freq, duration)` | 正弦波 |
| `sawtooth_wave(freq, duration)` | ノコギリ波 |
| `square_wave(freq, duration)` | 矩形波 |
| `triangle_wave(freq, duration)` | 三角波 |
| `white_noise(duration)` | ホワイトノイズ |
| `pink_noise(duration)` | ピンクノイズ |

### エンベロープ（関数）

| 関数 | 説明 |
|------|------|
| `adsr(duration, attack, decay, sustain, release)` | ADSRエンベロープ |
| `linear_envelope(duration, fade_in, fade_out)` | リニアエンベロープ |
| `cosine_envelope(duration, attack, release)` | コサインエンベロープ |

### 音程ユーティリティ（関数）

| 関数 | 説明 |
|------|------|
| `note_to_frequency(note_number)` | MIDIノート番号 → 周波数 |
| `frequency_to_note(frequency)` | 周波数 → MIDIノート番号 |
| `note_name_to_number(note_name)` | 音名（"C4"） → MIDIノート番号 |
| `number_to_note_name(note_number)` | MIDIノート番号 → 音名 |

### フィルター・エフェクト・楽器（オブジェクト）

全て `.process(signal)` または `.play_note(note, velocity, duration)` で `AudioSignal` を返します。

- **フィルター**: `LowPassFilter`, `HighPassFilter`, `BandPassFilter`
- **エフェクト**: `Reverb`, `Distortion`, `Delay`, `Chorus`, `Compressor`
- **楽器**: `Piano`, `Guitar`, `Organ`, `Drum` 等
- **シーケンサー**: `Sequencer`

### AudioSignal

全ての関数・メソッドが返すデータ型です。

```python
signal = sine_wave(440, 1.0)
signal.data          # numpy配列（-1.0〜1.0）
signal.sample_rate   # サンプリングレート（Hz）
signal.duration      # 長さ（秒）
signal.save("out.wav")  # WAV保存

# 演算
signal * envelope    # エンベロープ適用
signal * 0.5         # 音量調整
signal1 + signal2    # ミキシング
```

## 開発

```bash
uv sync --group dev   # 開発用依存関係
uv run pytest          # テスト
uv run ruff check .    # lint
uv run ruff format .   # フォーマット
```

詳細は [CONTRIBUTING.md](docs/CONTRIBUTING.md) をご覧ください。

## ライセンス

[MIT License](LICENSE)
