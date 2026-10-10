# Build and verification

## Build the published campaign

The checked-in `assets/levels.json` and `assets/passwords.json` define the released campaign and persistent passwords. Rebuilding does not regenerate them.

Requirements: Python 3, Pillow, Pasmo, and the fonts used by the graphics generators.
The current scripts target a Windows development environment and use `C:/Windows/Fonts/consolab.ttf`, `meiryob.ttc`, and related fonts. Font files are not bundled. An alternative font can change the generated graphics and ROM hash.

```powershell
python -m pip install Pillow
$env:PASMO = 'C:/path/to/pasmo.exe'
python tools/build.py
```

Without `PASMO`, the builder searches PATH, then tries `C:/Software/Pasmo/pasmo.exe`.
It writes `outputs/PAWS-PARTNERS-MSX2.rom` and generated `assets/` / `work/` files.
Do not rebuild while an emulator has the output ROM open.

`tools/campaign.py` is an authoring tool that regenerates stage data. It is **not required** to build the published campaign.
Source stage data includes solutions; read it only if spoilers are acceptable.

## Verification

Emulator scripts currently expect openMSX under `C:/Program Files/openMSX`. Machine ROMs must be provided separately where required. The scripts use isolated user directories under `work/` and do not modify ordinary openMSX user settings.

```powershell
python tools/check_open.py --machine TOY_MSX2_64
python tools/check_open.py --machine C-BIOS_MSX2_EU
python tools/check_open.py --machine Panasonic_FS-A1ST
python tools/check_passwords.py
python tools/check_sequence.py
python tools/check_music.py
python tools/verify_music_trace.py
```

The custom `TOY_MSX2_64` profile is generated from C-BIOS MSX2 JP with 64 KiB RAM and 64 KiB VRAM. Turbo R testing uses the game's Z80 mode.

Published ROM SHA-256:

```text
4ea8e0b01c95d51a2cc0a2b77c8729792c7969010fdbb323e9a4637551dabda1
```

- 50-stage keyboard-driven regression: **821 checks per profile**, all passing across the three profiles above.
- Password entry: **255 checks**, all passing.
- WAIT / FLIP: **12 checks**, all passing, including too-short/too-long waits, pause, overview, and retry.
- Music: **9 checks**, including two loops, title/stuck muting, and retry restart.
- Music shadow-register trace: **4,100 frames**, matching the supplied PSG stream, including looping and restart.

Reports under `validation/` carry the tested ROM hash. These checks do not prove behavior on physical hardware or every emulator. They also do not establish human difficulty or exhaustive correctness of every possible play sequence.

## Audio implementation

`tools/compile_music.py` extracts chip-0 PSG writes from the supplied register data into 5,566 bytes. It preserves timing and excludes unused OPLL/SCC initialization writes.
The 8 KiB music bank is mapped temporarily by the interrupt routine and the renderer's bank is restored afterwards.
VBlank playback is independent of the main rendering loop. VDP control-port pairs and mapper updates are protected against interruption.
Register 7 preserves the PSG I/O-direction bits. Brief effects borrow channel C; A/B continue playing the melody.
The 60 Hz source follows the display's approximately-60 Hz VBlank frequency; this introduces a small tempo difference from exact 60.000 Hz.

## 日本語補足

配布済みの面データと合言葉はそのままビルドしてください。`campaign.py` の実行は通常不要です。
検証スクリプトには開発環境用のパスが含まれます。実行環境に合わせて変更してください。
公開している確認結果はエミュレーター上のもので、実機動作保証ではありません。
