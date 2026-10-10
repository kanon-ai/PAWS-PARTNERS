"""Two friends: deterministic frame simulator and complete placement search."""
from pathlib import Path
import json,itertools
R=Path(__file__).resolve().parents[1]
DIR=[(0,-1),(1,0),(0,1),(-1,0)]
NAMES=['EMPTY','RIGHT','LEFT']

def expand(nodes):
 out=[nodes[0][:]]
 for q in nodes[1:]:
  x,y=out[-1];dx=0 if q[0]==x else (1 if q[0]>x else -1);dy=0 if q[1]==y else (1 if q[1]>y else -1)
  assert not(dx and dy)
  while [x,y]!=q:x+=dx;y+=dy;out.append([x,y])
 return out

def make(kind,mirror=False):
 if kind==0:
  paths=[[[1,4],[6,4],[6,3]],[[1,0],[6,0],[6,1]]];special=[];name='MEET THE FRIENDS'
 elif kind==1:
  paths=[[[1,4],[6,4],[6,3]],[[1,0],[6,0],[6,1]]];special=[(2,0,2),(3,0,4),(2,4,3),(3,4,1),(4,4,6)];name='HOP AND OPEN'
 else:
  paths=[[[1,2],[6,2],[6,0]],[[1,0],[5,0],[5,4],[7,4]]]
  special=[(2,0,2),(3,0,4),(2,2,3),(4,2,1),(5,2,6)]
  name='BUILD A BRIDGE'
  if kind>=3:special.extend([(6,1,8),(5,3,7)]);name='HELP EACH OTHER'
  if kind>=4:paths[0].append([7,0]);name='THE LAST DELIVERY'
 if mirror:
  paths=[[[7-x,y] for x,y in p] for p in paths];special=[(7-x,y,t) for x,y,t in special];name+=' WEST'
 route=[expand(p) for p in paths];tracks=[0]*48;terrain=[0]*48;sockets=[];answer=[];facing=[]
 for p in route:
  for a,b in zip(p,p[1:]):
   d=DIR.index((b[0]-a[0],b[1]-a[1]));tracks[a[1]*8+a[0]]|=1<<d;tracks[b[1]*8+b[0]]|=1<<((d+2)%4)
  for i in range(1,len(p)-1):
   a,b,c=p[i-1:i+2];di=DIR.index((b[0]-a[0],b[1]-a[1]));do=DIR.index((c[0]-b[0],c[1]-b[1]))
   if di!=do:
    assert b not in sockets
    sockets.append(b);answer.append(1 if (do-di)%4==1 else 2);facing.append(di)
 for x,y,t in special:terrain[y*8+x]=t
 # Routes are physical paths. Off-path decorative stones do not affect the solution.
 for x,y in [(0,3),(7,3),(0,5)]:
  if not tracks[y*8+x]:terrain[y*8+x]=5
 for who,p in enumerate(route):terrain[p[-1][1]*8+p[-1][0]]=10 if who==0 else 13
 starts=[p[0]+[DIR.index((p[1][0]-p[0][0],p[1][1]-p[0][1]))] for p in route]
 return dict(name=name,starts=starts,goals=[p[-1] for p in route],start=starts[0],goal=route[0][-1],sockets=sockets,answer=answer,facing=facing,mask=6,terrain=terrain,tracks=tracks,locks=0,par=len(answer),tier='TEAM',routes=route)

