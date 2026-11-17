from hypothesis import given, settings
from specforge.testing import st_dsl_program, st_invalid_transition, st_cr
from specforge.lexer import Lexer
from specforge.parser import Parser

@given(prog=st_dsl_program())
@settings(max_examples=20)
def test_dsl_parseable(prog):
    ast, errs = Parser(Lexer(prog).tokens).parse()
    assert isinstance(ast, list)

@given(t=st_invalid_transition())
def test_invalid_transition_detected(t):
    assert t["should_fail"] is True
    assert t["from"] in ('Maintenance', 'Retired')

@given(cr=st_cr())
@settings(max_examples=20)
def test_cr_structure(cr):
    assert 1 <= len(cr) <= 3
    for c in cr:
        assert c["type"] in ('rule_threshold', 'state_transition', 'entity_field')
        assert isinstance(c["value"], int)
