from typing import Optional

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.state = {}
        self.transitions = {}

    def load(self):
        for node in self.ast:
            if node['type'] == 'statemachine':
                keys = {node['target'], node['target'].split('.')[0]}
                for t in node['transitions']:
                    for key in keys:
                        self.transitions[(key, t['from'])] = (t['to'], t['on'])

    def fire(self, entity: str, current_state: str, action: str) -> Optional[str]:
        key = (entity, current_state)
        if key in self.transitions:
            to_state, act = self.transitions[key]
            if act == action or act == '*':
                return to_state
        key_wild = (entity, '*')
        if key_wild in self.transitions:
            to_state, act = self.transitions[key_wild]
            if act == action:
                return to_state
        return None

    def run_scenario(self, steps):
        trace = []
        current = {}
        for entity, action in steps:
            state = current.get(entity, 'Available')
            new_state = self.fire(entity, state, action)
            if new_state:
                current[entity] = new_state
                trace.append((entity, state, new_state, action, 'OK'))
            else:
                trace.append((entity, state, state, action, 'FAIL'))
        return trace
