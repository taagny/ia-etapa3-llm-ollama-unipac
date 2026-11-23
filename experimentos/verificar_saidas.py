"""Verifica sintaxe e asserts dos blocos Python gerados nos experimentos."""

from __future__ import annotations

import ast
import copy
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = [
    ROOT / "saidas" / "cenario_A_1.txt",
    ROOT / "saidas" / "cenario_A_2.txt",
    ROOT / "saidas" / "cenario_B_1.txt",
    ROOT / "saidas" / "cenario_B_2.txt",
    ROOT / "saidas" / "cenario_C_1.txt",
    ROOT / "saidas" / "cenario_C_2.txt",
    ROOT / "saidas" / "com_seed" / "cenario_B_seed42_1.txt",
    ROOT / "saidas" / "com_seed" / "cenario_B_seed42_2.txt",
    ROOT / "saidas" / "com_seed" / "cenario_C_seed42_1.txt",
    ROOT / "saidas" / "com_seed" / "cenario_C_seed42_2.txt",
    ROOT / "saidas" / "execucao_prints" / "cenario_A_print.txt",
    ROOT / "saidas" / "execucao_prints" / "cenario_B_print.txt",
    ROOT / "saidas" / "execucao_prints" / "cenario_C_print.txt",
]
SAFE_IMPORTS = {"re", "string", "unicodedata"}
FORBIDDEN_NAMES = {
    "open",
    "eval",
    "exec",
    "__import__",
    "system",
    "popen",
}
FORBIDDEN_MODULES = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "urllib",
    "http",
    "requests",
    "ftplib",
}


def extract_code(text: str) -> str:
    match = re.search(r"```python\s*\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("bloco ```python não encontrado")
    return match.group(1)


def safety_issues(tree: ast.AST) -> list[str]:
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    issues.append(f"import proibido: {alias.name}")
                elif root not in SAFE_IMPORTS:
                    issues.append(f"import externo não aprovado: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_MODULES:
                issues.append(f"import proibido: {node.module}")
            elif root not in SAFE_IMPORTS:
                issues.append(f"import externo não aprovado: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_NAMES:
                issues.append(f"chamada proibida: {node.func.id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_NAMES:
                issues.append(f"chamada proibida: {node.func.attr}")
    return sorted(set(issues))


class RemoveAsserts(ast.NodeTransformer):
    def visit_Assert(self, node: ast.Assert) -> None:
        return None


def main() -> None:
    for path in OUTPUTS:
        print(f"ARQUIVO: {path.relative_to(ROOT)}")
        try:
            code = extract_code(path.read_text(encoding="utf-8"))
        except Exception as error:
            print(f"  EXTRAÇÃO: falhou ({type(error).__name__}: {error})")
            continue
        try:
            tree = ast.parse(code)
            print("  SINTAXE: passou")
        except SyntaxError as error:
            print(f"  SINTAXE: falhou ({error})")
            continue
        issues = safety_issues(tree)
        if issues:
            print(f"  EXECUÇÃO: não realizada ({'; '.join(issues)})")
            continue
        assert_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
        namespace: dict[str, object] = {"__builtins__": __builtins__}
        try:
            setup_tree = RemoveAsserts().visit(copy.deepcopy(tree))
            ast.fix_missing_locations(setup_tree)
            exec(compile(setup_tree, str(path), "exec"), namespace, namespace)
        except Exception as error:
            print(f"  PREPARAÇÃO: falhou ({type(error).__name__}: {error})")
            continue
        if not assert_nodes:
            print("  ASSERTS: nenhum assert encontrado")
            continue
        for number, assert_node in enumerate(assert_nodes, start=1):
            single_assert = ast.Module(body=[copy.deepcopy(assert_node)], type_ignores=[])
            ast.fix_missing_locations(single_assert)
            try:
                exec(compile(single_assert, str(path), "exec"), namespace, namespace)
                print(f"  ASSERT {number} (linha {assert_node.lineno}): passou")
            except AssertionError as error:
                print(
                    f"  ASSERT {number} (linha {assert_node.lineno}): falhou "
                    f"(AssertionError: {error})"
                )
            except Exception as error:
                print(
                    f"  ASSERT {number} (linha {assert_node.lineno}): falhou "
                    f"({type(error).__name__}: {error})"
                )


if __name__ == "__main__":
    main()
