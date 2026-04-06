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
    """矩形波を生成（帯域制限付き加算合成）

    ナイキスト周波数以下の倍音のみを加算合成することで、
    エイリアシングのない矩形波を生成する。
    duty_cycle=0.5 のとき奇数次倍音のみの標準的な矩形波になる。

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
    nyquist = sample_rate / 2.0
    num_harmonics = int(nyquist / frequency)

    # 一般デューティ比のフーリエ級数:
    # x(t) = d - 0.5 + Σ (1/(kπ)) * sin(2πk*d) * cos(2πkft + kφ)
    #                - Σ (1/(kπ)) * (1 - cos(2πk*d)) * sin(2πkft + kφ)
    # ただし d = duty_cycle, k = 1, 2, 3, ...
    d = duty_cycle
    data = np.full_like(t, 2.0 * d - 1.0)  # DC成分: 2d - 1
    phase_rad = 2 * np.pi * phase
    for k in range(1, num_harmonics + 1):
        coeff = 2.0 * np.sin(k * np.pi * d) / (k * np.pi)
        if abs(coeff) > 1e-12:
            data += coeff * np.cos(2 * np.pi * k * frequency * t + k * phase_rad - k * np.pi * d)

    return AudioSignal(data, sample_rate)


def triangle_wave(frequency: float, duration: float, phase: float = 0.0, sample_rate: int = 44100) -> AudioSignal:
    """三角波を生成（帯域制限付き加算合成）

    ナイキスト周波数以下の奇数次倍音のみを加算合成することで、
    エイリアシングのない三角波を生成する。

    Args:
        frequency: 周波数 (Hz)
        duration: 継続時間 (秒)
        phase: 初期位相 (0.0-1.0)
        sample_rate: サンプリングレート (Hz)

    Returns:
        AudioSignal: 三角波データ
    """
    t = _create_time_array(duration, sample_rate)
    nyquist = sample_rate / 2.0
    num_harmonics = int(nyquist / frequency)

    # フーリエ級数: triangle(t) = 8/π² * Σ (-1)^((k-1)/2) * sin(2πkft) / k²  (奇数次のみ)
    data = np.zeros_like(t)
    phase_rad = 2 * np.pi * phase
    for k in range(1, num_harmonics + 1, 2):
        sign = (-1.0) ** ((k - 1) // 2)
        data += sign * np.sin(2 * np.pi * k * frequency * t + k * phase_rad) / (k * k)
    data *= 8.0 / (np.pi * np.pi)
    return AudioSignal(data, sample_rate)


def additive_synth(
    frequency: float, harmonics: dict, duration: float = 2.0, sample_rate: int = 44100,
) -> AudioSignal:
    """加算合成で音を生成する

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
    """
    t = _create_time_array(duration, sample_rate)
    data = np.zeros_like(t)

    for ratio, amp in harmonics.items():
        data += amp * np.sin(2 * np.pi * ratio * frequency * t)

    # 正規化（ゼロ除算を防ぐ）
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data /= max_val

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
