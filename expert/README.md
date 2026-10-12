# PAWS PARTNERS Expert Version 1.0.2

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

## BlueMSX+ auto-detection / 自動判別で起動しない場合

Expert版をドラッグ＆ドロップしても起動しない場合は、次の登録ファイルをご利用ください。Expert **1.0.0 / 1.0.1 / 1.0.2**をASCII8として認識させます。

1. [paws-partners-expert-db.xml をダウンロード](https://raw.githubusercontent.com/kanon-ai/PAWS-PARTNERS/main/expert/rom/paws-partners-expert-db.xml)して保存します。
2. **実際に遊ぶPC**のBlueMSX+フォルダー内にある `Databases` へXMLをコピーします。同名の古いXMLは今回のファイルに置き換えてください。他のデータベースはそのまま残してください。
3. BlueMSX+を終了して起動し直し、ROMをドラッグ＆ドロップします。

別の方法として、カートリッジを開く際にROM種別を **ASCII8** に指定することもできます。XMLはROMの内容（SHA-1）で識別するため、ファイル名を変えても有効です。対応版以外のROMには適用されません。今後ROMを更新する場合は、対応する登録情報も必要になります。

If dragging and dropping the Expert ROM fails to start it, use this database entry for Expert **1.0.0 / 1.0.1 / 1.0.2**:

1. Download and save [paws-partners-expert-db.xml](https://raw.githubusercontent.com/kanon-ai/PAWS-PARTNERS/main/expert/rom/paws-partners-expert-db.xml).
2. Copy it into the `Databases` folder of BlueMSX+ **on the PC used to play**. Replace an older file with the same name; keep all other database files.
3. Close and restart BlueMSX+, then drag and drop the ROM.

Alternatively, select **ASCII8** as the ROM type when opening the cartridge. The entry identifies the ROM by its SHA-1, so renaming the ROM does not affect recognition. Only the listed ROM versions match; future ROM revisions need corresponding entries.

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

## Version 1.0.2 / 更新内容

F5の縮小画面でSHIFTを押しながら矢印キーを使うと、任意のマスを拡大確認できます。SHIFTを離すと元の配置カーソルへ戻ります。小窓のBASEは床・仕掛け、CHIPは配置チップと状態表示です。確認中はキャラクターを一時的に隠して進行を止め、離すと元の実行・一時停止状態に戻ります。配置内容、50面、パスワード、音楽は変更していません。

Hold SHIFT and use arrows in the F5 overview to inspect any cell. Release SHIFT to return to the original placement cursor. BASE shows the floor or mechanism; CHIP shows the placement tile and badge. Actors are temporarily hidden and progress is held while inspecting. Releasing SHIFT restores the previous running or paused state. Placements, all 50 stages, passwords and music are unchanged.

日英マニュアルに通常・縮小・状態表示の比較図を追加しました。[ROM・対応XML・日英PDFの一括ダウンロード](rom/PAWS-PARTNERS-EXPERT-1.0.2.zip)も用意しています。

The bilingual manuals now compare normal tiles, overview tiles and small badges. [Download ROM, matching XML and bilingual PDFs together](rom/PAWS-PARTNERS-EXPERT-1.0.2.zip).

今回の変更はopenMSXのMSX2・TurboR設定で拡大表示、配置保持、復帰、停止・再開を確認し、従来の実行・クリア操作と各144タイルの描画も再確認しました。この更新のBlueMSX+での実行と実機動作は未確認です。XMLのSHA-1は同梱ROMとの一致を確認しています。

This update was checked in openMSX MSX2 and TurboR profiles for inspection, retained placements, return, pause and resume. Existing run/clear controls and 144 tile comparisons per profile also passed. This update has not been runtime-tested in BlueMSX+ or on physical hardware. The XML SHA-1 matches the supplied ROM.

## Version 1.0.1 / Previous update

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
