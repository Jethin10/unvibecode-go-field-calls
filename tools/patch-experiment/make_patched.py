"""Create patched copies of the shipped 0.3.15 Go builders (01 and 00a) that
(1) record struct field types, (2) emit field-chain method calls, (3) resolve them.
Experimental only; the shipped files are not modified."""
import shutil, sys
from pathlib import Path
SRC = Path("engine0315")
DST = Path("engine_patched")
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("__pycache__"))

EDITS = [
 # 1. capture struct fields on the type entity
 ('''                    elif child.type == "struct_type":
                        kind = "struct"
''', '''                    elif child.type == "struct_type":
                        kind = "struct"
                        struct_fields = {}
                        for decl in walk_ts(child):
                            if decl.type != "field_declaration":
                                continue
                            ftype = self._go_named_type(child_by_field_name(decl, "type"), source_bytes)
                            for fname in named_children(decl):
                                if fname.type == "field_identifier" and ftype:
                                    struct_fields[node_text(fname, source_bytes).strip()] = ftype
'''),
 ('''                    entity["scope"] = "package" if self._go_is_package_level(node) else "local"
                    entities.append(entity)
            elif t in {"var_spec", "const_spec"}:''', '''                    entity["scope"] = "package" if self._go_is_package_level(node) else "local"
                    if kind == "struct" and struct_fields:
                        entity["fields"] = struct_fields
                    entities.append(entity)
            elif t in {"var_spec", "const_spec"}:'''),
 # 2. catalogue: struct -> fields
 ('''                    "types": defaultdict(list),
''', '''                    "types": defaultdict(list),
                    "struct_fields": {},
'''),
 ('''                elif kind in {"type", "struct", "interface"}:
                    entry["types"][name].append(record)
''', '''                elif kind in {"type", "struct", "interface"}:
                    entry["types"][name].append(record)
                    if kind == "struct" and entity.get("fields"):
                        entry["struct_fields"][name] = dict(entity["fields"])
'''),
 # 3. collector: emit a field-chain method_call instead of falling through
 ('''                if target is not None and target.type == "selector_expression":
                    operand = child_by_field_name(target, "operand")
                    field = child_by_field_name(target, "field")
                    if operand is not None and field is not None and operand.type == "identifier":
                        receiver = text(operand)''', '''                if target is not None and target.type == "selector_expression":
                    operand = child_by_field_name(target, "operand")
                    field = child_by_field_name(target, "field")
                    chain = []
                    root_node = operand
                    while root_node is not None and root_node.type == "selector_expression":
                        chain.insert(0, text(child_by_field_name(root_node, "field")))
                        root_node = child_by_field_name(root_node, "operand")
                    if chain and field is not None and root_node is not None and root_node.type == "identifier" and text(root_node) in env:
                        usages.append(
                            {
                                "kind": "method_call",
                                "receiver": text(operand),
                                "receiver_type": {"kind": "field_chain", "base": env.get(text(root_node)), "fields": chain, "name": ".".join(chain), "qualifier": None},
                                "symbol": text(field),
                                "line": line_range_from_ts_node(node)["start_line"],
                            }
                        )
                        if arguments is not None:
                            visit(arguments, env)
                        return
                    if operand is not None and field is not None and operand.type == "identifier":
                        receiver = text(operand)'''),
 # 4. resolver: walk the field chain through the catalogue
 ('''            if hint_kind == "call":''', '''            if hint_kind == "field_chain":
                current, base_reason, _ = resolve_hint(hint.get("base"))
                if current is None:
                    return None, base_reason or "unknown_receiver_type", []
                for field_name in hint.get("fields") or []:
                    pkg_dir, type_name, cross, qual = current
                    fields = ((go_catalog.get(pkg_dir) or {}).get("struct_fields") or {}).get(type_name) or {}
                    field_type = fields.get(field_name)
                    if not field_type:
                        return None, "unknown_field_type", []
                    if "." in field_type:
                        fq, fn = field_type.split(".", 1)
                        mapped = qualifier_to_package.get(fq)
                        if mapped is None:
                            return None, "external_receiver_type", []
                        current = (mapped, fn, True, fq)
                    else:
                        current = (pkg_dir, field_type, cross, qual)
                return current, None, []
            if hint_kind == "call":'''),
]
for name in ("00a_shipreadyv2_fast_lane_v11_api_context_bundle.py", "01_shipreadyv2_merged_graph_pipeline_5chunks.py"):
    p = DST / "shipreadyv2" / "engine_sources" / name
    t = p.read_text(encoding="utf-8")
    for old, new in EDITS:
        n = t.count(old)
        if n != 1: sys.exit(f"{name}: anchor count {n}: {old[:60]!r}")
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("patched", name)
