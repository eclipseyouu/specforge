import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Set

class StateMachineLayout:
    def __init__(self, states: List[str], edges: List[Tuple[str, str]]):
        self.states = states
        self.edges = edges
        self.pos: Dict[str, List[float]] = {
            s: [random.uniform(-5, 5), random.uniform(-5, 5)] for s in states
        }
        self.area = 100.0
        self.k = math.sqrt(self.area / max(1, len(states)))

    def compute(self, iterations=80):
        t = 10.0
        for _ in range(iterations):
            forces = {s: [0.0, 0.0] for s in self.states}
            for i in self.states:
                for j in self.states:
                    if i == j: continue
                    dx = self.pos[i][0] - self.pos[j][0]
                    dy = self.pos[i][1] - self.pos[j][1]
                    d = max(0.01, math.hypot(dx, dy))
                    f = (self.k * self.k) / d
                    forces[i][0] += (dx / d) * f
                    forces[i][1] += (dy / d) * f
            for u, v in self.edges:
                if u not in self.pos or v not in self.pos: continue
                dx = self.pos[u][0] - self.pos[v][0]
                dy = self.pos[u][1] - self.pos[v][1]
                d = max(0.01, math.hypot(dx, dy))
                f = (d * d) / self.k
                forces[u][0] -= (dx / d) * f
                forces[u][1] -= (dy / d) * f
                forces[v][0] += (dx / d) * f
                forces[v][1] += (dy / d) * f
            for s in self.states:
                dx, dy = forces[s]
                d = max(0.01, math.hypot(dx, dy))
                self.pos[s][0] += (dx / d) * min(d, t)
                self.pos[s][1] += (dy / d) * min(d, t)
            t *= 0.95

    def to_svg(self, unreachable: Set[str] = None, filename="sm.svg"):
        self.compute()
        unreachable = unreachable or set()
        w, h = 600, 400
        ox, oy = w / 2, h / 2
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">']
        for u, v in self.edges:
            if u not in self.pos or v not in self.pos: continue
            x1, y1 = self.pos[u]; x2, y2 = self.pos[v]
            lines.append(f'<line x1="{ox+x1*20}" y1="{oy+y1*20}" x2="{ox+x2*20}" y2="{oy+y2*20}" stroke="black"/>')
        for s, (x, y) in self.pos.items():
            color = "red" if s in unreachable else "lightblue"
            lines.append(f'<circle cx="{ox+x*20}" cy="{oy+y*20}" r="20" fill="{color}" stroke="black"/>')
            lines.append(f'<text x="{ox+x*20}" y="{oy+y*20+5}" text-anchor="middle" font-size="10">{s}</text>')
        lines.append('</svg>')
        Path(filename).write_text('\n'.join(lines))
        return filename
