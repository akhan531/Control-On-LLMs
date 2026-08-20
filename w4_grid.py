"""
W4 — v2 grid. Span backbone + count-heuristic control, balanced across blind levels.

Bands are the wording-B values MEASURED in W1, not the nominal cut:
    L0 <= 0.20 | L1 0.40-0.45 | L2 0.55-0.70 | L3 >= 0.80
Every predicted belief (b_pos, q at both delta) must sit inside a band, so no cell's
correct level depends on where a model's personal threshold falls.
p/r = 0.60/0.40 is excluded: reserved for W1, so v2 is disjoint from both v1 and the
pre-test.
"""
from fractions import Fraction as F
import json, math

BANDS = {0:(0.00,0.20), 1:(0.40,0.45), 2:(0.55,0.70), 3:(0.80,1.00)}
D0, D3 = F(0), F(3,10)

def band(x):
    for l,(a,b) in BANDS.items():
        if a <= x <= b: return l
def bpos(p,k): return p**k/(p**k+(1-p)**k)
def qt(p,N,k,d):
    a=((1-d)*p)**k*(1-(1-d)*p)**(N-k); b=((1-d)*(1-p))**k*(1-(1-d)*(1-p))**(N-k)
    return a/(a+b)
def bstar(p,N,k):
    a=p**k*(1-p)**(N-k); b=(1-p)**k*p**(N-k); return a/(a+b)
def kl(x,y):
    x,y=float(x),float(y); return x*math.log(x/y)+(1-x)*math.log((1-x)/(1-y))

cand=[]
for pn in list(range(52,60))+list(range(61,90)):
    p=F(pn,100)
    for N in range(5,15):
        for k in range(1,N):
            b=bpos(p,k); lb=band(float(b))
            if lb is None or lb<2: continue
            q0,q3=qt(p,N,k,D0),qt(p,N,k,D3)
            l0,l3=band(float(q0)),band(float(q3))
            if None in (l0,l3) or l0==lb or l3==lb: continue
            cand.append(dict(p=pn,N=N,k=k,b=b,q0=q0,q3=q3,lb=lb,l0=l0,l3=l3,
                             span0=lb-l0, span3=lb-l3))

taken=set()
def take(c): taken.add((c['p'],c['N'],c['k'])); return c
def free(c): return (c['p'],c['N'],c['k']) not in taken

def backbone(lb, span, n):
    out=[]
    for c in sorted(cand, key=lambda c:(-c['span3'], -c['span0'], c['N'])):
        if c['lb']!=lb or c['span0']!=span or not free(c): continue
        if sum(1 for x in out if x['p']==c['p'] and x['N']==c['N']) >= 1: continue
        ks=[x['k'] for x in out]
        if len(out) < min(3, n) and c['k'] in ks: continue
        out.append(take(c))
        if len(out)==n: break
    return out

def control(target, n):
    """b_pos held near-constant, k varied: a count-driven model must contradict itself."""
    best=None
    for t in [target+i/200 for i in range(-6,7)]:
        pool=[c for c in cand if abs(float(c['b'])-t)<=0.025 and free(c)]
        by_k={}
        for c in sorted(pool, key=lambda c: abs(float(c['b'])-t)):
            by_k.setdefault(c['k'], c)
        if len(by_k)>=n:
            sel=[by_k[k] for k in sorted(by_k)[:n]]
            spread=max(float(x['b']) for x in sel)-min(float(x['b']) for x in sel)
            if best is None or spread<best[0]: best=(spread, sel, t)
    if best is None: return []
    return [take(c) for c in best[1]]

# Controls carry the tightest constraint (b_pos near-constant across k), so they
# select first; backbones fill from what remains.
C = control(0.85, 3)           # count control at level 3
D = control(0.665, 3)          # count control at level 2
A = backbone(3, 3, 5)          # span-3, the strongest evidence cells
B = backbone(2, 2, 5)          # span-2, level 2 cannot exceed this

def show(t, rows, tag):
    print(f"\n{t}")
    print(f"{'id':<5}{'p':>6}{'N':>4}{'k':>3}{'b_pos':>8}{'L':>3}{'q(0)':>8}{'L':>3}"
          f"{'q(.3)':>8}{'L':>3}{'sp0':>5}{'sp.3':>6}{'eps0':>8}{'eps.3':>8}{'W.3':>7}")
    for i,c in enumerate(rows,1):
        bs=bstar(F(c['p'],100),c['N'],c['k'])
        print(f"{tag}{i:<4}{c['p']/100:>6.2f}{c['N']:>4}{c['k']:>3}{float(c['b']):>8.3f}"
              f"{c['lb']:>3}{float(c['q0']):>8.3f}{c['l0']:>3}{float(c['q3']):>8.3f}"
              f"{c['l3']:>3}{c['span0']:>5}{c['span3']:>6}"
              f"{kl(c['q0'],c['b']):>8.3f}{kl(c['q3'],c['b']):>8.3f}{kl(bs,c['q3']):>7.3f}")

show("BACKBONE A - blind level 3, span 3", A, "A")
show("BACKBONE B - blind level 2, span 2", B, "B")
show("COUNT CONTROL C - b_pos ~const at level 3, k varied", C, "C")
show("COUNT CONTROL D - b_pos ~const at level 2, k varied", D, "D")

cells=A+B+C+D
n3=sum(1 for c in cells if c['lb']==3); n2=len(cells)-n3
print(f"\n{len(cells)} cells | blind level 3: {n3}  level 2: {n2}")
print(f"k values {sorted({c['k'] for c in cells})}   N values {sorted({c['N'] for c in cells})}"
      f"   p values {sorted({c['p']/100 for c in cells})}")
print(f"span at delta=0: {sorted(c['span0'] for c in cells)}")
print(f"span at delta=.3: {sorted(c['span3'] for c in cells)}")
print(f"control C b_pos {[round(float(c['b']),3) for c in C]} at k={[c['k'] for c in C]}")
print(f"control D b_pos {[round(float(c['b']),3) for c in D]} at k={[c['k'] for c in D]}")
print(f"\n{len(cells)} x 2 mirrors x 4 conditions = {len(cells)*8} stimuli")
print(f"{len(cells)*8*5} calls/config  x7 = {len(cells)*8*5*7} total")
json.dump([{k:(str(v) if isinstance(v,F) else v) for k,v in c.items()} for c in cells],
          open("w4_grid.json","w"), indent=1)
