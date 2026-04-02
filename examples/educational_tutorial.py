"""
教育用チュートリアル: 段階的な音の作り方

元のプログラムで何をしていたかを理解しやすい形で解説
"""

import numpy as np
import matplotlib.pyplot as plt
from audio_lib import (
    AudioSignal,
    sine_wave,
    sawtooth_wave,
    square_wave,
    adsr,
    linear_envelope,
    save_audio,
)
from audio_lib.effects import LowPassFilter, Reverb


def tutorial_01_what_is_sound():
    """チュートリアル1: 音とは何か？ - サイン波の基本"""
    print("=== チュートリアル1: 音とは何か？ ===")

    # 異なる周波数のサイン波を生成
    frequencies = [220, 440, 880]  # A3, A4, A5
    duration = 1.0

    print("異なる周波数のサイン波を生成します:")
    for i, freq in enumerate(frequencies):
        print(f"  {freq} Hz の音を生成中...")

        # サイン波を生成
        signal = sine_wave(freq, duration)

        # クリック音防止のエンベロープ
        envelope = linear_envelope(duration, fade_in=0.01, fade_out=0.01)
        signal = signal * envelope

        # 保存
        save_audio(f"tutorial_01_sine_{freq}hz.wav", signal)

        # 波形をプロット（最初の0.01秒分）
        plt.figure(figsize=(10, 4))

        # 時間軸
        samples_to_show = int(0.01 * signal.sample_rate)  # 0.01秒分
        t = np.linspace(0, 0.01, samples_to_show)

        plt.subplot(1, 2, 1)
        plt.plot(t, signal.data[:samples_to_show])
        plt.title(f"サイン波の波形 ({freq} Hz)")
        plt.xlabel("時間 (秒)")
        plt.ylabel("振幅")
        plt.grid(True)

        # 周波数スペクトラム
        plt.subplot(1, 2, 2)
        fft_data = np.fft.fft(signal.data[:1024])
        fft_freq = np.fft.fftfreq(1024, 1 / signal.sample_rate)
        plt.plot(fft_freq[:512], np.abs(fft_data[:512]))
        plt.title(f"周波数スペクトラム ({freq} Hz)")
        plt.xlabel("周波数 (Hz)")
        plt.ylabel("振幅")
        plt.xlim(0, 2000)
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f"tutorial_01_sine_{freq}hz_analysis.png")
        plt.close()

    print("→ tutorial_01_sine_*.wav ファイルと分析グラフを保存しました")


def tutorial_02_envelope_importance():
    """チュートリアル2: エンベロープの重要性"""
    print("\n=== チュートリアル2: エンベロープの重要性 ===")

    frequency = 440.0
    duration = 2.0

    # 1. エンベロープなし（クリック音あり）
    print("1. エンベロープなしの音（クリック音が発生）")
    signal_raw = sine_wave(frequency, duration)
    save_audio("tutorial_02_no_envelope.wav", signal_raw)

    # 2. 線形フェード
    print("2. 線形フェード付きの音")
    linear_env = linear_envelope(duration, fade_in=0.1, fade_out=0.1)
    signal_linear = signal_raw * linear_env
    save_audio("tutorial_02_linear_envelope.wav", signal_linear)

    # 3. ADSRエンベロープ
    print("3. ADSRエンベロープ付きの音（楽器らしい音）")
    adsr_env = adsr(duration, attack=0.1, decay=0.3, sustain=0.6, release=0.5, gate_time=1.5)
    signal_adsr = signal_raw * adsr_env
    save_audio("tutorial_02_adsr_envelope.wav", signal_adsr)

    # エンベロープの形状をプロット
    plt.figure(figsize=(12, 8))

    time_axis = np.linspace(0, duration, len(linear_env.data))

    plt.subplot(2, 2, 1)
    plt.plot(time_axis, np.ones_like(time_axis))
    plt.title("エンベロープなし")
    plt.ylabel("振幅")
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(time_axis, linear_env.data)
    plt.title("線形エンベロープ")
    plt.ylabel("振幅")
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.plot(time_axis, adsr_env.data)
    plt.title("ADSRエンベロープ")
    plt.xlabel("時間 (秒)")
    plt.ylabel("振幅")
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(time_axis[:1000], signal_raw.data[:1000], label="エンベロープなし")
    plt.plot(time_axis[:1000], signal_adsr.data[:1000], label="ADSR付き")
    plt.title("波形の比較（最初の部分）")
    plt.xlabel("時間 (秒)")
    plt.ylabel("振幅")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("tutorial_02_envelope_comparison.png")
    plt.close()

    print("→ tutorial_02_*.wav ファイルと比較グラフを保存しました")


