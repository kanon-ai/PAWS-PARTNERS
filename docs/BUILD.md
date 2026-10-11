# Build and verification — v0.2.6

Python 3, Pillow, Pasmo and Windows fonts are required. Fonts and BIOS files are not bundled.

```powershell
python -m pip install Pillow
$env:PASMO = 'C:/path/to/pasmo.exe'
python tools/build_release.py
```

This rebuilds the checked-in 50 stages without regenerating or reordering them. The release builder checks SHA-256 fingerprints of the stage data, rule model and exhaustive-search evidence, then replays all stored solutions. For changed puzzle inputs, use `python tools/build.py` to run a fresh exhaustive search (potentially slow). Output: `outputs/PAWS-PARTNERS-MSX2.rom`.

The renderer uses Windows fonts under `C:/Windows/Fonts`. Different font versions can change the ROM. Do not rebuild a ROM while an emulator has it open. Authoring scripts are not needed for a release rebuild. Stage data and validation evidence contain solutions.

## Current ROM — v0.2.6

SHA-256: `0f696fc9fee952cf632fec5cebc0e23eaa3b5808e7565478dbf6b3409eccea85`.

The live-overview implementation passed 40,687 checks in each openMSX profile (C-BIOS_MSX2_EU and Panasonic_FS-A1ST): all 50 stages, successful and blocked routes, retry and state preservation. Recorded overview rendering was checked over 33,648 sprite frames and 22,955 terrain patches. These reports identify the tested pre-footer-fix ROM hash.

The release ROM also fixes clipped text in the overview footer. On this final ROM, both profiles passed 18 keyboard-driven checks covering overview execution, pause/resume, switching, clear and retry. All 11 label widths and eight captured footer states were checked against VRAM, including the row below the footer. Stage data, passwords and puzzle rules are unchanged. Reports retain their actual tested ROM hashes. Physical hardware is unverified.

1 MiB ASCII8. MSX2 or later, 64 KiB RAM / 64 KiB VRAM; TurboR uses Z80 mode. Physical hardware is unverified.

```powershell
python tools/check_trials.py --machine C-BIOS_MSX2_EU --overview --wrong-paths
python tools/check_map_play.py --machine C-BIOS_MSX2_EU
python tools/check_map_play.py --machine Panasonic_FS-A1ST
python tools/check_map_footer.py
python tools/check_supports.py --machine C-BIOS_MSX2_EU
python tools/check_cancel.py --machine C-BIOS_MSX2_EU
python tools/check_passwords.py --machine C-BIOS_MSX2_EU
python tools/check_music.py --machine C-BIOS_MSX2_EU
python tools/verify_music_trace.py --machine C-BIOS_MSX2_EU
```

Repeat with `Panasonic_FS-A1ST`. Scripts expect openMSX at `C:/Program Files/openMSX` and use isolated directories under `work/`. Supply machine ROMs separately. Reports in `validation/` identify their ROM hashes. These checks do not establish physical-hardware compatibility, exhaustive ROM input coverage or measured human difficulty.

## 日本語

通常は `tools/build_release.py` で配布データを再ビルドしてください。面の自動生成ツールは不要です。データやルールを変更した場合は `tools/build.py` の全探索検証を実行します。ソースと検証資料には解法が含まれます。実機動作は未確認です。
