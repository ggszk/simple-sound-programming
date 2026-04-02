"""
音楽シーケンサー

複数の楽器と音符を組み合わせて楽曲を作成。
シーケンサーはトラック・ノートの管理状態を持つためオブジェクトとして設計。
"""

import numpy as np
from .core.audio_signal import AudioSignal
from .synthesis.note_utils import note_name_to_number


class Note:
    """音符を表すクラス"""

    def __init__(self, note_number: int | str = 60, velocity: int = 100, start_time: float = 0.0, duration: float = 1.0):
        """
        Args:
            note_number: MIDIノート番号または音名
            velocity: ベロシティ (0-127)
            start_time: 開始時間 (秒)
            duration: 音符の長さ (秒)
        """
        if isinstance(note_number, str):
            self.note_number = note_name_to_number(note_number)
        else:
            self.note_number = note_number

        self.velocity = velocity
        self.start_time = start_time
        self.duration = duration

    def get_frequency(self) -> float:
        """ノートの周波数を取得"""
        from .synthesis.note_utils import note_to_frequency
        return note_to_frequency(self.note_number)

    def __repr__(self) -> str:
        return f"Note(note={self.note_number}, vel={self.velocity}, start={self.start_time}, dur={self.duration})"


class Track:
    """楽器トラッククラス"""

    def __init__(self, name: str = "Track", instrument=None):
        """
        Args:
            name: トラック名
            instrument: 楽器インスタンス（後で設定可能）
        """
        self.name = name
        self.instrument = instrument
        self.notes: list[Note] = []
        self.volume = 1.0
        self.pan = 0.0  # -1.0 (左) to 1.0 (右)

    def add_note(self, note_number: int | str, velocity: int = 100, start_time: float = 0.0, duration: float = 1.0) -> Note:
        """音符を追加"""
        note = Note(note_number, velocity, start_time, duration)
        self.notes.append(note)
        return note

    def add_note_instance(self, note: Note) -> Note:
        """Noteインスタンスを直接追加"""
        self.notes.append(note)
        return note

    def add_notes(self, note_sequence: list) -> None:
        """複数の音符を一度に追加

        Args:
            note_sequence: 音符のリスト [(note, velocity, start, duration), ...]
        """
        for note_data in note_sequence:
            if len(note_data) == 4:
                self.add_note(*note_data)
            elif len(note_data) == 3:
                note, start, duration = note_data
                self.add_note(note, 100, start, duration)
            elif len(note_data) == 2:
                note, duration = note_data
                start_time = max([n.start_time + n.duration for n in self.notes] + [0])
                self.add_note(note, 100, start_time, duration)

    def clear(self) -> None:
        """全ての音符をクリア"""
        self.notes = []

    def get_total_duration(self) -> float:
        """トラックの総演奏時間を取得"""
        if not self.notes:
            return 0.0
        return max(note.start_time + note.duration for note in self.notes)

    def render(self, total_duration: float | None = None, sample_rate: int = 44100) -> AudioSignal:
        """トラックを音声データとしてレンダリング

        Args:
            total_duration: 総時間。Noneの場合は自動計算
            sample_rate: サンプリングレート (Hz)

        Returns:
            AudioSignal: レンダリングされた音声データ
        """
        if total_duration is None:
            total_duration = self.get_total_duration()

        if total_duration <= 0:
            return AudioSignal(np.array([]), sample_rate)

        total_samples = int(sample_rate * total_duration)
        output = np.zeros(total_samples)

        for note in self.notes:
            note_audio = self.instrument.play_note(note.note_number, note.velocity, note.duration)
            start_sample = int(sample_rate * note.start_time)
            end_sample = start_sample + note_audio.num_samples

            if start_sample < total_samples:
                actual_end = min(end_sample, total_samples)
                audio_end = actual_end - start_sample
                output[start_sample:actual_end] += note_audio.data[:audio_end] * self.volume

        return AudioSignal(output, sample_rate)

    def set_instrument(self, instrument) -> None:
        """楽器を設定"""
        self.instrument = instrument


class Sequencer:
    """音楽シーケンサー"""

    def __init__(self, sample_rate: int = 44100):
        """
        Args:
            sample_rate: サンプリングレート (Hz)
        """
        self.sample_rate = sample_rate
        self.tracks: dict[str, Track] = {}
        self.tempo = 120  # BPM
        self.master_volume = 1.0

    def add_track(self, track: Track) -> None:
        """トラックを追加"""
        self.tracks[track.name] = track

    def set_instrument(self, track_name: str, instrument) -> None:
        """指定されたトラックに楽器を設定"""
        if track_name in self.tracks:
            self.tracks[track_name].set_instrument(instrument)
        else:
            raise ValueError(f"トラック '{track_name}' が見つかりません")

    def remove_track(self, track_name: str) -> None:
        """トラックを削除"""
        if track_name in self.tracks:
            del self.tracks[track_name]

    def clear_all_tracks(self) -> None:
        """全てのトラックをクリア"""
        self.tracks = {}

    def get_total_duration(self) -> float:
        """全トラックの総演奏時間を取得"""
        if not self.tracks:
            return 0.0
        return max(track.get_total_duration() for track in self.tracks.values())

    def render(self, duration: float | None = None) -> AudioSignal:
        """全トラックをレンダリングしてミックス

        Args:
            duration: レンダリング時間（秒）。Noneの場合は自動計算

        Returns:
            AudioSignal: ミックスされた音声データ
        """
        total_duration = duration or self.get_total_duration()

        if total_duration <= 0:
            return AudioSignal(np.array([]), self.sample_rate)

        # 各トラックをレンダリング
        track_signals: list[AudioSignal] = []
        for track in self.tracks.values():
            if track.instrument is not None:
                audio = track.render(total_duration, self.sample_rate)
                track_signals.append(audio)

        # 全トラックをミックス
        if track_signals:
            mixed = track_signals[0]
            for sig in track_signals[1:]:
                mixed = mixed + sig
        else:
            mixed = AudioSignal(np.zeros(int(self.sample_rate * total_duration)), self.sample_rate)

        # マスターボリューム
        mixed = mixed * self.master_volume

        # クリッピング防止
        max_val = np.max(np.abs(mixed.data))
        if max_val > 0:
            mixed = mixed * (0.95 / max_val)

        return mixed

    def beats_to_seconds(self, beats: float) -> float:
        """拍数を秒数に変換"""
        return beats * 60.0 / self.tempo

    def seconds_to_beats(self, seconds: float) -> float:
        """秒数を拍数に変換"""
        return seconds * self.tempo / 60.0


def create_simple_melody(track: Track, notes: list, note_duration: float = 0.5, start_time: float = 0.0) -> None:
    """シンプルなメロディーをトラックに追加するヘルパー関数"""
    current_time = start_time
    for note in notes:
        if note is not None:  # Noneは休符
            track.add_note(note, 100, current_time, note_duration)
        current_time += note_duration


def create_chord(track: Track, chord_notes: list, start_time: float = 0.0, duration: float = 1.0, velocity: int = 100) -> None:
    """和音をトラックに追加するヘルパー関数"""
    for note in chord_notes:
        track.add_note(note, velocity, start_time, duration)
