"""Rebuild the released boards using hash-bound exhaustive-search evidence."""
from pathlib import Path
import hashlib,json
import build
R=Path(__file__).resolve().parents[1]
def verify_release():
 for name,digest in json.loads((R/'validation/build-inputs.json').read_text()).items():
  assert hashlib.sha256((R/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()==digest, 'Changed puzzle inputs: run tools/build.py for a fresh exhaustive search'
 proof=json.loads((R/'validation/level-validation.json').read_text())
 assert len(proof)==len(build.LEVELS)==50
 for lv,row in zip(build.LEVELS,proof):
  assert row['name']==lv['name'] and row['minimum']==lv['par']
  assert build.simulate(lv,lv['answer'])[0]
  for answer in row['solutions']:assert build.simulate(lv,answer)[0]
 (R/'outputs/level-validation.json').write_text(json.dumps(proof,indent=2))
 return proof
build.verify=verify_release
build.main()