def tutorial_03_waveform_types():
    """チュートリアル3: 異なる波形の音色"""
    print("\n=== チュートリアル3: 異なる波形の音色 ===")

    frequency = 440.0
    duration = 2.0

    # 異なる波形の生成関数
    wave_generators = {
        "sine": sine_wave,
        "sawtooth": sawtooth_wave,
        "square": square_wave,
    }

    # ADSRエンベロープ
    envelope = adsr(duration, attack=0.05, decay=0.2, sustain=0.7, release=0.3)

    print("異なる波形の音色を生成します:")

    plt.figure(figsize=(15, 10))

    for i, (name, generator) in enumerate(wave_generators.items()):
        print(f"  {name} 波を生成中...")

        # 波形を生成
        signal = generator(frequency, duration)
        signal = signal * envelope

        # 保存
        save_audio(f"tutorial_03_{name}_wave.wav", signal)

        # 波形をプロット
        samples_to_show = int(0.01 * signal.sample_rate)  # 0.01秒分
        t = np.linspace(0, 0.01, samples_to_show)

        plt.subplot(3, 3, i * 3 + 1)
        plt.plot(t, signal.data[:samples_to_show])
        plt.title(f"{name.capitalize()} Wave - 時間波形")
        plt.ylabel("振幅")
        plt.grid(True)

        # 周波数スペクトラム
        plt.subplot(3, 3, i * 3 + 2)
        fft_data = np.fft.fft(signal.data[:2048])
        fft_freq = np.fft.fftfreq(2048, 1 / signal.sample_rate)
        plt.plot(fft_freq[:1024], np.abs(fft_data[:1024]))
        plt.title(f"{name.capitalize()} Wave - 周波数スペクトラム")
        plt.xlabel("周波数 (Hz)")
        plt.xlim(0, 3000)
        plt.grid(True)

        # 倍音の表示
        plt.subplot(3, 3, i * 3 + 3)
        harmonics = []
        for h in range(1, 11):  # 10倍音まで
            harmonic_freq = frequency * h
            if harmonic_freq < signal.sample_rate / 2:
                # その周波数付近のスペクトラム強度を取得
                freq_index = int(harmonic_freq * 2048 / signal.sample_rate)
                if freq_index < len(fft_data):
                    harmonics.append(np.abs(fft_data[freq_index]))
                else:
                    harmonics.append(0)

        plt.bar(range(1, len(harmonics) + 1), harmonics)
        plt.title(f"{name.capitalize()} Wave - 倍音構造")
        plt.xlabel("倍音番号")
        plt.ylabel("強度")
        plt.grid(True)

    plt.tight_layout()
    plt.savefig("tutorial_03_waveform_analysis.png")
    plt.close()

    print("→ tutorial_03_*.wav ファイルと波形分析を保存しました")


def tutorial_04_filter_effects():
    """チュートリアル4: フィルターの効果"""
    print("\n=== チュートリアル4: フィルターの効果 ===")

    frequency = 220.0
    duration = 3.0

    # 基本の音を生成（倍音豊富なノコギリ波）
    signal = sawtooth_wave(frequency, duration)
    envelope = adsr(duration, attack=0.1, decay=0.2, sustain=0.8, release=0.5)
    signal = signal * envelope

    print("フィルターの効果を比較します:")

    # 1. 原音
    print("  1. 原音（フィルターなし）")
    save_audio("tutorial_04_original.wav", signal)

    # 2. ローパスフィルター（低音域のみ通す）
    print("  2. ローパスフィルター適用")
    lpf = LowPassFilter(cutoff_freq=800)
    signal_lpf = lpf.process(signal.data.copy())
    signal_lpf_audio = AudioSignal(signal_lpf, signal.sample_rate)
    save_audio("tutorial_04_lowpass.wav", signal_lpf_audio)

    # 3. さらに低いカットオフ周波数
    print("  3. より強いローパスフィルター")
    lpf_strong = LowPassFilter(cutoff_freq=400)
    signal_lpf_strong = lpf_strong.process(signal.data.copy())
    signal_lpf_strong_audio = AudioSignal(signal_lpf_strong, signal.sample_rate)
    save_audio("tutorial_04_lowpass_strong.wav", signal_lpf_strong_audio)

    # スペクトラム比較
    plt.figure(figsize=(15, 10))

    signals = {
        "原音": signal.data,
        "LPF 800Hz": signal_lpf,
        "LPF 400Hz": signal_lpf_strong,
    }

    for i, (name, sig) in enumerate(signals.items()):
        # 時間波形
        plt.subplot(3, 2, i * 2 + 1)
        samples_to_show = int(0.02 * signal.sample_rate)
        t = np.linspace(0, 0.02, samples_to_show)
        plt.plot(t, sig[:samples_to_show])
        plt.title(f"{name} - 時間波形")
        plt.ylabel("振幅")
        plt.grid(True)

        # 周波数スペクトラム
        plt.subplot(3, 2, i * 2 + 2)
        fft_data = np.fft.fft(sig[:4096])
        fft_freq = np.fft.fftfreq(4096, 1 / signal.sample_rate)
        plt.plot(fft_freq[:2048], 20 * np.log10(np.abs(fft_data[:2048]) + 1e-10))
        plt.title(f"{name} - 周波数スペクトラム")
        plt.xlabel("周波数 (Hz)")
        plt.ylabel("振幅 (dB)")
        plt.xlim(0, 2000)
        plt.ylim(-60, 20)
        plt.grid(True)

    plt.tight_layout()
    plt.savefig("tutorial_04_filter_comparison.png")
    plt.close()

    print("→ tutorial_04_*.wav ファイルとフィルター比較を保存しました")


