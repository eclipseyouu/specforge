from typing import List, Dict, Set
from .parser import Diagnostic

class SemanticAnalyzer:
    def __init__(self, ast: List[Dict]):
        self.ast = ast
        self.errors: List[Diagnostic] = []
        self.entities: Dict[str, Dict] = {}
        self.machines: Dict[str, Dict] = {}

    def analyze(self) -> List[Diagnostic]:
        for node in self.ast:
            if node['type'] == 'entity':
                self.entities[node['name']] = node
            elif node['type'] == 'statemachine':
                self.machines[node['target']] = node

        for node in self.ast:
            if node['type'] == 'statemachine':
                self._check_sm(node)
        return self.errors

    def _check_sm(self, sm: Dict):
        entity_name = sm['target'].split('.')[0]
        if entity_name not in self.entities:
            self.errors.append(Diagnostic(0, 0, f"Unknown entity '{entity_name}' in statemachine"))
        states: Set[str] = set()
        for t in sm['transitions']:
            if t['from'] != '*': states.add(t['from'])
            states.add(t['to'])
        reachable = self._bfs(sm)
        for s in states:
            if s not in reachable:
                self.errors.append(Diagnostic(0, 0, f"Unreachable state '{s}' in {sm['target']}"))

    def _bfs(self, sm: Dict) -> Set[str]:
        if not sm['transitions']: return set()
        start = sm['transitions'][0]['from']
        if start == '*': start = sm['transitions'][0]['to']
        visited = {start}
        queue = [start]
        adj = {}
        for t in sm['transitions']:
            adj.setdefault(t['from'], set()).add(t['to'])
            if t['from'] == '*':
                for s in {x['to'] for x in sm['transitions']}:
                    adj.setdefault(s, set()).add(t['to'])
        while queue:
            cur = queue.pop(0)
            for nxt in adj.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return visited
