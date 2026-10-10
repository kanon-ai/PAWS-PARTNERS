"""Timing-window puzzles: two cat switches open then close a route window."""
from puzzles import simulate,solve

def insert(levels,compile_routes):
    indices=[20,23,27,31,35,39,43,45,47,49]
    for n,index in enumerate(indices):
        base=[5,6,7,8,9,10,5,7,9,10][n]
        start=1 if n>=6 else 0
        cat=[[start,base],[6,base],[6,0]]
        rabbit=[[0,0],[5,0],[5,4]]
        if n>=6:
            cat.extend([[7,0],[7,3]])
            rabbit.extend([[3,4],[3,6],[4,6]])
        special=[(1,0,2),(3,base,1),(4,base,6),(6,3,14),(6,1,14),(5,0,15)]
        lv=compile_routes([cat,rabbit],special,12)
        # The signal arrow, not a user turn, determines the direction here.
        at=lv['sockets'].index([5,0])
        for field in ['sockets','answer','facing']:lv[field].pop(at)
        lv['sockets'].append([2,0]);lv['answer'].append(3);lv['facing'].append(1)
        # An early arrival takes a one-way dead end. Once it leaves the arrow,
        # changing the signal later does not retroactively turn the rabbit.
        for x in [5,6]:
            lv['tracks'][x]|=2;lv['tracks'][x+1]|=8
        lv['mask']=126
        possible=[]
        for tool in range(3,7):
            lv['answer'][-1]=tool
            if simulate(lv,lv['answer'])[0]:possible.append(tool)
        assert possible,(index+1,base)
        lv['answer'][-1]=possible[0]
        minimum,wins,nodes=solve(lv)
        assert minimum>=2 and wins
        old=lv['mask'];lv['mask']=6
        assert not solve(lv)[1], 'WAIT must be necessary'
        lv['mask']=old
        assert not solve(lv,cat_power=False)[1]
        assert not solve(lv,rabbit_power=False)[1]
        lv.update(name=f'STAGE {index+1:02}',par=minimum,minimum_moves=minimum,solutions=len(wins),sequence=True,valid_authored_wait_beats=[(v-2)*2 for v in possible])
        levels[index]=lv
    return levels
