"""
デジタルフィルター

ローパス、ハイパス、バンドパスなどの基本的なフィルター。
フィルターは内部状態（係数・バッファ）を持つためオブジェクトとして設計。
"""

import numpy as np
from ..core.audio_signal import AudioSignal


class BiquadFilter:
    """2次IIRフィルター（バイクアッドフィルター）"""

    def __init__(self, b_coeffs: list[float], a_coeffs: list[float]):
        """
        Args:
            b_coeffs: 分子係数 [b0, b1, b2]
            a_coeffs: 分母係数 [a0, a1, a2] (a0は通常1.0)
        """
        self.b = b_coeffs
        self.a = a_coeffs
        self.reset()

    def reset(self) -> None:
        """フィルターの状態をリセット"""
        self.x_history = [0.0, 0.0]
        self.y_history = [0.0, 0.0]

    def process(self, signal: AudioSignal) -> AudioSignal:
        """フィルターで信号を処理

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: フィルター処理された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            y_n = (
                self.b[0] * x_n
                + self.b[1] * self.x_history[0]
                + self.b[2] * self.x_history[1]
                - self.a[1] * self.y_history[0]
                - self.a[2] * self.y_history[1]
            )

            output[n] = y_n

            self.x_history[1] = self.x_history[0]
            self.x_history[0] = x_n
            self.y_history[1] = self.y_history[0]
            self.y_history[0] = y_n

        return AudioSignal(output, signal.sample_rate)


def _biquad_coeffs_lowpass(cutoff_freq: float, q_factor: float, sample_rate: int) -> tuple[list[float], list[float]]:
    """ローパスフィルターのバイクアッド係数を計算"""
    omega = 2 * np.pi * cutoff_freq / sample_rate
    sin_omega = np.sin(omega)
    cos_omega = np.cos(omega)
    alpha = sin_omega / (2 * q_factor)

    b0 = (1 - cos_omega) / 2
    b1 = 1 - cos_omega
    b2 = (1 - cos_omega) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_omega
    a2 = 1 - alpha

    return [b0 / a0, b1 / a0, b2 / a0], [1.0, a1 / a0, a2 / a0]


def _biquad_coeffs_highpass(cutoff_freq: float, q_factor: float, sample_rate: int) -> tuple[list[float], list[float]]:
    """ハイパスフィルターのバイクアッド係数を計算"""
    omega = 2 * np.pi * cutoff_freq / sample_rate
    sin_omega = np.sin(omega)
    cos_omega = np.cos(omega)
    alpha = sin_omega / (2 * q_factor)

    b0 = (1 + cos_omega) / 2
    b1 = -(1 + cos_omega)
    b2 = (1 + cos_omega) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_omega
    a2 = 1 - alpha

    return [b0 / a0, b1 / a0, b2 / a0], [1.0, a1 / a0, a2 / a0]


def _biquad_coeffs_bandpass(center_freq: float, q_factor: float, sample_rate: int) -> tuple[list[float], list[float]]:
    """バンドパスフィルターのバイクアッド係数を計算"""
    omega = 2 * np.pi * center_freq / sample_rate
    sin_omega = np.sin(omega)
    cos_omega = np.cos(omega)
    alpha = sin_omega / (2 * q_factor)

    b0 = alpha
    b1 = 0
    b2 = -alpha
    a0 = 1 + alpha
    a1 = -2 * cos_omega
    a2 = 1 - alpha

    return [b0 / a0, b1 / a0, b2 / a0], [1.0, a1 / a0, a2 / a0]


class LowPassFilter(BiquadFilter):
    """ローパスフィルター"""

    def __init__(self, cutoff_freq: float, q_factor: float = 0.707, sample_rate: int = 44100):
        """
        Args:
            cutoff_freq: カットオフ周波数 (Hz)
            q_factor: Q値（品質係数）
            sample_rate: サンプリングレート (Hz)
        """
        b, a = _biquad_coeffs_lowpass(cutoff_freq, q_factor, sample_rate)
        super().__init__(b, a)


class HighPassFilter(BiquadFilter):
    """ハイパスフィルター"""

    def __init__(self, cutoff_freq: float, q_factor: float = 0.707, sample_rate: int = 44100):
        """
        Args:
            cutoff_freq: カットオフ周波数 (Hz)
            q_factor: Q値（品質係数）
            sample_rate: サンプリングレート (Hz)
        """
        b, a = _biquad_coeffs_highpass(cutoff_freq, q_factor, sample_rate)
        super().__init__(b, a)


class BandPassFilter(BiquadFilter):
    """バンドパスフィルター"""

    def __init__(self, center_freq: float, q_factor: float = 1.0, sample_rate: int = 44100):
        """
        Args:
            center_freq: 中心周波数 (Hz)
            q_factor: Q値（品質係数）
            sample_rate: サンプリングレート (Hz)
        """
        b, a = _biquad_coeffs_bandpass(center_freq, q_factor, sample_rate)
        super().__init__(b, a)


class SimpleMovingAverageFilter:
    """移動平均フィルター（簡単なローパス効果）"""

    def __init__(self, window_size: int = 3):
        """
        Args:
            window_size: 窓のサイズ
        """
        self.window_size = window_size
        self.reset()

    def reset(self) -> None:
        """フィルターの状態をリセット"""
        self.buffer = np.zeros(self.window_size)
        self.index = 0

    def process(self, signal: AudioSignal) -> AudioSignal:
        """移動平均フィルターで信号を処理

        Args:
            signal: 入力信号

        Returns:
            AudioSignal: フィルター処理された信号
        """
        input_data = signal.data
        output = np.zeros_like(input_data)

        for n, x_n in enumerate(input_data):
            self.buffer[self.index] = x_n
            self.index = (self.index + 1) % self.window_size
            output[n] = np.mean(self.buffer)

        return AudioSignal(output, signal.sample_rate)