def simulate(lv,parts,cat_power=True,rabbit_power=True,trace=False):
 width=lv.get('width',8);terrain=lv['terrain'][:];gate=0;events=[];height=len(terrain)//width
 # x,y,d,remaining,targetX,targetY,done,jump,blocked
 actors=[[x,y,d,0,x,y,0,0,0,0] for x,y,d in lv['starts']]
 sockets={tuple(p):a for p,a in zip(lv['sockets'],parts)};seen=set();frames=[]
 def occupant(x,y,other):return not other[6] and ([x,y]==other[:2] or (other[3] and [x,y]==other[4:6]))
 for tick in range(6000):
  support_count=sum(t==19 for t in terrain)+sum(not a[6] and terrain[a[1]*width+a[0]] in (18,30) for a in actors)
  pressure=support_count>0
  key=(tuple(terrain),gate,tuple(tuple(a) for a in actors))
  if key in seen:return False,events,frames,'waiting-or-loop'
  seen.add(key)
  for who,a in enumerate(actors):
   if a[6]:continue
   if a[9]:a[9]-=1;continue
   if a[3]==0:
    a[8]=1;x,y,d=a[:3];dx,dy=DIR[d];nx=x+dx;ny=y+dy
    if not(0<=nx<width and 0<=ny<height):continue
    idx=ny*width+nx
    if not(lv['tracks'][idx]&(1<<((d+2)%4))):continue
    t=terrain[idx];other=actors[1-who]
    if occupant(nx,ny,other):continue
    jump=0
    if t==2:
     if who!=1 or not rabbit_power:continue
     nx+=dx;ny+=dy;jump=1
     if not(0<=nx<width and 0<=ny<height):continue
     idx=ny*width+nx;t=terrain[idx]
     if not(lv['tracks'][idx]&(1<<((d+2)%4))) or occupant(nx,ny,other):continue
     if t in (1,2,5,6,19):continue
    if t in (1,19):
     if who!=0 or not cat_power or jump:continue
     bx=nx+dx;by=ny+dy
     if not(0<=bx<width and 0<=by<height):continue
     bi=by*width+bx;bt=terrain[bi]
     if not lv['tracks'][bi] or bt not in (0,2,6,9,18) or occupant(bx,by,other):continue
     terrain[bi]=9 if bt in (2,6) else (19 if bt==18 else 1);terrain[idx]=18 if t==19 else 0;events.append('fill' if bt in (2,6) else 'push')
    if t in (5,6):continue
    if t==3 and not(gate&1):continue
    if t in (7,28) and not(gate&2):continue
    if t==20 and not pressure:continue
    if t==41 and pressure:continue
    if t==43 and support_count<2:continue
    if t==33 and not(gate&8):continue
    if t==34 and gate&8:continue
    a[3]=28 if jump else 14;a[4]=nx;a[5]=ny;a[7]=jump;a[8]=0
    if jump:events.append('hop')
   a[3]-=1
   if a[3]==0:
    old=a[1]*width+a[0]
    if terrain[old]==35:terrain[old]=2;events.append('crumble')
    a[0:2]=a[4:6];a[7]=0;t=terrain[a[1]*width+a[0]]
    if t==4:gate|=1;events.append('red')
    if t in (32,39):
     gate^=8;events.append('valve-open' if gate&8 else 'valve-close')
     if t==39:terrain[a[1]*width+a[0]]=40;events.append('spent')
    if t in (8,31):gate|=2;events.append('blue')
    if 23<=t<=26:a[2]=t-23
    if t==28:a[2]=2
    if t in (30,31):a[2]=1
    if t==14 and who==0:gate^=4;events.append('switch')
    if t==15:a[2]=2 if gate&4 else 1;events.append('arrow-down' if gate&4 else 'arrow-right')
    tool=sockets.get(tuple(a[:2]),0)
    if tool is None:return False,events,frames,('choice',lv['sockets'].index(a[:2]))
    if tool in (1,2):a[2]=(a[2]+(1 if tool==1 else -1))%4
    elif tool>=3:a[9]=(tool-2)*28;events.append('wait-'+str((tool-2)*2))
    if a[:2]==lv['goals'][who]:a[6]=1;events.append('cat-home' if who==0 else 'rabbit-home')
  if trace:frames.append(dict(actors=[a[:] for a in actors],terrain=terrain[:],gate=gate))
  if all(a[6] for a in actors):return True,events,frames,'clear'
 return False,events,frames,'analysis-bound'

def solve(lv,cat_power=True,rabbit_power=True):
 # Branch only when an actor reaches an unassigned socket. Unvisited sockets
 # cannot affect a successful run and are completed as EMPTY for minimum cost.
 wins=[];minimum=99;checked=0;pending=[[None]*len(lv['sockets'])]
 while pending:
  parts=pending.pop();checked+=1
  result=simulate(lv,parts,cat_power=cat_power,rabbit_power=rabbit_power)
  assert result[3]!='analysis-bound', 'Inconclusive search'
  if isinstance(result[3],tuple):
   index=result[3][1]
   for value in [0]+[v for v in range(1,7) if lv["mask"]&(1<<v)]:
    nxt=parts[:];nxt[index]=value;pending.append(nxt)
  elif result[0]:
   solution=[p or 0 for p in parts]
   minimum=min(minimum,sum(bool(x) for x in solution));wins.append(solution)
 return minimum,wins,checked

def generate():
 levels=[make(k,m) for k in range(5) for m in (False,True)]
 for i,lv in enumerate(levels):
  minimum,wins,checked=solve(lv)
  assert minimum==lv['par']>=2,(i,minimum,wins)
  assert simulate(lv,lv['answer'])[0],i
  lv['minimum_moves']=minimum;lv['solutions']=len(wins)
  print(i+1,lv['name'],minimum,simulate(lv,lv['answer'])[1])
 (R/'assets/levels.json').write_text(json.dumps(levels,indent=2))
 return levels
if __name__=='__main__':generate()
