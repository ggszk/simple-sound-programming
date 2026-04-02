# Google Colab 連携ガイド
# 基礎ゼミ用 - 4年生アシスタント & 1年生向け

## 🚀 GitHub → Colab 直接連携（推奨）

### **方法1: 直接URLアクセス（最もシンプル）**

各ノートブックは以下のURLで直接Colabで開けます：

```
https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_01_basics_and_sine_waves.ipynb
```

**URL構造:**
```
https://colab.research.google.com/github/{username}/{repo}/blob/{branch}/{path}
```

### **各レッスンの直接アクセスURL:**

1. **Lesson 01 - 基礎とサイン波**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_01_basics_and_sine_waves.ipynb
   ```

2. **Lesson 02 - エンベロープとADSR**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_02_envelopes_and_adsr.ipynb
   ```

3. **Lesson 03 - フィルターと音響設計**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_03_filters_and_sound_design.ipynb
   ```

4. **Lesson 04 - オーディオエフェクトと動力学**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_04_audio_effects_and_dynamics.ipynb
   ```

5. **Lesson 05 - MIDI とシーケンサー**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_05_midi_and_sequencer.ipynb
   ```

6. **Lesson 06 - サンプリングと分析**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_06_sampling_and_analysis.ipynb
   ```

7. **Lesson 07 - 最終プロジェクトとパフォーマンス**
   ```
   https://colab.research.google.com/github/ggszk/simple-audio-programming/blob/main/colab_lessons/lesson_07_final_project_and_performance.ipynb
   ```

## 🎯 4年生アシスタント用 - チェック手順

### **Step 1: 事前チェック用コピー作成**

1. **上記URLでノートブックを開く**
2. **「ドライブにコピー」をクリック**
3. **自分のGoogleドライブに保存**
4. **チェック後、コメント・修正案をまとめる**

### **Step 2: チェック項目**

#### **技術的チェック**
- [ ] セル実行がエラーなく完了するか
- [ ] 音声出力が正常に再生されるか
- [ ] インストール手順が正しく動作するか
- [ ] 実行時間が適切か（1セルあたり3分以内）

#### **難易度チェック（1年生基準）**
- [ ] 説明が理解しやすいか
- [ ] コード例が適切な複雑さか
- [ ] 段階的な学習になっているか
- [ ] 専門用語の説明が十分か

#### **教育的チェック**
- [ ] 学習目標が明確か
- [ ] 実践的な演習があるか
- [ ] 理論と実装の対応が分かりやすいか
- [ ] 次のレッスンへの橋渡しが適切か

## 🎓 1年生向け - 使用手順

### **基本的な使い方**

1. **ノートブックを開く**
   - 提供されたURLをクリック
   - Colabが自動で開きます

2. **自分用にコピー**
   - `ファイル` → `ドライブにコピーを保存`
   - 自分のGoogleドライブに保存されます

3. **実行前の準備**
   ```python
   # 最初のセルで必ずライブラリをインストール
   !pip install numpy scipy matplotlib
   
   # GitHubからライブラリをクローン
   !git clone https://github.com/ggszk/simple-audio-programming.git
   import sys
   sys.path.append('/content/simple-audio-programming')
   ```

4. **セルを順番に実行**
   - `Shift + Enter` でセル実行
   - エラーが出たら前のセルから確認

## 📋 管理面でのメリット

### **教員にとって**
- ✅ 常に最新版を学生に提供
- ✅ GitHub で版管理・更新が簡単
- ✅ 学生の進捗確認が容易
- ✅ アシスタントとの協力体制構築

### **アシスタントにとって**
- ✅ 簡単にアクセス・テスト可能
- ✅ 自分のドライブでメモ・修正案作成
- ✅ 元ファイルを汚さずチェック可能
- ✅ Issue でフィードバック提供

### **学生にとって**
- ✅ 複雑なセットアップ不要
- ✅ 常に動作する環境
- ✅ 自分のペースで学習可能
- ✅ 保存・共有が簡単

## 🔧 追加設定（オプション）

### **GitHub Pages でランディングページ作成**

学生向けに見やすいページを作成：

1. **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main
4. **各レッスンへの直接Colabリンクを配置**

### **QRコード生成**

各レッスンのColabリンクのQRコードを生成して、授業中に簡単アクセス。

## 📱 実際の授業での運用例

### **授業開始時**
1. **QRコードまたはURLを提示**
2. **学生が各自でColab開く**
3. **「ドライブにコピー」を確認**

### **授業中**
1. **アシスタントが巡回サポート**
2. **共通エラーを前で解説**
3. **進度確認とペース調整**

### **授業後**
1. **学生の作成ファイルを確認**
2. **次回の準備案内**
3. **アシスタントからのフィードバック収集**

---

この方法なら、**ファイル管理が最小限**で**常に最新版を提供**でき、**アシスタントとの協力**も効率的です！
