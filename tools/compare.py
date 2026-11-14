"""Compare go/types ground truth (oracle JSON) with shipped engine edges/unresolved usages."""
import json, sys, collections
oracle = json.load(open(sys.argv[1], encoding="utf-8")) or []
graph = json.load(open(sys.argv[2], encoding="utf-8"))
edges = {(e["source"], e["target"], e.get("line")) for e in graph["edges"] if e.get("type") == "method_call"}
unres = {(u.get("source"), u.get("line")) for u in graph["unresolved_go_usages"]}
stat = collections.Counter(); examples = collections.defaultdict(list)
for r in oracle:
    if r["CalleeFile"] == r["File"] or r["File"].endswith("_test.go"):
        continue
    key = "field" if r["ViaField"] else "direct"
    if (r["File"], r["CalleeFile"], r["Line"]) in edges: res = "edge"
    elif (r["File"], r["Line"]) in unres: res = "unresolved_recorded"
    else: res = "SILENT"
    stat[(key, res)] += 1
    if res == "SILENT" and len(examples[key]) < 6:
        examples[key].append(f'{r["File"]}:{r["Line"]} -> {r["Callee"]} ({r["CalleeFile"]})')
for k in sorted(stat): print(k, stat[k])
for k, v in examples.items():
    print("SILENT examples", k); [print("  ", x) for x in v]
