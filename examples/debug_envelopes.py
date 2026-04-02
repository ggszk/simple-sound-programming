#!/usr/bin/env python3
"""
デバッグ用: エンベロープのテスト

adsr, linear_envelopeの動作確認とデバッグ
"""

import numpy as np
import matplotlib.pyplot as plt
from audio_lib import sine_wave, adsr, linear_envelope, save_audio


def debug_adsr_envelope():
    """ADSRエンベロープのデバッグ"""
    print("🔍 ADSRエンベロープのデバッグ開始...")

    # エンベロープパラメータ
    attack_time = 0.1
    decay_time = 0.2
    sustain_level = 0.7
    release_time = 0.5

    try:
        duration = 2.0
        envelope_signal = adsr(
            duration,
            attack=attack_time,
            decay=decay_time,
            sustain=sustain_level,
            release=release_time,
        )

        print("✅ ADSRエンベロープ生成成功")
        print(f"   Attack: {attack_time}s")
        print(f"   Decay: {decay_time}s")
        print(f"   Sustain: {sustain_level}")
        print(f"   Release: {release_time}s")
        print(f"   総時間: {duration}s")
        print(f"   サンプル数: {envelope_signal.num_samples}")

        return envelope_signal

    except Exception as e:
        print(f"❌ ADSRエンベロープエラー: {e}")
        return None


def debug_linear_envelope():
    """Linearエンベロープのデバッグ"""
    print("\n🔍 Linearエンベロープのデバッグ開始...")

    try:
        duration = 2.0
        envelope_signal = linear_envelope(duration, fade_in=0.5, fade_out=0.5)

        print("✅ Linearエンベロープ生成成功")
        print("   fade_in: 0.5s, fade_out: 0.5s")
        print(f"   総時間: {duration}s")
        print(f"   サンプル数: {envelope_signal.num_samples}")

        return envelope_signal

    except Exception as e:
        print(f"❌ Linearエンベロープエラー: {e}")
        return None


def debug_envelope_application():
    """エンベロープ適用のデバッグ"""
    print("\n🔍 エンベロープ適用のデバッグ開始...")

    frequency = 440.0
    duration = 2.0

    try:
        # 基本のサイン波を生成
        sine_signal = sine_wave(frequency, duration)

        # ADSRエンベロープを作成して適用
        envelope = adsr(
            duration,
            attack=0.1,
            decay=0.2,
            sustain=0.7,
            release=0.5,
        )
        enveloped_signal = sine_signal * envelope

        print("✅ エンベロープ適用成功")
        print(f"   元の信号サンプル数: {sine_signal.num_samples}")
        print(f"   エンベロープ適用後: {enveloped_signal.num_samples}")

        # ファイル保存
        save_audio("debug_sine_no_envelope.wav", sine_signal)
        save_audio("debug_sine_with_adsr.wav", enveloped_signal)

        print("✅ ファイル保存完了:")
        print("   - debug_sine_no_envelope.wav (エンベロープなし)")
        print("   - debug_sine_with_adsr.wav (ADSRエンベロープあり)")

        return sine_signal, enveloped_signal

    except Exception as e:
        print(f"❌ エンベロープ適用エラー: {e}")
        return None, None


def visualize_envelopes():
    """エンベロープの可視化"""
    print("\n📊 エンベロープの可視化...")

    duration = 2.0

    try:
        # ADSRエンベロープ
        adsr_signal = adsr(
            duration,
            attack=0.1,
            decay=0.2,
            sustain=0.7,
            release=0.5,
        )

        # Linearエンベロープ
        linear_signal = linear_envelope(duration, fade_in=0.5, fade_out=0.5)

        # 時間軸
        time_array = np.linspace(0, duration, adsr_signal.num_samples)

        plt.figure(figsize=(15, 8))

        plt.subplot(2, 1, 1)
        plt.plot(time_array, adsr_signal.data, "b-", linewidth=2)
        plt.title("ADSRエンベロープ (Attack=0.1s, Decay=0.2s, Sustain=0.7, Release=0.5s)", fontsize=14)
        plt.ylabel("レベル")
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.1, 1.1)

        plt.subplot(2, 1, 2)
        plt.plot(time_array, linear_signal.data, "r-", linewidth=2)
        plt.title("Linearエンベロープ", fontsize=14)
        plt.ylabel("レベル")
        plt.xlabel("時間 (秒)")
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.1, 1.1)

        plt.tight_layout()
        plt.savefig("debug_envelopes_comparison.png", dpi=150, bbox_inches="tight")
        plt.show()

        print("✅ エンベロープ比較グラフを保存しました: debug_envelopes_comparison.png")

    except Exception as e:
        print(f"❌ エンベロープ可視化エラー: {e}")


if __name__ == "__main__":
    print("🔧 エンベロープデバッグスクリプト実行中...")
    print("=" * 50)

    # エンベロープ単体テスト
    adsr_signal = debug_adsr_envelope()
    linear_signal = debug_linear_envelope()

    # エンベロープ適用テスト
    original, enveloped = debug_envelope_application()

    # 可視化
    if adsr_signal is not None and linear_signal is not None:
        visualize_envelopes()

    print("\n🎉 エンベロープデバッグ完了！生成されたファイルを確認してください。")
