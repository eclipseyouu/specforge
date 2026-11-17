import hashlib
from collections import defaultdict, deque
from typing import Set, Dict

class TraceabilityGraph:
    def __init__(self):
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self.hashes: Dict[str, str] = {}
        self.nodes: Dict[str, Dict] = {}

    def add_node(self, nid: str, ntype: str, content: str = ""):
        self.nodes[nid] = {'type': ntype, 'content': content}
        self.hashes[nid] = hashlib.sha256(content.encode()).hexdigest()

    def add_link(self, src: str, dst: str):
        self.edges[src].add(dst)

    def get_impact_set(self, changed: Set[str]) -> Set[str]:
        affected = set()
        queue = deque(changed)
        visited = set(changed)
        while queue:
            cur = queue.popleft()
            for nxt in self.edges[cur]:
                if nxt not in visited:
                    visited.add(nxt)
                    if nxt.startswith('T-'):
                        affected.add(nxt)
                    queue.append(nxt)
        return affected

    def incremental_update(self, nid: str, new_content: str) -> Set[str]:
        old = self.hashes.get(nid, '')
        new = hashlib.sha256(new_content.encode()).hexdigest()
        if old == new:
            return set()
        self.hashes[nid] = new
        return self.get_impact_set({nid})

    def coverage_matrix(self) -> Dict:
        reqs = {n for n, d in self.nodes.items() if d['type'] == 'req'}
        specs = {n for n, d in self.nodes.items() if d['type'] == 'spec'}
        tests = {n for n, d in self.nodes.items() if d['type'] == 'test'}
        covered_reqs = {r for r in reqs if any(self.edges[r])}
        covered_specs = {s for s in specs if any(self.edges[s])}
        return {
            'reqs_without_tests': reqs - covered_reqs,
            'dead_specs': specs - covered_specs,
            'tests_without_reqs': tests - {t for t in tests if any(t in self.edges[s] for s in specs)},
        }
