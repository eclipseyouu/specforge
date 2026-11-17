from specforge.trace import TraceabilityGraph

def test_minimal_impact():
    g = TraceabilityGraph()
    for i in range(10):
        g.add_node(f"R-{i:02d}", 'req', f"req {i}")
    for i in range(20):
        tid = f"T-{i:02d}"
        g.add_node(tid, 'test', f"test {i}")
        g.add_link(f"R-{i % 10:02d}", tid)
        if i % 3 == 0:
            g.add_link(f"R-{(i+1) % 10:02d}", tid)

    affected = g.get_impact_set({"R-05"})
    for t in affected:
        assert t.startswith("T-")

    g.add_node("R-99", 'req', "orphan")
    assert g.get_impact_set({"R-99"}) == set()
