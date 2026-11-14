"""Run the shipped 0.3.15 Normal Lane (01) and Fast Lane (00a) graph builders on a directory."""
import importlib.util, json, sys, io, contextlib
from pathlib import Path
ENG = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("engine0315")  # extracted unvibecode-0.3.15 wheel (has shipreadyv2/)
sys.path.insert(0, str(ENG))
def load(fname, modname):
    spec = importlib.util.spec_from_file_location(modname, ENG / "shipreadyv2" / "engine_sources" / fname)
    m = importlib.util.module_from_spec(spec); sys.modules[modname] = m; spec.loader.exec_module(m); return m
repo = Path(sys.argv[1]).resolve()
which = sys.argv[2] if len(sys.argv) > 2 else "01"
fname = {"01": "01_shipreadyv2_merged_graph_pipeline_5chunks.py", "00a": "00a_shipreadyv2_fast_lane_v11_api_context_bundle.py"}[which]
m = load(fname, "eng" + which)
with contextlib.redirect_stdout(io.StringIO()):
    g = m.ShipReadyV2DeepGraphBuilder(str(repo)).build()
out = {k: g[k] for k in ("summary", "edges", "package_edges", "unresolved_go_usages")}
print(json.dumps(out, indent=1, default=str))
