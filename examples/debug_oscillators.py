#!/usr/bin/env python3
"""
デバッグ用: オシレーターのテスト

オシレーター（sine_wave, sawtooth_wave, square_wave）の動作確認とデバッグ
"""

import numpy as np
import matplotlib.pyplot as plt
from audio_lib import sine_wave, sawtooth_wave, square_wave, save_audio


def debug_sine_wave():
    """sine_waveオシレーターのデバッグ"""
    print("🔍 sine_waveオシレーターのデバッグ開始...")

    # 基本的なサイン波生成テスト
    frequency = 440.0
    duration = 1.0

    try:
        signal = sine_wave(frequency, duration)
        print(f"✅ サイン波生成成功: {signal.num_samples} サンプル")
        print(f"   周波数: {frequency} Hz")
        print(f"   長さ: {duration} 秒")
        print(f"   最大振幅: {np.max(signal.data):.3f}")
        print(f"   最小振幅: {np.min(signal.data):.3f}")

        # ファイル保存テスト
        save_audio("debug_sine_440hz.wav", signal)
        print("✅ ファイル保存成功: debug_sine_440hz.wav")

        return signal

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None


def debug_sawtooth_wave():
    """sawtooth_waveオシレーターのデバッグ"""
    print("\n🔍 sawtooth_waveオシレーターのデバッグ開始...")

    frequency = 440.0
    duration = 1.0

    try:
        signal = sawtooth_wave(frequency, duration)
        print(f"✅ ノコギリ波生成成功: {signal.num_samples} サンプル")
        print(f"   周波数: {frequency} Hz")
        print(f"   長さ: {duration} 秒")
        print(f"   最大振幅: {np.max(signal.data):.3f}")
        print(f"   最小振幅: {np.min(signal.data):.3f}")

        save_audio("debug_sawtooth_440hz.wav", signal)
        print("✅ ファイル保存成功: debug_sawtooth_440hz.wav")

        return signal

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None


def debug_square_wave():
    """square_waveオシレーターのデバッグ"""
    print("\n🔍 square_waveオシレーターのデバッグ開始...")

    frequency = 440.0
    duration = 1.0

    try:
        signal = square_wave(frequency, duration)
        print(f"✅ 矩形波生成成功: {signal.num_samples} サンプル")
        print(f"   周波数: {frequency} Hz")
        print(f"   長さ: {duration} 秒")
        print(f"   最大振幅: {np.max(signal.data):.3f}")
        print(f"   最小振幅: {np.min(signal.data):.3f}")

        save_audio("debug_square_440hz.wav", signal)
        print("✅ ファイル保存成功: debug_square_440hz.wav")

        return signal

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None


def compare_waveforms():
    """波形の比較表示"""
    print("\n📊 波形の比較表示...")

    frequency = 440.0
    duration = 0.01  # 表示用に短く

    try:
        sine_signal = sine_wave(frequency, duration)
        saw_signal = sawtooth_wave(frequency, duration)
        square_signal = square_wave(frequency, duration)

        time_array = np.linspace(0, duration, sine_signal.num_samples)

        plt.figure(figsize=(15, 10))

        plt.subplot(3, 1, 1)
        plt.plot(time_array, sine_signal.data, "b-", linewidth=2)
        plt.title("サイン波 (Sine Wave)", fontsize=14)
        plt.ylabel("振幅")
        plt.grid(True, alpha=0.3)

        plt.subplot(3, 1, 2)
        plt.plot(time_array, saw_signal.data, "r-", linewidth=2)
        plt.title("ノコギリ波 (Sawtooth Wave)", fontsize=14)
        plt.ylabel("振幅")
        plt.grid(True, alpha=0.3)

        plt.subplot(3, 1, 3)
        plt.plot(time_array, square_signal.data, "g-", linewidth=2)
        plt.title("矩形波 (Square Wave)", fontsize=14)
        plt.ylabel("振幅")
        plt.xlabel("時間 (秒)")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("debug_waveforms_comparison.png", dpi=150, bbox_inches="tight")
        plt.show()

        print("✅ 波形比較グラフを保存しました: debug_waveforms_comparison.png")

    except Exception as e:
        print(f"❌ 波形比較エラー: {e}")


if __name__ == "__main__":
    print("🔧 オシレーターデバッグスクリプト実行中...")
    print("=" * 50)

    # 各オシレーターをテスト
    sine_signal = debug_sine_wave()
    saw_signal = debug_sawtooth_wave()
    square_signal = debug_square_wave()

    # 波形比較
    if sine_signal is not None and saw_signal is not None and square_signal is not None:
        compare_waveforms()

    print("\n🎉 デバッグ完了！生成されたファイルを確認してください。")
