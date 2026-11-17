from specforge.lexer import Lexer
from specforge.parser import Parser
from specforge.semantic import SemanticAnalyzer

def test_recovery_5_errors():
    bad = """
    entity {
    statemachine X {
        A -> B on
        -> C on foo
    }
    rule {
    entity
    """
    ast, errors = Parser(Lexer(bad).tokens).parse()
    assert len(errors) >= 5, f"Expected >=5 errors, got {len(errors)}: {errors}"

def test_semantic_3_errors():
    src = """
    statemachine Ghost.status {
        A -> B on x
    }
    statemachine Equipment.status {
        X -> Y on a
        Z -> Y on b
    }
    """
    ast, _ = Parser(Lexer(src).tokens).parse()
    errs = SemanticAnalyzer(ast).analyze()
    assert len(errs) >= 3, f"Expected >=3 semantic errors, got {len(errs)}"
