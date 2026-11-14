"""Before/after evaluation of the field-receiver patch against go/types ground truth.
usage: eval_fix.py oracle.json graph_before.json graph_after.json [oracle_with_tests.json]
(the optional 4th file is used for the precision check, so edges from _test.go files are checked too)"""
import json, sys, collections
oracle = json.load(open(sys.argv[1], encoding="utf-8")) or []
def load(p):
    g = json.load(open(p, encoding="utf-8"))
    edges = {(e["source"], e["target"], e.get("line"), e.get("symbol")) for e in g["edges"] if e.get("type") == "method_call"}
    unres = {(u.get("source"), u.get("line")) for u in g["unresolved_go_usages"]}
    return edges, unres, g
b_edges, b_unres, _ = load(sys.argv[2]); a_edges, a_unres, ga = load(sys.argv[3])
truth = {}
for r in oracle:
    if r["CalleeFile"] == r["File"] or r["File"].endswith("_test.go"): continue
    truth.setdefault((r["File"], r["Line"]), []).append(r)
def classify(edges, unres, r):
    sym = r["Callee"].rsplit(".", 1)[-1]
    if (r["File"], r["CalleeFile"], r["Line"], sym) in edges: return "edge"
    if (r["File"], r["Line"]) in unres: return "unresolved"
    return "SILENT"
stat = collections.Counter()
for rows in truth.values():
    for r in rows:
        k = "field" if r["ViaField"] else "direct"
        stat[(k, "before", classify(b_edges, b_unres, r))] += 1
        stat[(k, "after", classify(a_edges, a_unres, r))] += 1
for k in sorted(stat): print(k, stat[k])
# precision: every NEW method_call edge must correspond to an oracle call at that file:line with that callee file
if len(sys.argv) > 4:
    truth = {}
    for r in json.load(open(sys.argv[4], encoding="utf-8")):
        truth.setdefault((r["File"], r["Line"]), []).append(r)
new = a_edges - b_edges
wrong = [e for e in new if not any(r["CalleeFile"] == e[1] and r["Callee"].endswith("." + e[3]) for r in truth.get((e[0], e[2]), []))]
print("new edges:", len(new), "not confirmed by oracle:", len(wrong))
for e in sorted(wrong)[:15]: print("  UNCONFIRMED", e)
new_unres = a_unres - b_unres
print("new unresolved records:", len(new_unres))
print("summary after:", {k: ga["summary"][k] for k in ("edges", "go_symbol_edges", "unresolved_go_usages")})
