# UnvibeCode: Go calls through struct fields go missing

Repro files, screenshots and the scripts I used for my UnvibeCode Engineering Challenge 2026 (Cohort 3, Track 1) issue.

Short version: when a Go method is called through a struct field (`h.svc.Place()`, `o.store.Insert()`), UnvibeCode's Connected Code Map doesn't record the call at all. There's no edge, and it doesn't show up as unresolved either.

## What's here

- `repro/go-field-only/`: three files, handler → service → store, all calls through fields. Hosted review gives 0 edges and 0 unresolved Go usages.
- `repro/go-field-receiver/`: same, plus a `PlaceDirect` function that calls through a parameter. Only that call gets an edge.
- `images/`: screenshots of the hosted Connected Code Map.
- `tools/gotypes-checker/`: small Go program using `go/types` that lists every call through a struct field to a concrete method in another file. Run it with `go run . <repo>`.
- `tools/run_graph.py`, `tools/compare.py`: run the Go graph builder from the `unvibecode-0.3.15` wheel on a repo, then compare its edges with the checker's output.
- `tools/patch-experiment/`: the patch I tried (`make_patched.py`) and the before/after check (`eval_fix.py`).

## Running the repro

```
pip install --upgrade unvibecode
python -m unvibecode review --repository ./repro/go-field-only --no-open-browser
```

Then look at `technical-logs/connected_code_map.log` and the repository context ZIP.

For the local scripts you need the `unvibecode-0.3.15` wheel extracted into a folder called `engine0315`, plus `tree-sitter==0.26.0` and `tree-sitter-language-pack==1.22.1`.
