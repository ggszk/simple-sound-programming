"""
音のプログラミング - 基本的な使用例

リファクタリングされたライブラリの使い方を示すサンプルコード
"""

import numpy as np
from audio_lib import (
    AudioSignal,
    sine_wave,
    adsr,
    linear_envelope,
    save_audio,
    note_to_frequency,
    note_name_to_number,
    Piano,
    Guitar,
    Drum,
    Sequencer,
    Track,
)


def example_01_basic_sine_wave():
    """例1: 基本的なサイン波の生成"""
    print("例1: 基本的なサイン波を生成中...")

    # 1秒間の440Hz（ラ音）を生成
    frequency = 440.0
    duration = 1.0
    signal = sine_wave(frequency, duration)

    # フェードイン・フェードアウトを追加（クリック音の防止）
    envelope = linear_envelope(duration, fade_in=0.01, fade_out=0.01)
    signal = signal * envelope

    # ファイルに保存
    save_audio("example_01_sine_wave.wav", signal)
    print("→ example_01_sine_wave.wav を保存しました")


def example_02_adsr_envelope():
    """例2: ADSRエンベロープの使用"""
    print("例2: ADSRエンベロープ付きの音を生成中...")

    # 音を生成
    frequency = note_to_frequency(60)  # 中央のC
    duration = 2.0
    signal = sine_wave(frequency, duration)

    # ADSRエンベロープを適用
    envelope = adsr(
        duration,
        attack=0.1,  # アタック: 0.1秒
        decay=0.2,  # ディケイ: 0.2秒
        sustain=0.7,  # サステイン: 70%
        release=0.5,  # リリース: 0.5秒
    )
    signal = signal * envelope

    save_audio("example_02_adsr.wav", signal)
    print("→ example_02_adsr.wav を保存しました")


def example_03_musical_notes():
    """例3: 音名を使った音の生成"""
    print("例3: 音名を使ったスケール演奏中...")

    # Cメジャースケール
    notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    note_duration = 0.5

    # 各音符を連続で生成
    all_audio = []
    for note_name in notes:
        note_number = note_name_to_number(note_name)
        frequency = note_to_frequency(note_number)

        # 音を生成
        signal = sine_wave(frequency, note_duration)
        envelope = adsr(note_duration, attack=0.05, decay=0.1, sustain=0.7, release=0.2)
        signal = signal * envelope

        all_audio.append(signal)

    # 全ての音をつなげる
    full_scale = AudioSignal(np.concatenate([s.data for s in all_audio]))

    save_audio("example_03_scale.wav", full_scale)
    print("→ example_03_scale.wav を保存しました")


def example_04_piano_instrument():
    """例4: ピアノ楽器クラスの使用"""
    print("例4: ピアノの音色でメロディー演奏中...")

    piano = Piano()

    # 簡単なメロディー (童謡「きらきら星」の一部)
    melody = [
        ("C4", 0.5),
        ("C4", 0.5),
        ("G4", 0.5),
        ("G4", 0.5),
        ("A4", 0.5),
        ("A4", 0.5),
        ("G4", 1.0),
        ("F4", 0.5),
        ("F4", 0.5),
        ("E4", 0.5),
        ("E4", 0.5),
        ("D4", 0.5),
        ("D4", 0.5),
        ("C4", 1.0),
    ]

    # メロディーを演奏
    all_audio = []
    for note_name, duration in melody:
        note_number = note_name_to_number(note_name)
        signal = piano.play_note(note_number, velocity=100, duration=duration)
        all_audio.append(signal)

    # 全てをつなげる
    full_melody = AudioSignal(np.concatenate([s.data for s in all_audio]))

    save_audio("example_04_piano_melody.wav", full_melody)
    print("→ example_04_piano_melody.wav を保存しました")


def example_05_sequencer_demo():
    """例5: シーケンサーを使った楽曲制作"""
    print("例5: シーケンサーで複数パートの楽曲制作中...")

    sequencer = Sequencer()
    sequencer.tempo = 120  # BPM

    # 楽器を準備
    piano = Piano()
    guitar = Guitar()
    drum = Drum()

    # トラックを作成して追加
    piano_track = Track("Piano", piano)
    guitar_track = Track("Guitar", guitar)
    kick_track = Track("Kick", drum)
    snare_track = Track("Snare", drum)
    sequencer.add_track(piano_track)
    sequencer.add_track(guitar_track)
    sequencer.add_track(kick_track)
    sequencer.add_track(snare_track)

    # ピアノのコード進行
    chord_duration = 2.0
    chords = [
        ["C4", "E4", "G4"],  # Cメジャー
        ["F4", "A4", "C5"],  # Fメジャー
        ["G4", "B4", "D5"],  # Gメジャー
        ["C4", "E4", "G4"],  # Cメジャー
    ]

    for i, chord in enumerate(chords):
        start_time = i * chord_duration
        _create_chord(piano_track, chord, start_time, chord_duration, velocity=80)

    # ギターのメロディー
    guitar_melody = [
        ("E5", 0.5),
        ("D5", 0.5),
        ("C5", 0.5),
        ("D5", 0.5),
        ("E5", 0.5),
        ("F5", 0.5),
        ("G5", 1.0),
        ("G5", 0.5),
        ("F5", 0.5),
        ("E5", 0.5),
        ("D5", 0.5),
        ("C5", 2.0),
    ]

    current_time = 0.0
    for note_name, duration in guitar_melody:
        note_number = note_name_to_number(note_name)
        guitar_track.add_note(note_number, 90, current_time, duration)
        current_time += duration

    # ドラムパターン
    beat_duration = 0.5
    total_beats = 16

    # キックドラム (4つ打ち)
    for beat in range(0, total_beats, 2):
        kick_track.add_note(36, 120, beat * beat_duration, beat_duration)

    # スネアドラム (2拍目、4拍目)
    for beat in range(1, total_beats, 2):
        snare_track.add_note(38, 100, beat * beat_duration, beat_duration)

    # レンダリングして保存
    sequencer.master_volume = 0.8
    result = sequencer.render()
    save_audio("example_05_sequencer_demo.wav", result)
    print("→ example_05_sequencer_demo.wav を保存しました")


def _create_chord(track, chord_notes, start_time, duration, velocity=100):
    """
    トラックに和音を追加するヘルパー関数

    Args:
        track: シーケンサーのトラック
        chord_notes: 音名のリスト（例: ['C4', 'E4', 'G4']）
        start_time: 開始時間（秒）
        duration: 音の長さ（秒）
        velocity: 音の強さ（0-127）
    """
    for note_name in chord_notes:
        note_number = note_name_to_number(note_name)
        track.add_note(note_number, velocity, start_time, duration)


def main():
    """全ての例を実行"""
    print("音のプログラミング - リファクタリング版デモ")
    print("=" * 50)

    try:
        example_01_basic_sine_wave()
        example_02_adsr_envelope()
        example_03_musical_notes()
        example_04_piano_instrument()
        example_05_sequencer_demo()

        print("\n全ての例が正常に完了しました！")
        print("生成されたWAVファイルを再生して確認してください。")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
