#!/usr/bin/env python3
"""Static analysis of test files to build a coverage matrix."""
import ast
import json
import os
import re

BASE = "agent"
TEST_DIR = os.path.join(BASE, "tests")

TARGET_MODULES = [
    "agent.capabilities.act",
    "agent.agent_definition",
    "agent.llm",
    "agent.roles",
    "agent.langgraph_runtime",
    "agent.orchestrator",
    "agent.team_graph_runtime",
    "agent.trace_store",
    "agent.tools",
    "agent.capabilities",
    "agent.runtime",
    "agent.world_model",
    "agent.self_improve",
]

def short_module(m):
    return m.replace("agent.", "").replace("agent.capabilities.", "capabilities.")

def find_test_files():
    files = []
    for root, dirs, fnames in os.walk(TEST_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in fnames:
            if fn.endswith(".py") and not fn.startswith("."):
                files.append(os.path.join(root, fn))
    return files

def extract_assertions(node):
    """Summarize assert/self.assert* calls within a function body."""
    summaries = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Attribute) and sub.func.attr.startswith("assert"):
                attr = sub.func.attr
                args = []
                for a in sub.args:
                    if isinstance(a, ast.Constant):
                        args.append(repr(a.value)[:60])
                    elif isinstance(a, ast.Name):
                        args.append(a.id)
                    elif isinstance(a, ast.Attribute):
                        args.append(a.attr)
                    elif isinstance(a, ast.List):
                        args.append("[...]")
                    else:
                        args.append("...")
                if isinstance(sub.func.value, ast.Name) and sub.func.value.id == "self":
                    summaries.append(f"self.{attr}(" + ", ".join(args) + ")")
                elif isinstance(sub.func.value, ast.Name):
                    pass
            elif isinstance(sub.func, ast.Name) and sub.func.id == "assertRaisesRegex":
                if len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant):
                    summaries.append(f"assertRaisesRegex pattern={sub.args[1].value!r}")
            elif isinstance(sub.func, ast.Attribute) and sub.func.attr == "assertRaisesRegex":
                if isinstance(sub.func.value, ast.Name) and sub.func.value.id == "self":
                    if len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant):
                        summaries.append(f"self.assertRaisesRegex pattern={sub.args[1].value!r}")
    return summaries

def infer_modules(source, filename):
    """Infer tested modules from imports + filename."""
    modules = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("agent"):
                modules.add(node.module)
    # heuristic: filename implies module
    base = os.path.basename(filename).replace("test_", "").replace(".py", "")
    guess_candidates = [
        f"agent.{base}",
        f"agent.{base}_runtime",
        f"agent.capabilities.{base}",
        f"agent.roles.{base}",
    ]
    for t in TARGET_MODULES:
        if base and (
            t == guess_candidates[0] or t == guess_candidates[1] or
            t == guess_candidates[2] or t == guess_candidates[3]
        ):
            modules.add(t)
        if base in t.split(".")[-1]:
            modules.add(t)
    return sorted(modules)

def analyze():
    coverage = {"generated_at": None, "test_files": [], "module_coverage": {}}
    module_assert_counts = {}
    module_tests = {}

    for path in find_test_files():
        rel = os.path.relpath(path, BASE)
        with open(path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)

        classes = []
        test_funcs = []
        total_asserts = 0
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and any(
                isinstance(d, ast.Name) and d.id == "TestCase" for d in node.bases
            ):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                        asserts = extract_assertions(item)
                        total_asserts += len(asserts)
                        methods.append({
                            "name": item.name,
                            "assertions": asserts[:6],
                            "assert_count": len(asserts),
                        })
                        test_funcs.append(item.name)
                classes.append({"name": node.name, "test_methods": methods})
            elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                asserts = extract_assertions(node)
                total_asserts += len(asserts)
                test_funcs.append(node.name)

        modules = infer_modules(source, path)

        for m in modules:
            module_assert_counts.setdefault(m, 0)
            module_assert_counts[m] += total_asserts
            module_tests.setdefault(m, set())
            module_tests[m].update(test_funcs)

        coverage["test_files"].append({
            "file": rel,
            "size": os.path.getsize(path),
            "test_classes": classes,
            "test_function_count": len(test_funcs),
            "test_function_names": test_funcs,
            "inferred_modules": modules,
            "assert_counts_per_func": {c["name"]: c["assert_count"] for cls in classes for c in cls["test_methods"]},
        })

    # Build module coverage matrix
    all_test_files = [t["file"] for t in coverage["test_files"]]
    for m in sorted(module_assert_counts):
        coverage["module_coverage"][m] = {
            "test_files": sorted(t["file"] for t in coverage["test_files"] if m in t["inferred_modules"]),
            "total_asserts": module_assert_counts[m],
            "test_functions": sorted(module_tests.get(m, set())),
        }

    return coverage

if __name__ == "__main__":
    result = analyze()
    with open("coverage_matrix.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
