"""
Code Maintainability & Complexity Metrics Analyzer.
Uses Python's standard 'ast' module to objectively measure:
1. Cyclomatic Complexity (McCabe's formula: CC = E - N + 2P or count of decision points + 1)
2. Lines of Code (LOC) and Logical Lines of Code (LLOC)
3. Number of Responsibilities (Functions & Classes)
"""
import ast
import os
import sys

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.complexity += 1
        self.generic_visit(node)

def analyze_file(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)
    lines = code.splitlines()
    loc = len(lines)
    lloc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

    functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    total_cc = 0
    func_complexities = []
    for f in functions:
        vis = ComplexityVisitor()
        vis.visit(f)
        func_complexities.append((f.name, vis.complexity))
        total_cc += vis.complexity

    avg_cc = round(total_cc / len(functions), 2) if functions else 1.0

    return {
        'file': file_path,
        'loc': loc,
        'lloc': lloc,
        'num_classes': len(classes),
        'num_functions': len(functions),
        'avg_complexity': avg_cc,
        'max_complexity': max([c[1] for c in func_complexities], default=1)
    }

if __name__ == '__main__':
    targets = [
        'utils/calculations.py',
        'engines/financial_calculator.py',
        'services/analytics_service.py',
        'services/budget_service.py',
        'services/transaction_service.py',
        'repositories/transaction_repository.py',
        'repositories/budget_repository.py'
    ]
    print(f"{'File':<40} | {'LOC':<6} | {'LLOC':<6} | {'Classes':<8} | {'Funcs':<6} | {'Avg CC':<7} | {'Max CC':<7}")
    print("-" * 88)
    for t in targets:
        res = analyze_file(t)
        if res:
            print(f"{res['file']:<40} | {res['loc']:<6} | {res['lloc']:<6} | {res['num_classes']:<8} | {res['num_functions']:<6} | {res['avg_complexity']:<7} | {res['max_complexity']:<7}")
