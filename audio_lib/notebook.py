"""
Jupyter/Colab ノートブック用ヘルパー関数

音声再生と波形・スペクトラム可視化のユーティリティ。
matplotlib と IPython はノートブック環境でのみ使用するため、
関数内でインポートする（ライブラリ本体の依存に含めない）。
"""

import numpy as np
from .core.audio_signal import AudioSignal


def setup_environment():
    """ノートブック環境の共通セットアップ

    - Colab/ローカル環境を検出して日本語フォントを設定
    - matplotlib の警告を抑制
    """
    import warnings

    warnings.filterwarnings("ignore")

    try:
        import google.colab  # noqa: F401

        import japanize_matplotlib  # noqa: F401

        print("✅ Google Colab環境セットアップ完了")
    except ImportError:
        import platform

        import matplotlib.pyplot as plt

        if platform.system() == "Darwin":
            plt.rcParams["font.family"] = "Hiragino Sans"
        else:
            plt.rcParams["font.family"] = "Meiryo"
        print("✅ ローカル環境セットアップ完了")


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


def plot_harmonics(signal: AudioSignal, max_freq: float = 5000, n_harmonics: int = 20,
                   title: str = "倍音構成", figsize: tuple = (12, 4)):
    """倍音の振幅を棒グラフで表示するヘルパー関数

    スペクトラム全体ではなく、基本周波数の整数倍のピーク振幅を
    棒グラフで表示する。加算合成のレシピ確認に便利。

    Args:
        signal: AudioSignal オブジェクト
        max_freq: 探索する最大周波数 (Hz)
        n_harmonics: 表示する倍音の最大数
        title: グラフのタイトル
        figsize: 図のサイズ
    """
    import matplotlib.pyplot as plt

    data = signal.data
    sr = signal.sample_rate
    n = len(data)

    # FFT
    fft_vals = np.abs(np.fft.rfft(data)) / n * 2
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)

    # 基本周波数を検出（max_freq 以下で最も振幅が大きいピーク）
    mask = freqs <= max_freq
    fft_masked = fft_vals.copy()
    fft_masked[~mask] = 0
    f0_idx = np.argmax(fft_masked)
    f0 = freqs[f0_idx]

    if f0 < 1.0:
        print("基本周波数を検出できませんでした")
        return

    # 各倍音のピーク振幅を取得
    harmonic_freqs = []
    harmonic_amps = []
    freq_resolution = freqs[1] - freqs[0]

    for k in range(1, n_harmonics + 1):
        target_freq = f0 * k
        if target_freq > max_freq:
            break
        # ピーク周辺を探索（周波数分解能の2倍の範囲）
        search_mask = np.abs(freqs - target_freq) <= freq_resolution * 2
        if not np.any(search_mask):
            continue
        peak_amp = np.max(fft_vals[search_mask])
        harmonic_freqs.append(k)
        harmonic_amps.append(peak_amp)

    # 基本波の振幅で正規化
    if harmonic_amps and harmonic_amps[0] > 0:
        base_amp = harmonic_amps[0]
        harmonic_amps_norm = [a / base_amp for a in harmonic_amps]
    else:
        harmonic_amps_norm = harmonic_amps

    plt.figure(figsize=figsize)
    plt.bar(harmonic_freqs, harmonic_amps_norm, color='#2563EB', alpha=0.8)
    plt.title(f"{title}（基本周波数: {f0:.0f}Hz）", fontsize=14)
    plt.xlabel("倍音番号", fontsize=12)
    plt.ylabel("相対振幅（基本波 = 1.0）", fontsize=12)
    plt.xticks(harmonic_freqs)
    plt.grid(True, alpha=0.3, axis='y')
    plt.show()
