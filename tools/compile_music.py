"""Compile the supplied PSG register stream without changing notes or timing."""
from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]

def compile_music():
    folder = R / 'assets/music'
    song = json.loads((folder / 'registers.json').read_text())
    manifest = json.loads((folder / 'manifest.json').read_text())
    assert song['hz'] == 60 and manifest['loop'] and manifest['loopFrame'] == 0
    data = bytearray()
    previous = 0
    for event in song['events']:
        writes = [(reg, value) for chip, reg, value in event['writes'] if chip == 0]
        if not writes:
            continue
        delta = event['frame'] - previous
        assert 0 <= delta < 255 and len(writes) < 255
        data.extend((delta, len(writes)))
        for reg, value in writes:
            assert 0 <= reg <= 13 and 0 <= value <= 255
            data.extend((reg, value))
        previous = event['frame']
    assert previous == manifest['frames']
    data.extend((255, 0))
    assert len(data) <= 8192
    (folder / 'psg-stream.bin').write_bytes(data)
    return len(data)

if __name__ == '__main__':
    print(compile_music())
