"""
音響エフェクト

リバーブ、ディストーション、ディレイなどの効果処理。
エフェクトは内部状態（遅延バッファ等）を持つためオブジェクトとして設計。
"""

import numpy as np
from ..core.audio_signal import AudioSignal


class Reverb:
    """Schroeder方式リバーブ（残響）エフェクト

    並列コムフィルタ4本 → 直列オールパスフィルタ2本の構成。
    """

    # コムフィルタの遅延時間 (秒) — Freeverbベースの値
    _BASE_COMB_DELAYS = [0.0353, 0.0366, 0.0338, 0.0322]
    # オールパスフィルタの遅延時間 (秒)
    _ALLPASS_DELAYS = [0.0126, 0.0100]
    _ALLPASS_GAIN = 0.5
    # コムフィルタへの入力ゲイン（共振によるエネルギー蓄積を抑制）
    _INPUT_GAIN = 0.015

    def __init__(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.5,
        sample_rate: int = 44100,
    ):
        """
        Args:
            room_size: 部屋のサイズ (0.0-1.0) — フィードバック量に影響
            damping: ダンピング量 (0.0-1.0) — 高域の減衰度合い
            wet_level: エフェクト音のレベル (0.0-1.0)
            sample_rate: サンプリングレート (Hz)
        """
        self.sample_rate = sample_rate
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level
        self.dry_level = 1.0 - wet_level

        # コムフィルタの初期化
        self.comb_feedbacks: list[float] = []
        self.comb_buffers: list[np.ndarray] = []
        self.comb_indices: list[int] = []
        self.comb_filter_states: list[float] = []

        for delay_time in self._BASE_COMB_DELAYS:
            delay_samples = int(delay_time * sample_rate)
            self.comb_buffers.append(np.zeros(delay_samples))
            self.comb_indices.append(0)
            self.comb_filter_states.append(0.0)
            # room_size でフィードバック量を制御 (0.7〜0.95)
            self.comb_feedbacks.append(0.7 + room_size * 0.25)

        # オールパスフィルタの初期化
        self.ap_buffers: list[np.ndarray] = []
        self.ap_indices: list[int] = []

        for delay_time in self._ALLPASS_DELAYS:
            delay_samples = int(delay_time * sample_rate)
            self.ap_buffers.append(np.zeros(delay_samples))
            self.ap_indices.append(0)

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
            scaled_input = x_n * self._INPUT_GAIN

            # --- 並列コムフィルタ ---
            comb_sum = 0.0
            for i in range(len(self.comb_buffers)):
                buf = self.comb_buffers[i]
                idx = self.comb_indices[i]
                delayed = buf[idx]

                # ダンピング: 1次ローパスフィルタをフィードバック経路に挿入
                self.comb_filter_states[i] = (
                    delayed * (1.0 - self.damping) + self.comb_filter_states[i] * self.damping
                )
                buf[idx] = scaled_input + self.comb_feedbacks[i] * self.comb_filter_states[i]
                self.comb_indices[i] = (idx + 1) % len(buf)
                comb_sum += delayed

            mixed = comb_sum / len(self.comb_buffers)

            # --- 直列オールパスフィルタ ---
            for i in range(len(self.ap_buffers)):
                buf = self.ap_buffers[i]
                idx = self.ap_indices[i]
                delayed = buf[idx]
                buf[idx] = mixed + self._ALLPASS_GAIN * delayed
                mixed = delayed - self._ALLPASS_GAIN * mixed
                self.ap_indices[i] = (idx + 1) % len(buf)

            output[n] = self.dry_level * x_n + self.wet_level * mixed

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