def tutorial_05_reverb_effect():
    """チュートリアル5: リバーブ（残響）の効果"""
    print("\n=== チュートリアル5: リバーブ（残響）の効果 ===")

    # 短い音を生成（リバーブの効果がわかりやすい）
    frequency = 880.0  # A5
    duration = 0.5

    signal = sine_wave(frequency, duration)
    # 短いアタック・リリースのエンベロープ
    envelope = adsr(duration, attack=0.01, decay=0.1, sustain=0.3, release=0.1)
    signal = signal * envelope

    print("リバーブの効果を比較します:")

    # 1. ドライ音（リバーブなし）
    print("  1. ドライ音（残響なし）")
    # 無音部分を追加してリバーブテールを聞きやすくする
    signal_with_tail = AudioSignal(np.concatenate([signal.data, np.zeros(int(44100 * 2))]))
    save_audio("tutorial_05_dry.wav", signal_with_tail)

    # 2. 短いリバーブ
    print("  2. 短いリバーブ")
    reverb_short = Reverb(reverb_time=0.5, wet_level=0.3)
    signal_reverb_short_data = reverb_short.process(signal_with_tail.data.copy())
    signal_reverb_short = AudioSignal(signal_reverb_short_data, signal_with_tail.sample_rate)
    save_audio("tutorial_05_reverb_short.wav", signal_reverb_short)

    # 3. 長いリバーブ
    print("  3. 長いリバーブ（ホールのような響き）")
    reverb_long = Reverb(reverb_time=2.0, wet_level=0.5)
    signal_reverb_long_data = reverb_long.process(signal_with_tail.data.copy())
    signal_reverb_long = AudioSignal(signal_reverb_long_data, signal_with_tail.sample_rate)
    save_audio("tutorial_05_reverb_long.wav", signal_reverb_long)

    # 波形比較
    plt.figure(figsize=(15, 8))

    signals = {
        "ドライ音": signal_with_tail.data,
        "短いリバーブ": signal_reverb_short_data,
        "長いリバーブ": signal_reverb_long_data,
    }

    for i, (name, sig) in enumerate(signals.items()):
        plt.subplot(3, 1, i + 1)
        t = np.linspace(0, len(sig) / signal_with_tail.sample_rate, len(sig))
        plt.plot(t, sig)
        plt.title(f"{name} - 時間波形")
        plt.ylabel("振幅")
        plt.xlim(0, 2.5)
        plt.grid(True)

    plt.xlabel("時間 (秒)")
    plt.tight_layout()
    plt.savefig("tutorial_05_reverb_comparison.png")
    plt.close()

    print("→ tutorial_05_*.wav ファイルとリバーブ比較を保存しました")


def main():
    """全てのチュートリアルを実行"""
    print("音のプログラミング - 教育用チュートリアル")
    print("=" * 60)
    print("このチュートリアルでは、音の基本から段階的に学習できます。")
    print("生成されるWAVファイルとグラフを確認しながら進めてください。")
    print()

    try:
        tutorial_01_what_is_sound()
        tutorial_02_envelope_importance()
        tutorial_03_waveform_types()
        tutorial_04_filter_effects()
        tutorial_05_reverb_effect()

        print("\n" + "=" * 60)
        print("全てのチュートリアルが完了しました！")
        print()
        print("学習のポイント:")
        print("1. 音は周波数の異なるサイン波で構成される")
        print("2. エンベロープはクリック音防止と楽器らしさに重要")
        print("3. 波形の違いが音色（倍音構造）の違いを生む")
        print("4. フィルターは特定の周波数を強調/減衰させる")
        print("5. リバーブは空間の響きをシミュレートする")
        print()
        print("次は examples/basic_examples.py で実際の楽曲制作を試してみましょう！")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
