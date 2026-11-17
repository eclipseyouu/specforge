import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

class Lexer:
    PATTERNS = [
        ('COMMENT', r'//[^\n]*'),
        ('WS', r'\s+'),
        ('ARROW', r'->'),
        ('EQ', r'=='),
        ('NEQ', r'!='),
        ('KEYWORD', r'\b(?:entity|statemachine|rule|if|then|else|end|pre|post|invariant|on|let|for|Enum|UUID|Integer|Decimal|String|Text)\b'),
        ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUMBER', r'\d+(?:\.\d+)?'),
        ('STRING', r'"[^"]*"'),
        ('SYMBOL', r'[{}().,=+\-*<>@:;]'),
    ]
    MASTER = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in PATTERNS))

    def __init__(self, text: str):
        self.tokens: List[Token] = []
        self._tokenize(text)

    def _tokenize(self, text: str):
        line, line_start = 1, 0
        for m in self.MASTER.finditer(text):
            kind = m.lastgroup
            val = m.group()
            if kind == 'WS':
                if '\n' in val:
                    line += 1
                    line_start = m.end()
                continue
            if kind == 'COMMENT':
                continue
            col = m.start() - line_start + 1
            self.tokens.append(Token(kind, val, line, col))
        self.tokens.append(Token('EOF', '', line, 1))
