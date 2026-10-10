"""Three distinct cooperation puzzles replacing reflected campaign stages."""
import json,sys
from pathlib import Path
from puzzles import DIR,simulate,solve,R

def insert(levels):
 layouts=json.loads(Path(__file__).with_name('pressure-layouts.json').read_text())
 for s in layouts:
  for key in ['arrows','plates','gates','buttons','locks']:s[key]={tuple(p):v for p,v in s[key]}
 for index,s in zip([21,29,25],layouts):
  terrain=[0]*96;tracks=[0]*96
  for a,b in s['edges']:
   tracks[a[1]*8+a[0]]|=1<<DIR.index((b[0]-a[0],b[1]-a[1]))
  for p in s['boxes']:terrain[p[1]*8+p[0]]=1
  for p in s['holes']:terrain[p[1]*8+p[0]]=6
  for k,t in [('plates',18),('gates',20),('buttons',8),('locks',7)]:
   for p in s[k]:terrain[p[1]*8+p[0]]=t
  sockets=[list(p) for p in s['sockets']];arrows=dict(s['arrows'])
  answer={21:[0,2,2],29:[0,3,2],25:[1,1]}[index]
  facing={21:[1,1,0],29:[1,1,1],25:[3,1]}[index]
  if index==21:
   del arrows[(3,1)];sockets.append([3,1])
  for p,d in arrows.items():
   i=p[1]*8+p[0];old=terrain[i]
   if old==7:assert d==2;terrain[i]=28
   elif old==18:assert d==1;terrain[i]=30
   elif old==8:assert d==1;terrain[i]=31
   else:assert old==0;terrain[i]=23+d
  for who,p in enumerate(s['goals']):terrain[p[1]*8+p[0]]=10 if who==0 else 13
  starts=[list(p) for p in s['starts']];goals=[list(p) for p in s['goals']]
  lv=dict(name=f'STAGE {index+1:02}',starts=starts,start=starts[0],goals=goals,goal=goals[0],sockets=sockets,answer=answer,facing=facing,mask=126 if index==29 else 6,terrain=terrain,tracks=tracks,locks=0,height=12,tier='TEAM',routes=[],pressure=True,design=s['name'])
  minimum,wins,_=solve(lv)
  assert wins and minimum>=2,(index,minimum)
  assert simulate(lv,answer)[0],(index,simulate(lv,answer)[1:])
  lv.update(par=minimum,minimum_moves=minimum,solutions=len(wins))
  levels[index]=lv
 return levels

if __name__=='__main__':
 levels=json.loads((R/'assets/levels.json').read_text())
 (R/'assets/levels.json').write_text(json.dumps(insert(levels),indent=2))
