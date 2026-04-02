"""
音響エフェクト

リバーブ、ディストーション、ディレイなどの効果処理。
エフェクトは内部状態（遅延バッファ等）を持つためオブジェクトとして設計。
"""

import numpy as np
from ..core.audio_signal import AudioSignal


class Reverb:
    """リバーブ（残響）エフェクト"""

    def __init__(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        sample_rate: int = 44100,
    ):
        """
        Args:
            room_size: 部屋のサイズ (0.0-1.0)
            damping: ダンピング量 (0.0-1.0)
            wet_level: エフェクト音のレベル (0.0-1.0)
            sample_rate: サンプリングレート (Hz)
        """
        self.sample_rate = sample_rate
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level
        self.reverb_time = room_size * 2.0

        # 遅延ラインの設定
        self.delay_times = [0.03, 0.05, 0.07, 0.09]
        self.delays: list[np.ndarray] = []
        self.feedbacks: list[float] = []

        for delay_time in self.delay_times:
            delay_samples = int(delay_time * sample_rate)
            self.delays.append(np.zeros(delay_samples))
            feedback = min(np.exp(-3 * delay_time / self.reverb_time), 0.9)
            self.feedbacks.append(feedback)

        self.delay_indices = [0] * len(self.delays)

    def process(self, signal: AudioSignal) -> AudioSignal:
        """リバーブエフェクトを適用

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: リバーブが適用された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            reverb_sum = 0.0

            for i, (delay_line, feedback) in enumerate(zip(self.delays, self.feedbacks)):
                delayed_sample = delay_line[self.delay_indices[i]]
                reverb_sum += delayed_sample

                damped_feedback = feedback * self.damping
                delay_line[self.delay_indices[i]] = x_n + damped_feedback * delayed_sample
                self.delay_indices[i] = (self.delay_indices[i] + 1) % len(delay_line)

            wet_signal = reverb_sum / len(self.delays)
            output[n] = self.dry_level * x_n + self.wet_level * wet_signal

        # クリッピング防止
        max_amplitude = np.max(np.abs(output))
        if max_amplitude > 1.0:
            output = output / max_amplitude

        return AudioSignal(output, signal.sample_rate)


class Distortion:
    """ディストーション（歪み）エフェクト"""

    def __init__(self, gain: float = 10.0, output_level: float = 0.5):
        """
        Args:
            gain: ゲイン（歪みの強さ）
            output_level: 出力レベル (0.0-1.0)
        """
        self.gain = gain
        self.output_level = output_level

    def process(self, signal: AudioSignal) -> AudioSignal:
        """ディストーションエフェクトを適用

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: ディストーションが適用された信号
        """
        amplified = signal.data * self.gain
        distorted = np.tanh(amplified)
        return AudioSignal(distorted * self.output_level, signal.sample_rate)


class Delay:
    """ディレイ（遅延）エフェクト"""

    def __init__(
        self,
        delay_time: float = 0.3,
        feedback: float = 0.3,
        wet_level: float = 0.3,
        sample_rate: int = 44100,
    ):
        """
        Args:
            delay_time: 遅延時間 (秒)
            feedback: フィードバック量 (0.0-1.0)
            wet_level: エフェクト音のレベル (0.0-1.0)
            sample_rate: サンプリングレート (Hz)
        """
        self.feedback = feedback
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level

        delay_samples = int(delay_time * sample_rate)
        self.delay_buffer = np.zeros(delay_samples)
        self.delay_index = 0

    def process(self, signal: AudioSignal) -> AudioSignal:
        """ディレイエフェクトを適用

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: ディレイが適用された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            delayed_sample = self.delay_buffer[self.delay_index]
            self.delay_buffer[self.delay_index] = x_n + self.feedback * delayed_sample
            output[n] = self.dry_level * x_n + self.wet_level * delayed_sample
            self.delay_index = (self.delay_index + 1) % len(self.delay_buffer)

        return AudioSignal(output, signal.sample_rate)


class Chorus:
    """コーラスエフェクト"""

    def __init__(
        self,
        rate: float = 2.0,
        depth: float = 0.002,
        wet_level: float = 0.5,
        sample_rate: int = 44100,
    ):
        """
        Args:
            rate: モジュレーション周波数 (Hz)
            depth: モジュレーションの深さ (秒)
            wet_level: エフェクト音のレベル (0.0-1.0)
            sample_rate: サンプリングレート (Hz)
        """
        self.sample_rate = sample_rate
        self.rate = rate
        self.depth = depth
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level
        self.phase = 0.0

        max_delay_samples = int((depth * 2) * sample_rate) + 1
        self.delay_buffer = np.zeros(max_delay_samples)
        self.buffer_index = 0

    def process(self, signal: AudioSignal) -> AudioSignal:
        """コーラスエフェクトを適用

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: コーラスが適用された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            self.delay_buffer[self.buffer_index] = x_n

            lfo = np.sin(2 * np.pi * self.phase)
            delay_time = self.depth * (1 + lfo)
            delay_samples = delay_time * self.sample_rate

            delay_index = (self.buffer_index - int(delay_samples)) % len(self.delay_buffer)
            delayed_sample = self.delay_buffer[delay_index]

            output[n] = self.dry_level * x_n + self.wet_level * delayed_sample

            self.buffer_index = (self.buffer_index + 1) % len(self.delay_buffer)
            self.phase += self.rate / self.sample_rate
            if self.phase >= 1.0:
                self.phase -= 1.0

        return AudioSignal(output, signal.sample_rate)


class Compressor:
    """コンプレッサー"""

    def __init__(
        self,
        threshold: float = 0.7,
        ratio: float = 4.0,
        attack: float = 0.01,
        release: float = 0.1,
        sample_rate: int = 44100,
    ):
        """
        Args:
            threshold: 閾値 (0.0-1.0)
            ratio: 圧縮比
            attack: アタック時間 (秒)
            release: リリース時間 (秒)
            sample_rate: サンプリングレート (Hz)
        """
        self.threshold = threshold
        self.ratio = ratio
        self.envelope = 0.0
        self.attack_coeff = np.exp(-1.0 / (attack * sample_rate))
        self.release_coeff = np.exp(-1.0 / (release * sample_rate))

    def process(self, signal: AudioSignal) -> AudioSignal:
        """コンプレッサーを適用

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: 圧縮された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            current_level = abs(x_n)

            if current_level > self.envelope:
                self.envelope += (current_level - self.envelope) * (1 - self.attack_coeff)
            else:
                self.envelope += (current_level - self.envelope) * (1 - self.release_coeff)

            if self.envelope > self.threshold:
                excess = self.envelope - self.threshold
                gain_reduction = 1.0 - (excess / self.ratio) / self.envelope
            else:
                gain_reduction = 1.0

            output[n] = x_n * gain_reduction

        return AudioSignal(output, signal.sample_rate)
