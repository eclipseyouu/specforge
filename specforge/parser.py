from dataclasses import dataclass
from typing import List, Dict, Optional
from .lexer import Token

@dataclass
class Diagnostic:
    line: int
    col: int
    message: str
    def __str__(self): return f"{self.line}:{self.col}: {self.message}"

class Parser:
    TOP_LEVEL = {'entity', 'statemachine', 'rule', '@'}

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[Diagnostic] = []
        self.ast: List[Dict] = []

    def cur(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF', '', 0, 0)

    def at(self, value=None, ttype=None) -> bool:
        t = self.cur()
        return (value is None or t.value == value) and (ttype is None or t.type == ttype)

    def advance(self) -> Token:
        t = self.cur()
        if t.type != 'EOF':
            self.pos += 1
        return t

    def _err(self, msg: str, token: Optional[Token] = None):
        t = token or self.cur()
        self.errors.append(Diagnostic(t.line, t.col, msg))

    def expect(self, value=None, ttype=None, desc=None) -> Optional[Token]:
        t = self.cur()
        ok = True
        if value is not None and t.value != value:
            ok = False
        if ttype is not None and t.type != ttype:
            ok = False
        if not ok:
            expected = desc or value or ttype
            self._err(f"Expected {expected}, got {t.type}('{t.value}')", t)
            return None
        return self.advance()

    def _skip_to(self, stops):
        while self.cur().type != 'EOF' and self.cur().value not in stops:
            self.advance()

    def parse(self):
        while self.cur().type != 'EOF':
            start = self.pos
            try:
                if self.at('@'):
                    self.ast.append(self._parse_annotation())
                elif self.at('entity'):
                    self.ast.append(self._parse_entity())
                elif self.at('statemachine'):
                    self.ast.append(self._parse_statemachine())
                elif self.at('rule'):
                    self.ast.append(self._parse_rule())
                else:
                    self._err(f"Unexpected '{self.cur().value}'")
                    self.advance()
            except Exception as e:
                self._err(f"Fatal: {e}")
                if self.pos == start:
                    self.advance()
        return self.ast, self.errors

    def _parse_annotation(self):
        self.advance()
        name = ''
        if self.cur().type == 'IDENT':
            name = self.advance().value
        else:
            self._err(f"Expected annotation name, got {self.cur().type}('{self.cur().value}')")
        args = []
        if not self.expect('('):
            return {'type': 'annotation', 'name': name, 'args': args}
        while not self.at(')') and self.cur().type != 'EOF':
            if self.cur().value == ',':
                self.advance()
                continue
            args.append(self.advance().value)
        self.expect(')')
        return {'type': 'annotation', 'name': name, 'args': args}

    def _parse_type(self) -> str:
        t = self.cur()
        if t.type not in ('IDENT', 'KEYWORD'):
            self._err(f"Expected type, got {t.type}('{t.value}')")
            return ''
        base = self.advance().value
        if base == 'Enum' and self.at('('):
            self.advance()
            args = []
            while not self.at(')') and self.cur().type != 'EOF':
                if self.at(','):
                    self.advance()
                    continue
                args.append(self.advance().value)
            self.expect(')')
            return f"Enum({','.join(args)})"
        return base

    def _parse_entity(self):
        self.advance()
        name = 'unknown'
        if self.cur().type == 'IDENT':
            name = self.advance().value
        else:
            self._err(f"Expected entity name, got {self.cur().type}('{self.cur().value}')")

        fields = []
        if not self.expect('{'):
            self._skip_to(self.TOP_LEVEL)
            return {'type': 'entity', 'name': name, 'fields': fields}

        while not self.at('}') and self.cur().type != 'EOF':
            if self.cur().value in self.TOP_LEVEL:
                self._err(f"Unexpected '{self.cur().value}' inside entity '{name}'")
                break
            if self.cur().type == 'IDENT':
                fname = self.advance().value
                if not self.expect(':'):
                    self._skip_to({',' , '}'})
                    if self.at(','):
                        self.advance()
                    continue
                ftype = self._parse_type()
                if ftype:
                    fields.append({'name': fname, 'type': ftype})
                if self.at(','):
                    self.advance()
                elif not self.at('}') and self.cur().type != 'EOF' and self.cur().value not in self.TOP_LEVEL:
                    self._err(f"Expected ',' or '}}', got '{self.cur().value}'")
                    self._skip_to({',', '}'})
                    if self.at(','):
                        self.advance()
            else:
                self._err(f"Expected field name, got {self.cur().type}('{self.cur().value}')")
                self._skip_to({',', '}'})
                if self.at(','):
                    self.advance()
        self.expect('}')
        return {'type': 'entity', 'name': name, 'fields': fields}

    def _parse_statemachine(self):
        self.advance()
        target = ''
        if self.cur().type == 'IDENT':
            target = self.advance().value
            if self.at('.'):
                self.advance()
                if self.cur().type == 'IDENT':
                    target += '.' + self.advance().value
                else:
                    self._err(f"Expected field name after '.', got {self.cur().type}('{self.cur().value}')")
            else:
                self._err(f"Expected '.' after '{target}', got {self.cur().type}('{self.cur().value}')")
        else:
            self._err(f"Expected statemachine target, got {self.cur().type}('{self.cur().value}')")

        transitions = []
        if not self.expect('{'):
            self._skip_to(self.TOP_LEVEL)
            return {'type': 'statemachine', 'target': target, 'transitions': transitions}

        while not self.at('}') and self.cur().type != 'EOF':
            if self.cur().value in self.TOP_LEVEL:
                self._err(f"Unexpected '{self.cur().value}' inside statemachine '{target}'")
                break
            if self.cur().type == 'IDENT' or self.at('*'):
                src = self.advance().value
                if not self.expect('->'):
                    self._skip_to({'}', '->', 'on'})
                    continue
                dst = ''
                if self.cur().type == 'IDENT':
                    dst = self.advance().value
                else:
                    self._err(f"Expected target state, got {self.cur().type}('{self.cur().value}')")
                if not self.expect('on'):
                    self._skip_to({'}', '->'})
                    continue
                action = ''
                if self.cur().type == 'IDENT':
                    action = self.advance().value
                else:
                    self._err(f"Expected action name, got {self.cur().type}('{self.cur().value}')")
                if dst:
                    transitions.append({'from': src, 'to': dst, 'on': action})
            else:
                self._err(f"Expected transition or '}}', got '{self.cur().value}'")
                self.advance()
        self.expect('}')
        return {'type': 'statemachine', 'target': target, 'transitions': transitions}

    def _parse_rule(self):
        self.advance()
        name = 'unknown'
        if self.cur().type == 'IDENT':
            name = self.advance().value
        else:
            self._err(f"Expected rule name, got {self.cur().type}('{self.cur().value}')")

        target = ''
        if self.at('for'):
            self.advance()
            if self.cur().type == 'IDENT':
                target = self.advance().value
            else:
                self._err(f"Expected entity name after 'for', got {self.cur().type}('{self.cur().value}')")
        else:
            self._err(f"Expected 'for', got {self.cur().type}('{self.cur().value}')")
            self._skip_to({'for', '{'})
            if self.at('for'):
                self.advance()
                if self.cur().type == 'IDENT':
                    target = self.advance().value

        body = []
        if not self.expect('{'):
            self._skip_to(self.TOP_LEVEL)
            return {'type': 'rule', 'name': name, 'target': target, 'body': body}

        depth = 1
        while depth > 0 and self.cur().type != 'EOF':
            if depth == 1 and self.cur().value in self.TOP_LEVEL:
                self._err(f"Unterminated rule '{name}', expected '}}'")
                break
            if self.at('{'):
                depth += 1
            elif self.at('}'):
                depth -= 1
                if depth == 0:
                    self.advance()
                    break
            body.append(self.cur().value)
            self.advance()
        if depth > 0 and self.cur().type == 'EOF':
            self._err(f"Unterminated rule '{name}', expected '}}'")
        return {'type': 'rule', 'name': name, 'target': target, 'body': body}
