"""
楽器クラス

様々な楽器の音色を合成するクラス群。
楽器は複数の部品（波形生成・エンベロープ・フィルター）の構成を
まとめるオブジェクトとして設計。
"""

import numpy as np
from ..synthesis.oscillators import sine_wave, sawtooth_wave, white_noise
from ..synthesis.envelopes import adsr
from ..synthesis.note_utils import note_to_frequency
from ..effects.filters import LowPassFilter
from ..core.audio_signal import AudioSignal


class BaseInstrument:
    """楽器の基底クラス"""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> AudioSignal:
        """音符を演奏（派生クラスで実装）"""
        raise NotImplementedError("派生クラスで実装してください")


class SimpleSynthesizer(BaseInstrument):
    """シンプルなシンセサイザー"""

    def __init__(
        self,
        oscillator_type: str = "sine",
        attack: float = 0.1,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.2,
        sample_rate: int = 44100,
    ):
        """
        Args:
            oscillator_type: オシレーター種類 ('sine', 'sawtooth', 'square')
            attack, decay, sustain, release: ADSRパラメータ
            sample_rate: サンプリングレート (Hz)
        """
        super().__init__(sample_rate)
        self.oscillator_type = oscillator_type
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def _generate_wave(self, frequency: float, duration: float) -> AudioSignal:
        """オシレータータイプに応じた波形を生成"""
        if self.oscillator_type == "sine":
            return sine_wave(frequency, duration, sample_rate=self.sample_rate)
        elif self.oscillator_type == "sawtooth":
            return sawtooth_wave(frequency, duration, sample_rate=self.sample_rate)
        elif self.oscillator_type == "square":
            from ..synthesis.oscillators import square_wave
            return square_wave(frequency, duration, sample_rate=self.sample_rate)
        else:
            raise ValueError(f"未知のオシレータータイプ: {self.oscillator_type}")

    def play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> AudioSignal:
        """音符を演奏"""
        frequency = note_to_frequency(note_number)
        signal = self._generate_wave(frequency, duration)

        amplitude = velocity / 127.0
        envelope = adsr(duration, self.attack, self.decay, self.sustain, self.release, sample_rate=self.sample_rate)

        return signal * envelope * amplitude


class BasicPiano(BaseInstrument):
    """ピアノの音色をシミュレート"""

    def play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> AudioSignal:
        """ピアノの音を生成"""
        frequency = note_to_frequency(note_number)
        sr = self.sample_rate

        # 基音 + 倍音
        signal = sine_wave(frequency, duration, sample_rate=sr)
        harmonics = [(2.0, 0.5), (3.0, 0.25), (4.0, 0.125), (5.0, 0.063)]
        for harmonic_ratio, amp in harmonics:
            signal = signal + sine_wave(frequency * harmonic_ratio, duration, sample_rate=sr) * amp

        # ベロシティ + エンベロープ
        amplitude = velocity / 127.0
        envelope = adsr(duration, attack=0.01, decay=0.3, sustain=0.3, release=1.0, sample_rate=sr)
        signal = signal * envelope * amplitude

        # 正規化
        max_val = np.max(np.abs(signal.data))
        if max_val > 0:
            signal = signal * (0.8 / max_val)

        return signal


class BasicOrgan(BaseInstrument):
    """オルガンの音色をシミュレート"""

    def play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> AudioSignal:
        """オルガンの音を生成"""
        frequency = note_to_frequency(note_number)
        sr = self.sample_rate

        # 複数の倍音を組み合わせ
        harmonics = [(1.0, 1.0), (2.0, 0.7), (3.0, 0.5), (4.0, 0.3), (6.0, 0.2)]

        num_samples = int(sr * duration)
        signal = AudioSignal(np.zeros(num_samples), sr)
        for harmonic_ratio, amp in harmonics:
            signal = signal + sine_wave(frequency * harmonic_ratio, duration, sample_rate=sr) * amp

        # ベロシティ + エンベロープ
        amplitude = velocity / 127.0
        envelope = adsr(duration, attack=0.01, decay=0.0, sustain=1.0, release=0.1, sample_rate=sr)
        signal = signal * envelope * amplitude

        # 正規化
        max_val = np.max(np.abs(signal.data))
        if max_val > 0:
            signal = signal * (0.8 / max_val)

        return signal


class BasicGuitar(BaseInstrument):
    """ギターの音色をシミュレート"""

    def play_note(self, note_number: int, velocity: int = 100, duration: float = 1.0) -> AudioSignal:
        """ギターの音を生成"""
        frequency = note_to_frequency(note_number)
        sr = self.sample_rate

        # ノコギリ波ベース + ローパスフィルター
        signal = sawtooth_wave(frequency, duration, sample_rate=sr)
        lpf = LowPassFilter(cutoff_freq=3000, sample_rate=sr)
        signal = lpf.process(signal)

        # ベロシティ + エンベロープ
        amplitude = velocity / 127.0
        envelope = adsr(duration, attack=0.01, decay=0.2, sustain=0.6, release=0.5, sample_rate=sr)
        signal = signal * envelope * amplitude

        # 正規化
        max_val = np.max(np.abs(signal.data))
        if max_val > 0:
            signal = signal * (0.8 / max_val)

        return signal


class BasicDrum(BaseInstrument):
    """ドラムの音色をシミュレート"""

    def play_note(self, note_number: int = 60, velocity: int = 100, duration: float = 0.5) -> AudioSignal:
        """ドラム音を生成

        MIDIノート番号に基づいてドラムの種類を決定:
        - 36: キックドラム
        - 38: スネアドラム
        - 42: ハイハット
        - その他: ノイズ
        """
        sr = self.sample_rate

        if note_number == 36:  # キック
            signal = sine_wave(50, duration, sample_rate=sr)
            pitch_bend = np.exp(-np.linspace(0, 3, signal.num_samples))
            signal = signal * pitch_bend

            sub_bass = sine_wave(25, duration, sample_rate=sr)
            sub_decay = np.exp(-np.linspace(0, 4, sub_bass.num_samples))
            signal = signal + sub_bass * sub_decay * 0.5
            signal = signal * 2.0

            env = adsr(duration, attack=0.001, decay=0.15, sustain=0.0, release=0.4, sample_rate=sr)

        elif note_number == 38:  # スネア
            tone = sine_wave(200, duration, sample_rate=sr)
            noise = white_noise(duration, sample_rate=sr)
            signal = tone * 0.3 + noise * 0.7

            env = adsr(duration, attack=0.001, decay=0.05, sustain=0.0, release=0.1, sample_rate=sr)

        elif note_number == 42:  # ハイハット
            signal = white_noise(duration, sample_rate=sr)
            env = adsr(duration, attack=0.001, decay=0.02, sustain=0.0, release=0.05, sample_rate=sr)

        else:  # 汎用
            signal = white_noise(duration, sample_rate=sr)
            env = adsr(duration, attack=0.001, decay=0.1, sustain=0.0, release=0.2, sample_rate=sr)

        # ベロシティ + エンベロープ
        amplitude = velocity / 127.0
        signal = signal * env * amplitude

        # 正規化
        max_val = np.max(np.abs(signal.data))
        if max_val > 0:
            signal = signal * (0.8 / max_val)

        return signal


# エイリアス
Piano = BasicPiano
Organ = BasicOrgan
Guitar = BasicGuitar
Drum = BasicDrum
