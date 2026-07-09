"""Graph Analytics (Module 4) — NetworkX over the wikilink graph.

The vault's [[wikilinks]] ARE the knowledge graph; this extracts them into a
directed graph and computes things Obsidian can't: centrality (what concept is
most connected?), pathfinding (how does A connect to B?), and neighborhoods.
No graph DB — at this scale NetworkX over parsed links is the right tool.
"""
from __future__ import annotations
import networkx as nx

from vault import Note, load_vault


def build_graph(notes: list[Note] | None = None) -> nx.DiGraph:
    notes = notes or load_vault()
    g = nx.DiGraph()
    for n in notes:
        if n.type in ("template",) or "/Reviews/" in f"/{n.rel_path}":
            continue
        g.add_node(n.filename, type=n.type, title=n.title,
                   confidence=n.confidence_state, freshness=n.freshness)
    for n in notes:
        if n.type in ("template",) or "/Reviews/" in f"/{n.rel_path}":
            continue
        for target in n.outlinks:
            if not target.startswith("__UNRESOLVED__") and g.has_node(target):
                g.add_edge(n.filename, target)
    return g


def central(notes: list[Note] | None = None, k: int = 12) -> list[tuple[str, float]]:
    g = build_graph(notes)
    if g.number_of_nodes() == 0:
        return []
    # undirected degree centrality reads best as "how connected is this idea"
    dc = nx.degree_centrality(g.to_undirected())
    return sorted(dc.items(), key=lambda x: -x[1])[:k]


def path(a: str, b: str, notes: list[Note] | None = None) -> list[str] | None:
    g = build_graph(notes).to_undirected()
    a, b = _resolve(g, a), _resolve(g, b)
    if a is None or b is None:
        return None
    try:
        return nx.shortest_path(g, a, b)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def neighbors(node: str, notes: list[Note] | None = None, radius: int = 1) -> list[str]:
    g = build_graph(notes).to_undirected()
    node = _resolve(g, node)
    if node is None:
        return []
    ego = nx.ego_graph(g, node, radius=radius)
    return [n for n in ego.nodes if n != node]


def clusters(notes: list[Note] | None = None) -> list[list[str]]:
    g = build_graph(notes).to_undirected()
    return [sorted(c) for c in nx.connected_components(g)]


def _resolve(g: nx.Graph, name: str) -> str | None:
    if g.has_node(name):
        return name
    low = name.lower()
    for n in g.nodes:
        if n.lower() == low or low in n.lower():
            return n
    return None


def summary(notes: list[Note] | None = None) -> dict:
    g = build_graph(notes)
    ug = g.to_undirected()
    comps = list(nx.connected_components(ug))
    isolates = list(nx.isolates(ug))
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "components": len(comps),
        "largest_component": max((len(c) for c in comps), default=0),
        "isolates": len(isolates),
        "top_central": central(notes, k=10),
    }


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "path":
        p = path(args[1], args[2])
        print(" → ".join(p) if p else "no path found")
    elif len(args) >= 2 and args[0] == "neighbors":
        for n in neighbors(args[1], radius=int(args[2]) if len(args) > 2 else 1):
            print(f"  {n}")
    else:
        s = summary()
        print(f"Graph: {s['nodes']} nodes, {s['edges']} edges, "
              f"{s['components']} component(s), largest={s['largest_component']}, "
              f"{s['isolates']} isolate(s)")
        print("\nMost central ideas (most connected):")
        for name, score in s["top_central"]:
            print(f"  {score:.3f}  {name}")
