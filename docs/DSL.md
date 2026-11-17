# SpecForge DSL

## Грамматика (EBNF)
program   := (annotation | entity | statemachine | rule)*
entity    := 'entity' IDENT '{' field (',' field)* '}'
field     := IDENT ':' type
type      := 'UUID' | 'Integer' | 'Decimal' | 'String' | 'Text' | 'Enum' '(' IDENT (',' IDENT)* ')'
statemachine := 'statemachine' IDENT '.' IDENT '{' transition* '}'
transition   := (IDENT | '*') '->' IDENT 'on' IDENT
rule      := 'rule' IDENT 'for' IDENT '{' stmt* '}'
stmt      := let_stmt | if_stmt | invariant
annotation := '@' IDENT '(' IDENT (',' IDENT)* ')'

## Семантика
- entity описывает структуру данных
- statemachine описывает автомат состояний
- rule описывает бизнес-правило с инвариантами
- @req(...) связывает узел с требованиями

## Пример
См. examples/techvault.spec
