# PAWS PARTNERS Expert Version 1.0.1

**新作50面の高難易度版 / 50 new expert puzzles**

ネコとウサギをそれぞれの家へ導く、時間制限のない協力パズルです。共有する床の状態、仕事を分担する順序、箱や足場を残す・使う時機を考えます。ノーマル版とは独立した50面とパスワードを収録しています。難易度は人による試遊前の暫定評価です。

Guide the cat and rabbit to their own homes. Plan shared floor states, divide duties, and decide when to preserve or consume resources. There is no time limit. This edition contains 50 new stages and separate passwords. Difficulty is provisional pending human playtesting.

## Download / ダウンロード

- [ROM: PAWS-PARTNERS-EXPERT-MSX2.rom](rom/PAWS-PARTNERS-EXPERT-MSX2.rom) — 1 MiB, ASCII8
- [日本語マニュアル](docs/MANUAL-ja.md) / [English manual](docs/MANUAL-en.md)
- [日本語ヒントブック](docs/TECHNIQUE-GUIDE-ja.md) / [English hint book](docs/TECHNIQUE-GUIDE-en.md)
- [仕様 / Specifications](SPECIFICATIONS.md)
- [ライセンス / License](LICENSE) · [制作・音楽の表記 / Credits](CREDITS.md) · [免責 / Disclaimer](DISCLAIMER.md)
- [ROM SHA-256](SHA256SUMS.txt)

マニュアルには実際のチップ画像、状態変化、チップに重なる小さな表示の説明があります。ヒントブックは考え方とテクニックを扱い、全解答やパスワード一覧は掲載していません。HTML版・テキスト版もdocsフォルダーに同梱しています。HTML版は画像フォルダーと一緒にダウンロードして開いてください。

The illustrated manuals explain tiles, state changes and small mechanism badges. The hint books discuss techniques rather than listing solutions or passwords. Offline HTML and text editions are included in docs; keep the images folder with the HTML files.

## Offline PDF / 手元で読むPDF

画像入りのPDFです。ダウンロード後はネット接続や別の画像フォルダーなしで読めます。A4で印刷できます。

Self-contained PDFs for offline reading and A4 printing; no separate image files are required.

- [日本語マニュアル / Manual (Japanese)](docs/MANUAL-ja.pdf)
- [English manual](docs/MANUAL-en.pdf)
- [日本語ヒントブック / Hints (Japanese)](docs/TECHNIQUE-GUIDE-ja.pdf)
- [English hint book](docs/TECHNIQUE-GUIDE-en.pdf)
- [4冊まとめてダウンロード / Download all four PDFs](docs/PAWS-PARTNERS-EXPERT-PDF-GUIDES.zip)

## Requirements / 動作条件

MSX2以降、RAM 64KiB・VRAM 64KiB以上、キーボード、1MiB ASCII8 ROM対応環境。TurboRでもZ80モードで動作します。拡張VDPは不要です。512KiB専用カートリッジには収まりません。

MSX2 or later, 64 KiB RAM and 64 KiB VRAM, keyboard, and support for 1 MiB ASCII8 ROMs. TurboR uses Z80 mode. No enhanced VDP is needed. A 512 KiB-only cartridge is insufficient.

## Quick start / 操作

- タイトルでパスワードを空欄にしてEnter / Leave the password blank and press Enter to start.
- 左右で配置場所、Spaceでチップ、Enterで実行 / Left/right selects a slot; Space cycles chips; Enter starts.
- F5で全体表示・通常表示を切替。全体表示でも配置・実行できます / F5 toggles overview, including editing and live simulation.
- 実行中Enterで停止・再開、Escで配置へ戻る / Enter pauses/resumes; Esc cancels back to planning.
- F1でヘルプと現在のパスワード、F2でパスワード入力 / F1 shows help and the current password; F2 opens password entry.

## Version 1.0.1 / 更新内容

F5の縮小画面でチップを設定してEnterを押すと、縮小画面のまま実行を開始します。通常画面から開始した場合も、その表示を維持します。ステージとパスワードの変更はありません。

Pressing Enter after editing in the F5 overview now starts the simulation in that same view. Starting from the normal view also preserves that view. Stages and passwords are unchanged.

今回の修正はopenMSXのMSX2・TurboR両設定で、各24項目と144タイルの描画を確認しました。配置保持、両表示からの開始、一時停止・再開、取消、クリアを含みます。

This change passed 24 checks and 144 tile comparisons on each of the MSX2 and TurboR profiles in openMSX, covering retained placements, starting in either view, pause/resume, cancellation and clearing a stage.

## Verification / 検証

openMSXのC-BIOS_MSX2_EUおよびPanasonic_FS-A1ST設定で検証しました。実機では未検証です。全50面・登録別解・面遷移・盤面展開を確認し、最終の文字表示修正と展開高速化には追加検証を実施しました。高速化後も両設定の250画面ずつが期待するVRAMデータと一致し、F5操作、画面保持、取消・復元・再クリアを確認しています。

Tested with the C-BIOS_MSX2_EU and Panasonic_FS-A1ST profiles in openMSX; physical hardware is not yet verified. Tests cover all 50 stages, registered alternative solutions, stage transitions and board decoding. Targeted tests cover the final text fix and decoder optimization, including exact VRAM data for 250 pages per profile, overview controls, retained camera images, cancellation, restoration and replay.

## Music / 音楽

Expert専用BGM: **8-bit Puzzle Fun - EXPERT PSG**。制作ワークフロー: **Suno (Premium) → PSG変換 → AI music editor**。クリア音: **Moonlit Gem - Clear Jingle B**。提供パッケージのライセンス表記を保持しています。

Expert BGM: **8-bit Puzzle Fun - EXPERT PSG**, created through **Suno (Premium) → PSG conversion → AI music editor**. Clear phrase: **Moonlit Gem - Clear Jingle B**. Supplied license notices are retained.

[ノーマル版へ / Back to Normal edition](../README.md)
