"""
WAVファイルの読み書きを行うクラス

元のコードの複雑な変換処理を整理し、理解しやすい形に改善
"""

import numpy as np
from scipy.io import wavfile
from .audio_config import AudioConfig

class WaveFileIO:
    """WAVファイルの入出力を担当するクラス"""
    
    @staticmethod
    def load_mono(filename, config=None):
        """
        モノラルWAVファイルを読み込む
        
        Args:
            filename (str): ファイル名
            config (AudioConfig): オーディオ設定
            
        Returns:
            tuple: (サンプリング周波数, 音声データ配列)
        """
        if config is None:
            config = AudioConfig()
            
        file_sample_rate, audio_data = wavfile.read(filename)
        
        # データ型を浮動小数点に変換
        audio_data = audio_data.astype(np.float64)
        
        # 16bitの場合の正規化 (-1.0 to 1.0)
        if audio_data.dtype == np.int16 or np.max(np.abs(audio_data)) > 1.0:
            audio_data = audio_data / 32768.0

        # configのサンプリング周波数を更新
        updated_config = AudioConfig(
            sample_rate=file_sample_rate
        )
    
        return updated_config, audio_data
    
    @staticmethod
    def save_mono(filename, audio_data, config=None):
        """
        モノラル音声データをWAVファイルに保存
        
        Args:
            filename (str): 保存ファイル名
            audio_data (np.ndarray): 音声データ (-1.0 to 1.0)
            config (AudioConfig): オーディオ設定
        """
        if config is None:
            config = AudioConfig()
                
        # クリッピング防止
        audio_data = np.clip(audio_data, -config.max_amplitude, config.max_amplitude)
        
        # 16bit整数に変換
        audio_data_16bit = (audio_data * 32767).astype(np.int16)
        
        # ファイルに保存
        wavfile.write(filename, config.sample_rate, audio_data_16bit)
    
    @staticmethod
    def load_stereo(filename, config=None):
        """
        ステレオWAVファイルを読み込む
        
        Args:
            filename (str): ファイル名
            config (AudioConfig): オーディオ設定
            
        Returns:
            tuple: (サンプリング周波数, 音声データ配列[左, 右])
        """
        if config is None:
            config = AudioConfig()
            
        file_sample_rate, audio_data = wavfile.read(filename)
        
        # データ型を浮動小数点に変換
        audio_data = audio_data.astype(np.float64)
        
        # 16bitの場合の正規化
        if np.max(np.abs(audio_data)) > 1.0:
            audio_data = audio_data / 32768.0

        # configのサンプリング周波数を更新
        updated_config = AudioConfig(
            sample_rate=file_sample_rate
        )
    
        return updated_config, audio_data
    
    @staticmethod
    def save_stereo(filename, audio_data, config=None):
        """
        ステレオ音声データをWAVファイルに保存
        
        Args:
            filename (str): 保存ファイル名
            audio_data (np.ndarray): 音声データ [N x 2] (-1.0 to 1.0)
            config (AudioConfig): オーディオ設定
        """
        if config is None:
            config = AudioConfig()
        
        # クリッピング防止
        audio_data = np.clip(audio_data, -config.max_amplitude, config.max_amplitude)
        
        # 16bit整数に変換
        audio_data_16bit = (audio_data * 32767).astype(np.int16)
        
        # ファイルに保存
        wavfile.write(filename, config.sample_rate, audio_data_16bit)


# 便利な関数エイリアス（後方互換性のため）
def save_wav(filename, audio_data, config=None):
    """簡単なWAVファイル保存関数"""
    WaveFileIO.save_mono(filename, audio_data, config)

def read_wav(filename, config=None):
    """簡単なWAVファイル読み込み関数"""
    return WaveFileIO.load_mono(filename, config)
