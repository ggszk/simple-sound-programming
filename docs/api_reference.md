# audio_lib API リファレンス

*このドキュメントは `scripts/generate_api_docs.py` により docstring から自動生成されています。*

---

## Core: AudioSignal

`audio_lib.core.audio_signal`

### `AudioSignal`

音声信号データとサンプリングレートをセットで管理するクラス

```python
AudioSignal(self, data: numpy.ndarray, sample_rate: int = 44100)
```

Args:
    data: 音声データ（float64, 通常 -1.0 〜 1.0）
    sample_rate: サンプリングレート（Hz）

**メソッド:**

- `save(self, filename: str) -> None` — WAVファイルとして保存

### `save_audio(filename: str, signal: audio_lib.core.audio_signal.AudioSignal) -> None`

AudioSignalをWAVファイルとして保存

Args:
    filename: 保存先ファイル名
    signal: 保存する音声信号

### `load_audio(filename: str) -> audio_lib.core.audio_signal.AudioSignal`

WAVファイルを読み込みAudioSignalとして返す

Args:
    filename: 読み込むファイル名

Returns:
    AudioSignal: 読み込んだ音声信号

---

## 波形生成 (Oscillators)

`audio_lib.synthesis.oscillators`

### `sine_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

正弦波を生成

Args:
    frequency: 周波数 (Hz)
    duration: 継続時間 (秒)
    phase: 初期位相 (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: 正弦波データ

### `sawtooth_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

ノコギリ波を生成（帯域制限付き加算合成）

ナイキスト周波数以下の倍音のみを加算合成することで、
エイリアシングのない滑らかなノコギリ波を生成する。

Args:
    frequency: 周波数 (Hz)
    duration: 継続時間 (秒)
    phase: 初期位相 (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: ノコギリ波データ

### `square_wave(frequency: float, duration: float, phase: float = 0.0, duty_cycle: float = 0.5, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

矩形波を生成

Args:
    frequency: 周波数 (Hz)
    duration: 継続時間 (秒)
    phase: 初期位相 (0.0-1.0)
    duty_cycle: デューティ比 (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: 矩形波データ

### `triangle_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

三角波を生成

Args:
    frequency: 周波数 (Hz)
    duration: 継続時間 (秒)
    phase: 初期位相 (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: 三角波データ

### `additive_synth(frequency: float, harmonics: dict, duration: float = 2.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

加算合成で音を生成する

倍音のレシピ（辞書）を指定してサイン波を足し合わせ、音色を作る。
辞書のキーは基本周波数に対する倍率（整数でなくてもよい）、
値は各成分の振幅。出力は最大振幅 1.0 に正規化される。

Args:
    frequency: 基本周波数 (Hz)
    harmonics: 倍音のレシピ。{倍率: 振幅} の辞書
               例: {1: 1.0, 2: 0.5, 3: 0.3}
    duration: 継続時間 (秒)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: 合成された音声信号（最大振幅 1.0 に正規化）

Examples:
    >>> # ノコギリ波的な音色
    >>> sig = additive_synth(440, {k: 1.0/k for k in range(1, 11)})

    >>> # ベル風（非整数倍音）
    >>> sig = additive_synth(440, {1: 1.0, 2.76: 0.4, 3.95: 0.25})

### `white_noise(duration: float, amplitude: float = 1.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

ホワイトノイズを生成

Args:
    duration: 継続時間 (秒)
    amplitude: 振幅
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: ホワイトノイズデータ

### `pink_noise(duration: float, amplitude: float = 1.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

ピンクノイズを生成（簡易版）

Args:
    duration: 継続時間 (秒)
    amplitude: 振幅
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: ピンクノイズデータ

---

## エンベロープ (Envelopes)

`audio_lib.synthesis.envelopes`

### `adsr(duration: float, attack: float = 0.1, decay: float = 0.1, sustain: float = 0.7, release: float = 0.2, gate_time: float | None = None, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

ADSRエンベロープを生成

Args:
    duration: 全体の継続時間 (秒)
    attack: アタック時間 (秒)
    decay: ディケイ時間 (秒)
    sustain: サステインレベル (0.0-1.0)
    release: リリース時間 (秒)
    gate_time: ゲート時間 (秒)。Noneの場合はduration - release
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: ADSRエンベロープデータ

### `linear_envelope(duration: float, fade_in: float = 0.01, fade_out: float = 0.01, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

リニア（直線的）エンベロープを生成

Args:
    duration: 継続時間 (秒)
    fade_in: フェードイン時間 (秒)
    fade_out: フェードアウト時間 (秒)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: リニアエンベロープデータ

### `cosine_envelope(duration: float, attack: float = 0.1, release: float = 0.1, sustain_level: float = 1.0, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal`

コサイン型エンベロープを生成（滑らかな変化）

Args:
    duration: 継続時間 (秒)
    attack: アタック時間 (秒)
    release: リリース時間 (秒)
    sustain_level: サステインレベル (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

Returns:
    AudioSignal: コサインエンベロープデータ

---

## 音程ユーティリティ (Note Utils)

`audio_lib.synthesis.note_utils`

### `note_to_frequency(note_number)`

MIDIノート番号を周波数(Hz)に変換

Args:
    note_number (int): MIDIノート番号 (0-127, 60=中央のC)
    
Returns:
    float: 周波数 (Hz)

### `frequency_to_note(frequency)`

周波数(Hz)をMIDIノート番号に変換

Args:
    frequency (float): 周波数 (Hz)
    
Returns:
    int: MIDIノート番号

### `note_name_to_number(note_name)`

音名をMIDIノート番号に変換

Args:
    note_name (str): 音名 (例: "C4", "A#3", "Bb5")
    
Returns:
    int: MIDIノート番号

### `number_to_note_name(note_number)`

MIDIノート番号を音名に変換

Args:
    note_number (int): MIDIノート番号
    
Returns:
    str: 音名 (例: "C4", "A#3")

### `create_scale(root_note, scale_type='major')`

指定したルート音からスケールを生成

Args:
    root_note (int or str): ルート音 (MIDIノート番号または音名)
    scale_type (str): スケールタイプ ('major', 'minor', 'pentatonic')
    
Returns:
    list: スケールのMIDIノート番号リスト

---

## フィルター (Filters)

`audio_lib.effects.filters`

### `LowPassFilter`

ローパスフィルター

```python
LowPassFilter(self, cutoff_freq: float, q_factor: float = 0.707, sample_rate: int = 44100)
```

Args:
    cutoff_freq: カットオフ周波数 (Hz)
    q_factor: Q値（品質係数）
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — フィルターで信号を処理
- `reset(self) -> None` — フィルターの状態をリセット

### `HighPassFilter`

ハイパスフィルター

```python
HighPassFilter(self, cutoff_freq: float, q_factor: float = 0.707, sample_rate: int = 44100)
```

Args:
    cutoff_freq: カットオフ周波数 (Hz)
    q_factor: Q値（品質係数）
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — フィルターで信号を処理
- `reset(self) -> None` — フィルターの状態をリセット

### `BandPassFilter`

バンドパスフィルター

```python
BandPassFilter(self, center_freq: float, q_factor: float = 1.0, sample_rate: int = 44100)
```

Args:
    center_freq: 中心周波数 (Hz)
    q_factor: Q値（品質係数）
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — フィルターで信号を処理
- `reset(self) -> None` — フィルターの状態をリセット

---

## エフェクト (Effects)

`audio_lib.effects.audio_effects`

### `Reverb`

Schroeder方式リバーブ（残響）エフェクト

並列コムフィルタ4本 → 直列オールパスフィルタ2本の構成。

```python
Reverb(self, room_size: float = 0.5, damping: float = 0.5, wet_level: float = 0.5, sample_rate: int = 44100)
```

Args:
    room_size: 部屋のサイズ (0.0-1.0) — フィードバック量に影響
    damping: ダンピング量 (0.0-1.0) — 高域の減衰度合い
    wet_level: エフェクト音のレベル (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — リバーブエフェクトを適用

### `Distortion`

ディストーション（歪み）エフェクト

```python
Distortion(self, gain: float = 10.0, output_level: float = 0.5)
```

Args:
    gain: ゲイン（歪みの強さ）
    output_level: 出力レベル (0.0-1.0)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — ディストーションエフェクトを適用

### `Delay`

ディレイ（遅延）エフェクト

```python
Delay(self, delay_time: float = 0.3, feedback: float = 0.3, wet_level: float = 0.3, sample_rate: int = 44100)
```

Args:
    delay_time: 遅延時間 (秒)
    feedback: フィードバック量 (0.0-1.0)
    wet_level: エフェクト音のレベル (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — ディレイエフェクトを適用

### `Chorus`

コーラスエフェクト

```python
Chorus(self, rate: float = 2.0, depth: float = 0.002, wet_level: float = 0.5, sample_rate: int = 44100)
```

Args:
    rate: モジュレーション周波数 (Hz)
    depth: モジュレーションの深さ (秒)
    wet_level: エフェクト音のレベル (0.0-1.0)
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — コーラスエフェクトを適用

### `Compressor`

コンプレッサー

```python
Compressor(self, threshold: float = 0.7, ratio: float = 4.0, attack: float = 0.01, release: float = 0.1, sample_rate: int = 44100)
```

Args:
    threshold: 閾値 (0.0-1.0)
    ratio: 圧縮比
    attack: アタック時間 (秒)
    release: リリース時間 (秒)
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `process(self, signal: audio_lib.core.audio_signal.AudioSignal) -> audio_lib.core.audio_signal.AudioSignal` — コンプレッサーを適用

---

## 楽器 (Instruments)

`audio_lib.instruments.basic_instruments`

### `SimpleSynthesizer`

シンプルなシンセサイザー

```python
SimpleSynthesizer(self, oscillator_type: str = 'sine', attack: float = 0.1, decay: float = 0.1, sustain: float = 0.7, release: float = 0.2, sample_rate: int = 44100)
```

Args:
    oscillator_type: オシレーター種類 ('sine', 'sawtooth', 'square')
    attack, decay, sustain, release: ADSRパラメータ
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> audio_lib.core.audio_signal.AudioSignal` — 音符を演奏

### `BasicPiano`

ピアノの音色をシミュレート

```python
BasicPiano(self, sample_rate: int = 44100)
```

Initialize self.  See help(type(self)) for accurate signature.

**メソッド:**

- `play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> audio_lib.core.audio_signal.AudioSignal` — ピアノの音を生成

### `BasicOrgan`

オルガンの音色をシミュレート

```python
BasicOrgan(self, sample_rate: int = 44100)
```

Initialize self.  See help(type(self)) for accurate signature.

**メソッド:**

- `play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> audio_lib.core.audio_signal.AudioSignal` — オルガンの音を生成

### `BasicGuitar`

ギターの音色をシミュレート

```python
BasicGuitar(self, sample_rate: int = 44100)
```

Initialize self.  See help(type(self)) for accurate signature.

**メソッド:**

- `play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> audio_lib.core.audio_signal.AudioSignal` — ギターの音を生成

### `BasicDrum`

ドラムの音色をシミュレート

```python
BasicDrum(self, sample_rate: int = 44100)
```

Initialize self.  See help(type(self)) for accurate signature.

**メソッド:**

- `play_note(self, note_number: int = 60, velocity: int = 100, duration: float = 0.5) -> audio_lib.core.audio_signal.AudioSignal` — ドラム音を生成

---

## シーケンサー (Sequencer)

`audio_lib.sequencer`

### `Note`

音符を表すクラス

```python
Note(self, note_number: int | str = 60, velocity: int = 100, start_time: float = 0.0, duration: float = 1.0)
```

Args:
    note_number: MIDIノート番号または音名
    velocity: ベロシティ (0-127)
    start_time: 開始時間 (秒)
    duration: 音符の長さ (秒)

**メソッド:**

- `get_frequency(self) -> float` — ノートの周波数を取得

### `Track`

楽器トラッククラス

```python
Track(self, name: str = 'Track', instrument=None)
```

Args:
    name: トラック名
    instrument: 楽器インスタンス（後で設定可能）

**メソッド:**

- `add_note(self, note_number: int | str, velocity: int = 100, start_time: float = 0.0, duration: float = 1.0) -> audio_lib.sequencer.Note` — 音符を追加
- `add_note_instance(self, note: audio_lib.sequencer.Note) -> audio_lib.sequencer.Note` — Noteインスタンスを直接追加
- `add_notes(self, note_sequence: list) -> None` — 複数の音符を一度に追加
- `clear(self) -> None` — 全ての音符をクリア
- `get_total_duration(self) -> float` — トラックの総演奏時間を取得
- `render(self, total_duration: float | None = None, sample_rate: int = 44100) -> audio_lib.core.audio_signal.AudioSignal` — トラックを音声データとしてレンダリング
- `set_instrument(self, instrument) -> None` — 楽器を設定

### `Sequencer`

音楽シーケンサー

```python
Sequencer(self, sample_rate: int = 44100)
```

Args:
    sample_rate: サンプリングレート (Hz)

**メソッド:**

- `add_track(self, track: audio_lib.sequencer.Track) -> None` — トラックを追加
- `beats_to_seconds(self, beats: float) -> float` — 拍数を秒数に変換
- `clear_all_tracks(self) -> None` — 全てのトラックをクリア
- `get_total_duration(self) -> float` — 全トラックの総演奏時間を取得
- `remove_track(self, track_name: str) -> None` — トラックを削除
- `render(self, duration: float | None = None) -> audio_lib.core.audio_signal.AudioSignal` — 全トラックをレンダリングしてミックス
- `seconds_to_beats(self, seconds: float) -> float` — 秒数を拍数に変換
- `set_instrument(self, track_name: str, instrument) -> None` — 指定されたトラックに楽器を設定

### `create_simple_melody(track: audio_lib.sequencer.Track, notes: list, note_duration: float = 0.5, start_time: float = 0.0) -> None`

シンプルなメロディーをトラックに追加するヘルパー関数

### `create_chord(track: audio_lib.sequencer.Track, chord_notes: list, start_time: float = 0.0, duration: float = 1.0, velocity: int = 100) -> None`

和音をトラックに追加するヘルパー関数

---

## ノートブック用ヘルパー (Notebook)

`audio_lib.notebook`

### `setup_environment()`

ノートブック環境の共通セットアップ

- Colab/ローカル環境を検出して日本語フォントを設定
- matplotlib の警告を抑制

### `play_sound(signal: audio_lib.core.audio_signal.AudioSignal, title: str = 'Audio')`

音声を再生するヘルパー関数

Args:
    signal: AudioSignal オブジェクト
    title: 表示用タイトル

### `plot_waveform(signal: audio_lib.core.audio_signal.AudioSignal, duration: float = 0.01, title: str = '波形', figsize: tuple = (12, 4))`

波形を可視化するヘルパー関数

Args:
    signal: AudioSignal オブジェクト
    duration: 表示する時間長（秒）
    title: グラフのタイトル
    figsize: 図のサイズ

### `plot_spectrum(signal: audio_lib.core.audio_signal.AudioSignal, max_freq: float = 5000, title: str = '周波数スペクトラム', figsize: tuple = (12, 4))`

周波数スペクトラムを表示するヘルパー関数

Args:
    signal: AudioSignal オブジェクト
    max_freq: 表示する最大周波数 (Hz)
    title: グラフのタイトル
    figsize: 図のサイズ

### `plot_harmonics(signal: audio_lib.core.audio_signal.AudioSignal, max_freq: float = 5000, n_harmonics: int = 20, title: str = '倍音構成', figsize: tuple = (12, 4))`

倍音の振幅を棒グラフで表示するヘルパー関数

スペクトラム全体ではなく、基本周波数の整数倍のピーク振幅を
棒グラフで表示する。加算合成のレシピ確認に便利。

Args:
    signal: AudioSignal オブジェクト
    max_freq: 探索する最大周波数 (Hz)
    n_harmonics: 表示する倍音の最大数
    title: グラフのタイトル
    figsize: 図のサイズ

### `apply_effect(signal: audio_lib.core.audio_signal.AudioSignal, effect) -> audio_lib.core.audio_signal.AudioSignal`

pedalboard のエフェクトを AudioSignal に適用するヘルパー

Args:
    signal: AudioSignal オブジェクト
    effect: pedalboard のエフェクト (Reverb, Delay, Chorus 等) または Pedalboard チェーン

Returns:
    AudioSignal: エフェクト適用後の信号

---
