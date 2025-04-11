import networkx as nx

from app.models import Node, Relationship


def build_graph(nodes: list[Node], relationships: list[Relationship]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for node in nodes:
        graph.add_node(node.id, **node.model_dump())

    for rel in relationships:
        graph.add_edge(rel.start_node_id, rel.end_node_id, **rel.model_dump())

    return graph
