# Google Colab セットアップガイド

## 各レッスンのアクセスURL

各ノートブックは以下のURLで直接Google Colabで開けます。

| レッスン | URL |
|---------|-----|
| 01 - 基本概念とサイン波 | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_01_basics_and_sine_waves.ipynb` |
| 02 - エンベロープとADSR | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_02_envelopes_and_adsr.ipynb` |
| 03 - 周波数分析 | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_03_frequency_analysis.ipynb` |
| 04 - フィルターと音色デザイン | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_04_filters_and_sound_design.ipynb` |
| 05 - オーディオエフェクト | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_05_audio_effects_and_dynamics.ipynb` |
| 06 - MIDIとシーケンサー | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_06_midi_and_sequencer.ipynb` |
| 07 - 最終プロジェクト | `https://colab.research.google.com/github/ggszk/simple-sound-programming/blob/main/colab_lessons/lesson_07_final_project_and_performance.ipynb` |

**URL構造:** `https://colab.research.google.com/github/{user}/{repo}/blob/{branch}/{path}`

## 学生向け - 使用手順

### 1. ノートブックを開く

提供されたURLをクリックすると、Colabが自動で開きます。

### 2. 自分用にコピー

`ファイル` → `ドライブにコピーを保存` で自分のGoogleドライブに保存します。

### 3. セットアップセルを実行

各ノートブックの最初のコードセルがセットアップです。Colab環境を自動判定し、必要なライブラリのインストールとリポジトリのクローンを行います。

```python
# 各ノートブック共通のセットアップセル（自動実行）
import sys
try:
    import google.colab
    !pip install -q japanize-matplotlib
    !git clone -q https://github.com/ggszk/simple-sound-programming.git
    sys.path.append('/content/simple-sound-programming')
except ImportError:
    sys.path.append('..')

from audio_lib.notebook import setup_environment
setup_environment()
```

> **注意:** Lesson 05 では追加で `pedalboard` パッケージもインストールされます。

### 4. セルを順番に実行

`Shift + Enter` でセルを実行します。エラーが出たら前のセルから確認してください。

## アシスタント向け - チェック手順

ノートブックの事前チェックには [ASSISTANT_CHECKLIST.md](ASSISTANT_CHECKLIST.md) を使用してください。

基本的な流れ：

1. 上記URLでノートブックを開く
2. `ファイル` → `ドライブにコピーを保存` で自分のドライブにコピー
3. チェックリストに沿って確認
4. フィードバックをまとめて報告

## 授業での運用

### 授業開始時
1. QRコードまたはURLを提示
2. 学生が各自でColabを開く
3. 「ドライブにコピー」を確認

### 授業中
1. アシスタントが巡回サポート
2. 共通エラーを前で解説
3. 進度確認とペース調整

### 授業後
1. 学生の作成ファイルを確認
2. 次回の準備案内
3. アシスタントからのフィードバック収集
