"""
Jupyter/Colab ノートブック用ヘルパー関数

音声再生と波形・スペクトラム可視化のユーティリティ。
matplotlib と IPython はノートブック環境でのみ使用するため、
関数内でインポートする（ライブラリ本体の依存に含めない）。
"""

import numpy as np
from .core.audio_signal import AudioSignal


def apply_effect(signal: AudioSignal, effect) -> AudioSignal:
    """pedalboard のエフェクトを AudioSignal に適用するヘルパー

    Args:
        signal: AudioSignal オブジェクト
        effect: pedalboard のエフェクト (Reverb, Delay, Chorus 等) または Pedalboard チェーン

    Returns:
        AudioSignal: エフェクト適用後の信号
    """
    import numpy as np

    input_2d = signal.data.astype(np.float32).reshape(1, -1)
    output_2d = effect.process(input_2d, signal.sample_rate)
    return AudioSignal(output_2d.flatten().astype(np.float64), signal.sample_rate)


def play_sound(signal: AudioSignal, title: str = "Audio"):
    """音声を再生するヘルパー関数

    Args:
        signal: AudioSignal オブジェクト
        title: 表示用タイトル
    """
    from IPython.display import Audio

    print(f"🔊 {title} (サンプルレート: {signal.sample_rate} Hz)")
    # クリッピング防止のため振幅を0.8倍に抑える
    data = signal.data * 0.8
    return Audio(data, rate=signal.sample_rate, normalize=False)


def plot_waveform(signal: AudioSignal, duration: float = 0.01, title: str = "波形", figsize: tuple = (12, 4)):
    """波形を可視化するヘルパー関数

    Args:
        signal: AudioSignal オブジェクト
        duration: 表示する時間長（秒）
        title: グラフのタイトル
        figsize: 図のサイズ
    """
    import matplotlib.pyplot as plt

    time_samples = int(duration * signal.sample_rate)
    time_samples = min(time_samples, signal.num_samples)
    time_array = np.linspace(0, duration, time_samples)

    plt.figure(figsize=figsize)
    plt.plot(time_array, signal.data[:time_samples], "b-", linewidth=2)
    plt.title(title, fontsize=16)
    plt.xlabel("時間 (秒)", fontsize=12)
    plt.ylabel("振幅", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_spectrum(signal: AudioSignal, max_freq: float = 5000, title: str = "周波数スペクトラム",
                  figsize: tuple = (12, 4)):
    """周波数スペクトラムを表示するヘルパー関数

    Args:
        signal: AudioSignal オブジェクト
        max_freq: 表示する最大周波数 (Hz)
        title: グラフのタイトル
        figsize: 図のサイズ
    """
    import matplotlib.pyplot as plt

    data = signal.data
    sr = signal.sample_rate
    windowed = data * np.hanning(len(data))
    fft_result = np.fft.fft(windowed)
    fft_magnitude = np.abs(fft_result)
    fft_freq = np.fft.fftfreq(len(data), 1 / sr)

    positive_idx = fft_freq >= 0
    freq = fft_freq[positive_idx]
    magnitude = fft_magnitude[positive_idx]

    range_idx = freq <= max_freq

    plt.figure(figsize=figsize)
    plt.plot(freq[range_idx], 20 * np.log10(magnitude[range_idx] + 1e-10), "g-", linewidth=2)
    plt.title(title, fontsize=16)
    plt.xlabel("周波数 (Hz)", fontsize=12)
    plt.ylabel("振幅 (dB)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.show()
