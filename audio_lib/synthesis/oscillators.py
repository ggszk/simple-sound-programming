"""
波形生成関数

各関数は周波数・長さ・サンプリングレートを受け取り、AudioSignalを返す。
状態を持たない純粋な関数として設計。
"""

import numpy as np
from ..core.audio_signal import AudioSignal


def _create_time_array(duration: float, sample_rate: int) -> np.ndarray:
    """時間軸配列を作成"""
    num_samples = int(sample_rate * duration)
    return np.linspace(0, duration, num_samples, endpoint=False)


def sine_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> AudioSignal:
    """正弦波を生成

    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        phase: 初期位相 (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: 正弦波データ
    """
    t = _create_time_array(duration, sample_rate)
    data = np.sin(2 * np.pi * frequency * t + 2 * np.pi * phase)
    return AudioSignal(data, sample_rate)


def sawtooth_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> AudioSignal:
    """ノコギリ波を生成（帯域制限付き加算合成）

    ナイキスト周波数以下の倍音のみを加算合成することで、
    エイリアシングのない滑らかなノコギリ波を生成する。

    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        phase: 初期位相 (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: ノコギリ波データ
    """
    t = _create_time_array(duration, sample_rate)
    nyquist = sample_rate / 2.0
    num_harmonics = int(nyquist / frequency)

    # フーリエ級数: sawtooth(t) = -2/π * Σ (-1)^k * sin(2πkft) / k
    data = np.zeros_like(t)
    phase_rad = 2 * np.pi * phase
    for k in range(1, num_harmonics + 1):
        data += ((-1.0) ** k) * np.sin(2 * np.pi * k * frequency * t + k * phase_rad) / k
    data *= -2.0 / np.pi

    return AudioSignal(data, sample_rate)


def square_wave(
    frequency: float, duration: float, phase: float = 0.0, duty_cycle: float = 0.5, sample_rate: int = 44100,
) -> AudioSignal:
    """矩形波を生成

    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        phase: 初期位相 (0.0-1.0)
        duty_cycle: デューティ比 (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: 矩形波データ
    """
    t = _create_time_array(duration, sample_rate)
    phase_signal = (frequency * t + phase) % 1.0
    data = np.where(phase_signal < duty_cycle, 1.0, -1.0)
    return AudioSignal(data, sample_rate)


def triangle_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> AudioSignal:
    """三角波を生成

    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        phase: 初期位相 (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: 三角波データ
    """
    t = _create_time_array(duration, sample_rate)
    phase_signal = (frequency * t + phase) % 1.0
    data = np.where(
        phase_signal < 0.5,
        4.0 * phase_signal - 1.0,   # 上昇部
        3.0 - 4.0 * phase_signal,   # 下降部
    )
    return AudioSignal(data, sample_rate)


def white_noise(duration: float, amplitude: float = 1.0, sample_rate: int = 44100) -> AudioSignal:
    """ホワイトノイズを生成

    Args:
        duration: 継続時間 (秒)
        amplitude: 振幅
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: ホワイトノイズデータ
    """
    num_samples = int(sample_rate * duration)
    data = amplitude * (2.0 * np.random.random(num_samples) - 1.0)
    return AudioSignal(data, sample_rate)


def pink_noise(duration: float, amplitude: float = 1.0, sample_rate: int = 44100) -> AudioSignal:
    """ピンクノイズを生成（簡易版）

    Args:
        duration: 継続時間 (秒)
        amplitude: 振幅
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: ピンクノイズデータ
    """
    num_samples = int(sample_rate * duration)
    white = amplitude * (2.0 * np.random.random(num_samples) - 1.0)

    # 簡易的なIIRフィルタでピンクノイズ的な特性を生成
    filtered = np.zeros_like(white)
    b0, b1, b2 = 0.99765, -1.99530, 0.99765
    a1, a2 = -1.99530, 0.99530

    for i in range(2, len(white)):
        filtered[i] = b0 * white[i] + b1 * white[i - 1] + b2 * white[i - 2] - a1 * filtered[i - 1] - a2 * filtered[i - 2]

    return AudioSignal(filtered, sample_rate)
