import click
import json
from pathlib import Path
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .interpreter import Interpreter
from .trace import TraceabilityGraph
from .db import Database
from .visualize import StateMachineLayout

@click.group()
def cli(): pass

@cli.command()
@click.argument("file")
def parse(file):
    text = Path(file).read_text()
    tokens = Lexer(text).tokens
    ast, errors = Parser(tokens).parse()
    errors += SemanticAnalyzer(ast).analyze()
    if errors:
        for e in errors: print(f"ERROR {e}")
    else:
        print(f"OK: {len(ast)} nodes parsed")

@cli.command()
@click.argument("file")
def visualize(file):
    text = Path(file).read_text()
    ast, _ = Parser(Lexer(text).tokens).parse()
    for n in ast:
        if n['type'] == 'statemachine':
            states = set()
            edges = []
            for t in n['transitions']:
                if t['from'] != '*': states.add(t['from'])
                states.add(t['to'])
                edges.append((t['from'], t['to']))
            out = StateMachineLayout(list(states), edges).to_svg(filename=f"{file}.svg")
            print(f"Saved: {out}")

@cli.command()
@click.argument("reqs")
@click.argument("tests")
def trace(reqs, tests):
    g = TraceabilityGraph()
    for r in json.loads(Path(reqs).read_text()):
        g.add_node(r['id'], 'req', r['text'])
    for t in json.loads(Path(tests).read_text()):
        g.add_node(t['id'], 'test', json.dumps(t))
        for rid in t.get('covers', []):
            g.add_link(rid, t['id'])
    cov = g.coverage_matrix()
    print("Coverage:")
    print(f"  Reqs without tests: {cov['reqs_without_tests']}")
    print(f"  Dead specs: {cov['dead_specs']}")

@cli.command()
@click.argument("cr_file")
@click.argument("reqs")
@click.argument("tests")
def impact(cr_file, reqs, tests):
    g = TraceabilityGraph()
    for r in json.loads(Path(reqs).read_text()):
        g.add_node(r['id'], 'req', r['text'])
    for t in json.loads(Path(tests).read_text()):
        g.add_node(t['id'], 'test', json.dumps(t))
        for rid in t.get('covers', []):
            g.add_link(rid, t['id'])
    cr = json.loads(Path(cr_file).read_text())
    changed = set(cr['changed_reqs'])
    affected = g.get_impact_set(changed)
    print(f"Changed: {changed}")
    print(f"Affected tests ({len(affected)}): {sorted(affected)}")

@cli.command()
@click.argument("spec")
@click.argument("tests")
@click.option("--seed", default=42)
def run(spec, tests, seed):
    ast, _ = Parser(Lexer(Path(spec).read_text()).tokens).parse()
    interp = Interpreter(ast); interp.load()
    from .testing import TestRunner
    runner = TestRunner(interp, seed)
    results = runner.run_all(json.loads(Path(tests).read_text()))
    for r in results:
        print(f"{r['id']}: {r['status']}")

@cli.command()
def initdb():
    Database("specforge.db")
    print("DB initialized")
