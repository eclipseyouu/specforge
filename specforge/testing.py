import random
from hypothesis import strategies as st
from hypothesis.strategies import composite

@composite
def st_dsl_program(draw):
    entities = draw(st.lists(st.sampled_from(['Equipment', 'Employee', 'Reservation']), min_size=1, max_size=2))
    states = ['Available', 'Reserved', 'Issued', 'Maintenance']
    n = draw(st.integers(1, 4))
    trs = []
    for _ in range(n):
        s1 = draw(st.sampled_from(states))
        s2 = draw(st.sampled_from(states))
        trs.append(f"{s1} -> {s2} on act()")
    prog = f"entity {entities[0]} {{ status: Enum({','.join(states)}) }}\n"
    prog += f"statemachine {entities[0]}.status {{\n" + "\n".join(trs) + "\n}"
    return prog

@composite
def st_invalid_transition(draw):
    current = draw(st.sampled_from(['Maintenance', 'Retired']))
    target = draw(st.sampled_from(['Available', 'Reserved']))
    return {"from": current, "to": target, "should_fail": True}

@composite
def st_cr(draw):
    n = draw(st.integers(1, 3))
    changes = []
    for _ in range(n):
        changes.append({
            "type": draw(st.sampled_from(['rule_threshold', 'state_transition', 'entity_field'])),
            "target": draw(st.text(min_size=1, max_size=8)),
            "value": draw(st.integers(0, 100))
        })
    return changes

class TestRunner:
    def __init__(self, interpreter, seed=42):
        self.interp = interpreter
        self.rng = random.Random(seed)

    def run_scenario(self, steps):
        return self.interp.run_scenario(steps)

    def run_all(self, tests):
        results = []
        for t in tests:
            trace = self.run_scenario(t['steps'])
            status = 'PASS' if all(r[4] == 'OK' for r in trace) else 'FAIL'
            results.append({'id': t['id'], 'status': status, 'trace': trace})
        return results
