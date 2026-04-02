# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Contributing guidelines (CONTRIBUTING.md)
- Comprehensive documentation

### Changed
- Improved README.md structure
- Enhanced code documentation

### Fixed
- Minor bug fixes in audio processing

## [1.0.0] - 2025-07-04

### Added
- **Core Audio Library**
  - Basic oscillators (SineWave, SquareWave, SawtoothWave, TriangleWave)
  - ADSR envelope generation
  - Audio file I/O (WAV format)
  - Basic audio configuration management

- **Synthesis Module**
  - Note utilities with MIDI note conversion
  - Frequency calculation functions
  - Envelope generators (ADSR, exponential decay)

- **Effects Module**
  - Basic filters (lowpass, highpass, bandpass)
  - Audio effects (reverb, distortion, chorus)
  - Dynamic range processing

- **Instruments Module**
  - Basic instrument classes (Piano, Guitar, Drum)
  - Polyphonic note handling
  - Velocity sensitivity

- **Sequencer**
  - Multi-track sequencing
  - MIDI-like note scheduling
  - Basic mixing capabilities

- **Educational Content**
  - 7 comprehensive Jupyter notebook lessons
  - Progressive learning curriculum from basics to advanced topics
  - Practical examples and exercises

- **Examples and Tutorials**
  - Basic usage examples
  - Educational tutorial scripts
  - Audio synthesis demonstrations

### Technical Features
- Type hints throughout the codebase
- Comprehensive Japanese documentation
- Educational-focused code structure
- NumPy-based efficient audio processing
- SciPy integration for advanced DSP

### Educational Philosophy
- "Understandable Black Box" elimination
- Direct mapping between theory and implementation
- Progressive complexity for natural learning curve
- Source code as educational material

---

## Development Notes

### Version 1.0.0 Highlights
音響プログラミング初心者のための教育的Pythonライブラリの初回リリースです。

**主な特徴：**
- 教育性を重視したライブラリ設計
- 理解しやすいコード構造
- 段階的学習が可能な設計
- 理論と実装の直接的な対応

**対象ユーザー：**
- 音響プログラミング初心者
- デジタル信号処理を学ぶ学生
- 音楽制作に興味のあるプログラマー

### Future Roadmap
- [ ] Real-time audio processing capabilities
- [ ] Advanced synthesis methods (FM, AM, granular)
- [ ] Machine learning integration for audio analysis
- [ ] Web-based interactive tutorials
- [ ] MIDI file import/export
- [ ] Advanced filter designs (IIR, FIR)
- [ ] Spectral analysis tools
