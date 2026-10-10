from pathlib import Path
import json
from puzzles import solve
R=Path(__file__).resolve().parents[1]
levels=json.loads((R/'assets/levels.json').read_text());report=[]
for i,lv in enumerate(levels):
 _,a,ca=solve(lv,cat_power=False)
 _,b,cb=solve(lv,rabbit_power=False)
 if i>=2:assert not a and not b
 report.append(dict(stage=i+1,cat_search_nodes=ca,rabbit_search_nodes=cb,without_cat_solutions=len(a),without_rabbit_solutions=len(b),both_required=i>=2))
(R/'outputs/cooperation-audit.json').write_text(json.dumps(report,indent=2))
print('Both abilities required in stages 3-50; complete reachable-decision search.')
