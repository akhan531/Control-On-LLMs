"""W4 grid search under the W1-tightened cell rule."""
from fractions import Fraction as F
import itertools, json

# W1 measured the low->high switch at 0.70 (wording A) and 0.80 (wording B).
# Any predicted belief between them is a cell where the two wordings disagree
# about the correct level, so the result would be wording-dependent. Exclude it,
# and its mirror image on the low side.
DEAD_HI = (0.65, 0.85)
DEAD_LO = (0.15, 0.35)
NEAR_EVEN = 0.05
EDGES = (0.25, 0.50, 0.75)

def lvl(x):
    return 0 if x < .25 else 1 if x < .50 else 2 if x < .75 else 3

def usable(x):
    if DEAD_LO[0] <= x <= DEAD_LO[1] or DEAD_HI[0] <= x <= DEAD_HI[1]:
        return False
    return abs(x - 0.5) >= NEAR_EVEN

def b_pos(p, k):
    return float(p**k / (p**k + (1-p)**k))

def q(p, N, k, d):
    a = ((1-d)*p)**k * (1 - (1-d)*p)**(N-k)
    b = ((1-d)*(1-p))**k * (1 - (1-d)*(1-p))**(N-k)
    return float(a/(a+b))

rows = []
for pnum in (55, 65, 70, 75, 80):
    p = F(pnum, 100)
    if pnum == 60:           # reserved for W1
        continue
    for N in range(5, 14):
        for k in range(1, N):
            bp = b_pos(p, k)
            if not usable(bp):
                continue
            for d in (F(0), F(3, 10)):
                qq = q(p, N, k, d)
                if not usable(qq):
                    continue
                if lvl(bp) == lvl(qq):
                    continue          # no discrimination available
                rows.append(dict(p=pnum/100, N=N, k=k, delta=float(d),
                                 b_pos=round(bp,4), q=round(qq,4),
                                 lvl_b=lvl(bp), lvl_q=lvl(qq),
                                 span=lvl(bp)-lvl(qq)))

print(f"{len(rows)} informative (p,N,k,delta) cells survive the dead-zone rule\n")
# a cell is a (p,N,k) with BOTH delta values usable -- D7 wants delta as an axis
byk = {}
for r in rows:
    byk.setdefault((r['p'],r['N'],r['k']), []).append(r)
both = {k:v for k,v in byk.items() if len(v)==2}
print(f"{len(both)} (p,N,k) cells informative at BOTH delta=0 and delta=0.3\n")
print(f"{'p':>5}{'N':>4}{'k':>3} {'b_pos':>7}{'lvl':>4} | {'q(d=0)':>7}{'lvl':>4} | {'q(d=.3)':>8}{'lvl':>4}")
for (p,N,k), v in sorted(both.items()):
    z = {r['delta']: r for r in v}
    a, b = z[0.0], z[0.3]
    print(f"{p:>5}{N:>4}{k:>3} {a['b_pos']:>7.3f}{a['lvl_b']:>4} | "
          f"{a['q']:>7.3f}{a['lvl_q']:>4} | {b['q']:>8.3f}{b['lvl_q']:>4}")
json.dump(rows, open("w4_candidates.json","w"), indent=1)
