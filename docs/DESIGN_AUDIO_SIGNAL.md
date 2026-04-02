# AudioSignal設計書

## 動機

現行の`AudioConfig`は`sample_rate`, `bit_depth`, `max_amplitude`を混在して持ち、
全クラスのコンストラクタに渡される設計だが、以下の問題がある。

1. **性質の異なるものが混在**: `sample_rate`は音響処理の根幹、`bit_depth`/`max_amplitude`はWAV保存の実装詳細
2. **データとメタデータの分離**: 生成された信号（np.ndarray）がsample_rateを持たないため、呼び出し側が常にペアで管理する必要がある
3. **config不一致のリスク**: 各クラスが`config or AudioConfig()`で独立にデフォルト生成するため、異なるsample_rateのオブジェクトが混在しうる
4. **APIの不整合**: `save_audio`の定義と呼び出し側で引数の意味が食い違い、テストが3件失敗している

音響ライブラリの標準的な設計（librosa, scipy, pydub）に倣い、
**信号データにsample_rateを持たせる`AudioSignal`クラス**を導入し、`AudioConfig`を廃止する。

## 設計方針: 関数とオブジェクトの使い分け

状態を持たない操作は**関数**、状態を持つ操作は**オブジェクト**として設計する。
この使い分け自体がプログラミング教育の教材となる。

| 分類 | 形 | 理由 |
|------|---|------|
| 波形生成（サイン波等） | **関数** | 入力→出力の純粋な変換。内部状態なし |
| エンベロープ（ADSR等） | **関数** | 同上 |
| フィルター（LowPass等） | **オブジェクト** | 内部状態（フィルタ係数・バッファ） |
| エフェクト（Reverb等） | **オブジェクト** | 内部状態（遅延バッファ等） |
| 楽器（Piano等） | **オブジェクト** | 複数部品の構成をまとめる |
| シーケンサー | **オブジェクト** | トラック・ノート管理 |

## AudioSignalクラス

```python
class AudioSignal:
    """音声信号データとサンプリングレートをセットで管理するクラス"""

    def __init__(self, data: np.ndarray, sample_rate: int = 44100):
        self.data = data            # np.ndarray, float64, [-1.0, 1.0]
        self.sample_rate = sample_rate

    @property
    def duration(self) -> float:
        """信号の長さ（秒）"""
        return len(self.data) / self.sample_rate

    @property
    def num_samples(self) -> int:
        return len(self.data)

    def save(self, filename: str) -> None:
        """WAVファイルとして保存"""
        ...

    # --- 算術演算（教育的に重要な操作を自然に書けるようにする） ---

    def __mul__(self, other):
        """信号 * エンベロープ、信号 * 音量係数"""
        if isinstance(other, AudioSignal):
            # エンベロープ適用: signal * envelope
            _check_same_sample_rate(self, other)
            return AudioSignal(self.data * other.data, self.sample_rate)
        elif isinstance(other, (int, float, np.ndarray)):
            return AudioSignal(self.data * other, self.sample_rate)

    def __add__(self, other):
        """信号の重ね合わせ（ミキシング）"""
        if isinstance(other, AudioSignal):
            _check_same_sample_rate(self, other)
            # 長さが異なる場合はゼロパディングで合わせる
            ...
            return AudioSignal(mixed_data, self.sample_rate)

    def __rmul__(self, other):
        return self.__mul__(other)
```

### 設計判断

- **np.ndarrayのサブクラスにしない**: サブクラス化は複雑で教育向きでない。ラッパーの方がシンプル
- **`.data`で生のndarrayにアクセス可能**: NumPy操作やmatplotlibでのプロット時に使う
- **算術演算のサポート**: `signal * envelope`, `signal1 + signal2` が自然に書ける
- **sample_rateの不一致チェック**: 異なるsample_rateの信号同士の演算はエラーにする

## 各APIの変更

### 波形生成（クラス → 関数）

