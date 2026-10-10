"""Authored cooperative routes, checked by the independent simulator."""
from puzzles import *

def compile_routes(paths,special,height=12,decoys=()):
    routes=[expand(p) for p in paths];tracks=[0]*(8*height);terrain=tracks[:]
    sockets=[];answer=[];facing=[]
    for route in routes:
        for a,b in zip(route,route[1:]):
            d=DIR.index((b[0]-a[0],b[1]-a[1]))
            tracks[a[1]*8+a[0]]|=1<<d;tracks[b[1]*8+b[0]]|=1<<((d+2)%4)
        for a,b,c in zip(route,route[1:],route[2:]):
            di=DIR.index((b[0]-a[0],b[1]-a[1]));do=DIR.index((c[0]-b[0],c[1]-b[1]))
            if di!=do:
                tool=1 if (do-di)%4==1 else 2
                if b in sockets:assert answer[sockets.index(b)]==tool
                else:sockets.append(b);answer.append(tool);facing.append(di)
    for p in decoys:
        if p not in sockets:
            sockets.append(p);answer.append(0);facing.append(0)
    for x,y,t in special:
        assert tracks[y*8+x],(x,y,t)
        terrain[y*8+x]=t
    for who,p in enumerate(routes):terrain[p[-1][1]*8+p[-1][0]]=10 if who==0 else 13
    starts=[p[0]+[DIR.index((p[1][0]-p[0][0],p[1][1]-p[0][1]))] for p in routes]
    assert len(sockets)<=12
    return dict(name='TEAMWORK',starts=starts,goals=[p[-1] for p in routes],start=starts[0],goal=routes[0][-1],sockets=sockets,answer=answer,facing=facing,mask=6,terrain=terrain,tracks=tracks,locks=0,par=sum(bool(x) for x in answer),tier='TEAM',routes=routes,height=height)

def reflected(lv):
    import copy
    lv=copy.deepcopy(lv)
    for field in ['terrain','tracks']:
        out=[]
        for y in range(lv['height']):
            row=lv[field][y*8:y*8+8][::-1]
            if field=='tracks':row=[(v&5)|((v&2)<<2)|((v&8)>>2) for v in row]
            out.extend(row)
        lv[field]=out
    for field in ['starts','goals','sockets']:
        for p in lv[field]:
            p[0]=7-p[0]
            if len(p)==3:p[2]=(-p[2])%4
    lv['answer']=[3-v if v else 0 for v in lv['answer']]
    lv['facing']=[(-v)%4 for v in lv['facing']]
    lv['start']=lv['starts'][0];lv['goal']=lv['goals'][0]
    lv['routes']=[[[7-x,y] for x,y in p] for p in lv['routes']]
    return lv

def wide(kind):
    # Two bridges are made from opposite directions. The rabbit opens red,
    # the cat opens blue; both actors need the shared bridge crossings.
    top=2+(kind%3);bottom=8+(kind//3)%2;cross=2+(kind//6)%2
    cat=[[1,top],[6,top],[6,bottom],[1,bottom],[1,6],[cross,6]]
    rabbit=[[1,0],[5,0],[5,11],[cross,11],[cross,5],[7,5]]
    special=[(2,0,2),(3,0,4),(2,top,3),(4,top,1),(5,top,6),
             (6,7,8),(5,5,7),(cross+1,bottom,1),(cross,bottom,6)]
    if kind>=6:
        # Final delivery turns back toward the centre, after crossing twice.
        rabbit.extend([[7,1],[6,1]])
    if kind>=10:
        # Cat must take the return route before entering its own home.
        cat[-1]=[0,6]
        cat.append([0,5])
    lv=compile_routes([cat,rabbit],special)
    return lv

def add_choices(lv,seed):
    """Add alternative connected passages only if they preserve the puzzle proof."""
    import copy,random
    candidates=[];height=lv['height']
    for x,y in lv['sockets']:
        for d,(dx,dy) in enumerate(DIR):
            if lv['tracks'][y*8+x]&(1<<d):continue
            path=[[x,y]];nx=x;ny=y
            while True:
                nx+=dx;ny+=dy
                if not(0<=nx<8 and 0<=ny<height):break
                if lv['terrain'][ny*8+nx]:break
                path.append([nx,ny])
                if lv['tracks'][ny*8+nx]:
                    if len(path)>2:candidates.append(path)
                    break
    random.Random(seed).shuffle(candidates);accepted=0
    for path in candidates:
        trial=copy.deepcopy(lv)
        for a,b in zip(path,path[1:]):
            d=DIR.index((b[0]-a[0],b[1]-a[1]))
            trial['tracks'][a[1]*8+a[0]]|=1<<d
            trial['tracks'][b[1]*8+b[0]]|=1<<((d+2)%4)
        if not simulate(trial,trial['answer'])[0]:continue
        minimum,wins,_=solve(trial)
        if minimum<lv['par']:continue
        if solve(trial,cat_power=False)[1] or solve(trial,rabbit_power=False)[1]:continue
        lv=trial;accepted+=1
        if accepted==2:break
    lv['alternate_passages']=accepted
    return lv

def main():
    # Keep the original ten introductions byte-for-byte in gameplay content.
    levels=[make(k,m) for k in range(5) for m in (False,True)]
    for lv in levels:lv['height']=6
    for n in range(5):
        cat=[[1,2],[6,2],[6,0],[7,0]]
        rabbit=[[1,0],[5,0],[5,4],[7,4]]
        if n>=1:rabbit.append([7,5])
        if n>=2:cat.append([7,1])
        if n>=3:rabbit.extend([[6,5],[6,3]])
        if n>=4:rabbit.append([4,3])
        special=[(2,0,2),(3,0,4),(2,2,3),(4,2,1),(5,2,6),(6,1,8),(5,3,7)]
        lv=compile_routes([cat,rabbit],special,6)
        levels.extend([lv,reflected(lv)])
    for k in range(15):
        lv=wide(k);levels.extend([lv,reflected(lv)])
    assert len(levels)==50
    for i,lv in enumerate(levels):
        if i>=10:
            lv=add_choices(lv,20261010+i);levels[i]=lv
        ok,events,_,reason=simulate(lv,lv['answer'])
        assert ok,(i+1,reason,events,lv['answer'])
        minimum,wins,checked=solve(lv)
        assert minimum>=2 and wins,(i+1,minimum)
        lv['par']=minimum;lv['minimum_moves']=minimum;lv['solutions']=len(wins)
        lv['name']=f'STAGE {i+1:02}'
        print(i+1,minimum,len(lv['sockets']),checked,flush=True)
    from sequence_campaign import insert
    levels=insert(levels,compile_routes)
    from pressure_campaign import insert as insert_pressure
    levels=insert_pressure(levels)
    (R/'assets/levels.json').write_text(json.dumps(levels,indent=2))

if __name__=='__main__':main()
