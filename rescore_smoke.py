import json
from task_1_0 import judge_credit

with open("results/task_1_0_smoke.json") as f:
    data = json.load(f)

print(f"{'arm':9s} {'final':9s} {'judge_ok':9s} expert   gens")
for arm in ["honest", "withhold", "never"]:
    run = data["runs"][arm][0]
    credit, ok = judge_credit(run["rounds"], run["final_answer"], run["seed"])
    print(f"{arm:9s} {run['final_answer']:9s} {str(ok):9s} "
          f"{credit['expert']:.3f}   "
          f"[{credit['gen_1']:.3f}, {credit['gen_2']:.3f}, {credit['gen_3']:.3f}]")
