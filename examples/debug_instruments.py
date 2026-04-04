#!/usr/bin/env python3
"""
デバッグ用: 楽器とシーケンサーのテスト

Piano, Guitar, Drum, Sequencerの動作確認とデバッグ
"""

import numpy as np
from audio_lib import (
    save_audio,
    note_name_to_number,
    note_to_frequency,
    Piano,
    Guitar,
    Drum,
    Sequencer,
    Track,
)


def debug_piano():
    """Pianoインストゥルメントのデバッグ"""
    print("🔍 Pianoインストゥルメントのデバッグ開始...")

    piano = Piano()

    try:
        # C4の音を2秒間生成
        note = "C4"
        midi_number = note_name_to_number(note)
        duration = 2.0

        signal = piano.play_note(midi_number, velocity=100, duration=duration)

        print(f"✅ Piano音生成成功: {note} (MIDI: {midi_number})")
        print(f"   長さ: {duration}秒")
        print(f"   サンプル数: {signal.num_samples}")
        print(f"   最大振幅: {np.max(np.abs(signal.data)):.3f}")

        save_audio("debug_piano_c4.wav", signal)
        print("✅ ファイル保存成功: debug_piano_c4.wav")

        return signal

    except Exception as e:
        print(f"❌ Pianoエラー: {e}")
        return None


def debug_guitar():
    """Guitarインストゥルメントのデバッグ"""
    print("\n🔍 Guitarインストゥルメントのデバッグ開始...")

    guitar = Guitar()

    try:
        # E2の音を2秒間生成（ギターの低いE弦）
        note = "E2"
        midi_number = note_name_to_number(note)
        duration = 2.0

        signal = guitar.play_note(midi_number, velocity=100, duration=duration)

        print(f"✅ Guitar音生成成功: {note} (MIDI: {midi_number})")
        print(f"   長さ: {duration}秒")
        print(f"   サンプル数: {signal.num_samples}")
        print(f"   最大振幅: {np.max(np.abs(signal.data)):.3f}")

        save_audio("debug_guitar_e2.wav", signal)
        print("✅ ファイル保存成功: debug_guitar_e2.wav")

        return signal

    except Exception as e:
        print(f"❌ Guitarエラー: {e}")
        return None


def debug_drum():
    """Drumインストゥルメントのデバッグ"""
    print("\n🔍 Drumインストゥルメントのデバッグ開始...")

    drum = Drum()

    try:
        # キック、スネア、ハイハットをテスト
        drum_sounds = {
            "kick": 36,  # MIDI番号36はキックドラム
            "snare": 38,  # MIDI番号38はスネアドラム
            "hihat": 42,  # MIDI番号42はクローズドハイハット
        }

        duration = 1.0

        for drum_name, midi_number in drum_sounds.items():
            signal = drum.play_note(midi_number, velocity=100, duration=duration)

            print(f"✅ Drum音生成成功: {drum_name} (MIDI: {midi_number})")
            print(f"   長さ: {duration}秒")
            print(f"   サンプル数: {signal.num_samples}")
            print(f"   最大振幅: {np.max(np.abs(signal.data)):.3f}")

            filename = f"debug_drum_{drum_name}.wav"
            save_audio(filename, signal)
            print(f"✅ ファイル保存成功: {filename}")

        return True

    except Exception as e:
        print(f"❌ Drumエラー: {e}")
        return False


def debug_sequencer():
    """Sequencerのデバッグ"""
    print("\n🔍 Sequencerのデバッグ開始...")

    sequencer = Sequencer()

    try:
        # 楽器を準備
        piano = Piano()
        drum = Drum()

        # トラックを作成して追加
        piano_track = Track("Piano", piano)
        drum_track = Track("Drums", drum)
        sequencer.add_track(piano_track)
        sequencer.add_track(drum_track)

        print("✅ トラックの追加成功: Piano, Drums")

        # 簡単なシーケンスを作成
        # ピアノでCメジャーコード → Fメジャーコード
        for note_name in ["C4", "E4", "G4"]:
            piano_track.add_note(note_name, 100, 0.0, 1.0)
        for note_name in ["F4", "A4", "C5"]:
            piano_track.add_note(note_name, 100, 1.0, 1.0)

        # ドラムパターン
        drum_track.add_note(36, 120, 0.0, 0.1)   # キック
        drum_track.add_note(38, 100, 0.5, 0.1)   # スネア
        drum_track.add_note(36, 120, 1.0, 0.1)   # キック
        drum_track.add_note(38, 100, 1.5, 0.1)   # スネア

        print("✅ ノートの追加成功")

        # シーケンスを再生（ミックス）
        sequence_length = 2.0
        mixed_audio = sequencer.render(sequence_length)

        print("✅ シーケンス生成成功")
        print(f"   長さ: {sequence_length}秒")
        print(f"   サンプル数: {mixed_audio.num_samples}")
        print(f"   最大振幅: {np.max(np.abs(mixed_audio.data)):.3f}")

        save_audio("debug_sequencer_demo.wav", mixed_audio)
        print("✅ ファイル保存成功: debug_sequencer_demo.wav")

        return mixed_audio

    except Exception as e:
        print(f"❌ Sequencerエラー: {e}")
        return None


def debug_note_utilities():
    """ノートユーティリティ関数のデバッグ"""
    print("\n🔍 ノートユーティリティのデバッグ開始...")

    try:
        # いくつかの音名をテスト
        test_notes = ["C4", "D#4", "F#5", "Bb3", "A4"]

        print("音名 -> MIDI番号 -> 周波数の変換テスト:")
        print("音名\tMIDI番号\t周波数(Hz)")
        print("-" * 30)

        for note in test_notes:
            midi_number = note_name_to_number(note)
            frequency = note_to_frequency(midi_number)
            print(f"{note}\t{midi_number}\t{frequency:.2f}")

        print("✅ ノートユーティリティテスト成功")
        return True

    except Exception as e:
        print(f"❌ ノートユーティリティエラー: {e}")
        return False


if __name__ == "__main__":
    print("🔧 楽器・シーケンサーデバッグスクリプト実行中...")
    print("=" * 50)

    # ノートユーティリティテスト
    debug_note_utilities()

    # 各楽器テスト
    piano_signal = debug_piano()
    guitar_signal = debug_guitar()
    drum_success = debug_drum()

    # シーケンサーテスト
    sequence_signal = debug_sequencer()

    print("\n🎉 楽器・シーケンサーデバッグ完了！生成されたファイルを確認してください。")