```python
# Before
sine = SineWave(config)
signal = sine.generate(frequency=440, duration=1.0)  # → np.ndarray

# After
signal = sine_wave(frequency=440, duration=1.0, sample_rate=44100)  # → AudioSignal
signal = sine_wave(frequency=440, duration=1.0)  # sample_rate省略時は44100
```

提供する関数:
- `sine_wave(frequency, duration, sample_rate=44100)` → AudioSignal
- `sawtooth_wave(frequency, duration, sample_rate=44100)` → AudioSignal
- `square_wave(frequency, duration, duty_cycle=0.5, sample_rate=44100)` → AudioSignal
- `triangle_wave(frequency, duration, sample_rate=44100)` → AudioSignal
- `white_noise(duration, amplitude=1.0, sample_rate=44100)` → AudioSignal
- `pink_noise(duration, amplitude=1.0, sample_rate=44100)` → AudioSignal

### エンベロープ（クラス → 関数）

```python
# Before
adsr = ADSREnvelope(attack=0.1, decay=0.2, sustain=0.7, release=0.3, config=config)
envelope = adsr.generate(duration=1.0)             # → np.ndarray
result = signal * envelope                          # np.ndarray同士の乗算

# After
envelope = adsr(duration=1.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3,
                sample_rate=44100)                  # → AudioSignal
result = signal * envelope                          # AudioSignal同士の乗算 → AudioSignal
```

提供する関数:
- `adsr(duration, attack, decay, sustain, release, gate_time=None, sample_rate=44100)` → AudioSignal
- `linear_envelope(duration, fade_in, fade_out, sample_rate=44100)` → AudioSignal

### フィルター（オブジェクト維持）

```python
# Before
lpf = LowPassFilter(cutoff_freq=1000, config=config)
filtered = lpf.process(signal)                      # np.ndarray → np.ndarray

# After
lpf = LowPassFilter(cutoff_freq=1000, sample_rate=44100)
filtered = lpf.process(signal)                      # AudioSignal → AudioSignal
```

### エフェクト（オブジェクト維持）

```python
# Before
reverb = Reverb(room_size=0.8, damping=0.5, wet_level=0.3, config=config)
wet = reverb.process(signal)                        # np.ndarray → np.ndarray

# After
reverb = Reverb(room_size=0.8, damping=0.5, wet_level=0.3, sample_rate=44100)
wet = reverb.process(signal)                        # AudioSignal → AudioSignal
```

### 楽器（オブジェクト維持）

```python
# Before
piano = BasicPiano(config)
sound = piano.play_note(note_number=60, velocity=100, duration=2.0)  # → np.ndarray

# After
piano = BasicPiano(sample_rate=44100)
sound = piano.play_note(note_number=60, velocity=100, duration=2.0)  # → AudioSignal
```

### シーケンサー（オブジェクト維持）

```python
# Before
sequencer = Sequencer(config)
result = sequencer.render(output_filename="song.wav")  # → np.ndarray

# After
sequencer = Sequencer(sample_rate=44100)
result = sequencer.render()                            # → AudioSignal
result.save("song.wav")                                # 保存は明示的に
```

### ファイルI/O

```python
# Before
save_audio("output.wav", config.sample_rate, signal)   # ← 実際の呼び出し（定義と不一致）
config, data = load_audio("input.wav")                 # → (AudioConfig, np.ndarray)

# After
signal.save("output.wav")                              # AudioSignalのメソッド
signal = load_audio("input.wav")                       # → AudioSignal

# 関数形式も提供（scipy互換の感覚で）
save_audio("output.wav", signal)                       # AudioSignalを受け取る
```

## 廃止するもの

| 廃止対象 | 理由 | 移動先 |
|---------|------|--------|
| `AudioConfig`クラス | sample_rate以外の属性が不要になる | sample_rateは各関数/クラスの引数へ、AudioSignalへ |
| `AudioConfig.bit_depth` | WAV保存の実装詳細 | `save()`の内部定数（16bit固定）またはオプション引数 |
| `AudioConfig.max_amplitude` | 保存時の安全マージン | `save()`の内部定数（0.95固定） |
| `AudioConfig.duration_to_samples()` | 各関数内でローカルに計算可能 | `int(sample_rate * duration)` |
| `AudioConfig.samples_to_duration()` | 同上 | `AudioSignal.duration`プロパティ |
| `WaveFileIO`クラス | staticメソッドのみのクラスは関数で十分 | `save_audio()`, `load_audio()` 関数 |
| `save_wav()`, `read_wav()` | エイリアスの重複 | `save_audio()`, `load_audio()` に統一 |
| `SineWave`等のオシレータークラス | 状態を持たないため関数が適切 | `sine_wave()`等の関数 |
| `ADSREnvelope`等のエンベロープクラス | 同上 | `adsr()`等の関数 |
| `apply_envelope()` | AudioSignalの`*`演算子で代替 | `signal * envelope` |

## 典型的な使用例（変更後）

### Lesson 01レベル: 基本のサイン波

```python
from audio_lib import sine_wave

signal = sine_wave(frequency=440, duration=1.0)

print(f"サンプリングレート: {signal.sample_rate}Hz")
print(f"長さ: {signal.duration}秒")
print(f"サンプル数: {signal.num_samples}")

signal.save("my_first_sound.wav")
```

### Lesson 02レベル: エンベロープ適用

```python
from audio_lib import sine_wave, adsr

signal = sine_wave(frequency=440, duration=1.0)
envelope = adsr(duration=1.0, attack=0.1, decay=0.2, sustain=0.7, release=0.3)

# 自然な記法でエンベロープ適用
shaped = signal * envelope
shaped.save("with_envelope.wav")
```

### Lesson 03レベル: フィルター

```python
from audio_lib import sawtooth_wave, LowPassFilter

signal = sawtooth_wave(frequency=440, duration=1.0)

lpf = LowPassFilter(cutoff_freq=1000)
filtered = lpf.process(signal)
filtered.save("filtered.wav")
```

### Lesson 04レベル: エフェクト

```python
from audio_lib import sine_wave, Reverb

signal = sine_wave(frequency=440, duration=1.0)

reverb = Reverb(room_size=0.8, damping=0.5, wet_level=0.3)
wet = reverb.process(signal)
wet.save("with_reverb.wav")
```

### 複合例: 関数とオブジェクトの自然な組み合わせ

```python
from audio_lib import sine_wave, adsr, LowPassFilter, Reverb

# 生成（関数: 状態なし）
signal = sine_wave(frequency=440, duration=2.0)
envelope = adsr(duration=2.0, attack=0.1, decay=0.3, sustain=0.6, release=0.5)
shaped = signal * envelope

# 加工（オブジェクト: 状態あり）
lpf = LowPassFilter(cutoff_freq=2000)
filtered = lpf.process(shaped)

reverb = Reverb(room_size=0.7, damping=0.4, wet_level=0.3)
final = reverb.process(filtered)

final.save("complete.wav")
```

## 影響範囲

### ライブラリ本体（audio_lib/）
- `core/audio_config.py` → 廃止、`core/audio_signal.py`を新設
- `core/wave_io.py` → `save_audio()`, `load_audio()`関数に簡素化
- `synthesis/oscillators.py` → クラスを関数に変更、戻り値をAudioSignalに
- `synthesis/envelopes.py` → クラスを関数に変更、戻り値をAudioSignalに
- `effects/filters.py` → config→sample_rate、入出力をAudioSignalに
- `effects/audio_effects.py` → 同上
- `instruments/basic_instruments.py` → config→sample_rate、戻り値をAudioSignalに
- `sequencer.py` → 同上
- `__init__.py` → エクスポート更新

### テスト（tests/）
- 全テストファイルのAPI呼び出しを更新
- 既存の3件の失敗が解消される

### ノートブック（colab_lessons/）・examples/
- Phase 3で新APIに更新
