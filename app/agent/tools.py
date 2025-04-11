from typing import List
import networkx as nx


def get_gene_pathways(graph: nx.DiGraph, gene_id: str) -> List[str]:
    """Identify biological pathways the gene is involved in."""
    return [
        target for target in graph.successors(gene_id)
        if graph.nodes[target]["type"] == "pathway"
    ]


def get_go_terms(graph: nx.DiGraph, gene_id: str) -> List[str]:
    """Retrieve GO terms linked to the gene."""
    return [
        target for target in graph.successors(gene_id)
        if graph.nodes[target]["type"] == "go_term"
    ]


def get_downstream_genes(graph: nx.DiGraph, gene_id: str, depth: int = 2) -> List[str]:
    """Find genes that are downstream of the gene based on KEGG relationships."""
    paths = nx.single_source_shortest_path_length(graph, source=gene_id, cutoff=depth)
    return [
        node for node in paths
        if graph.nodes[node]["type"] == "gene" and node != gene_id
    ]


def get_downstream_go_terms(graph: nx.DiGraph, gene_id: str, depth: int = 2) -> dict[str, list[str]]:
    """
    Find genes downstream of gene_id using KEGG relationships
    then gets their GO terms. Returns a dict: downstream_gene_id -> list of GO terms.
    """
    downstream_genes = get_downstream_genes(graph, gene_id, depth=depth)
    result = {}
    for downstream_gene in downstream_genes:
        go_terms = get_go_terms(graph, downstream_gene)
        result[downstream_gene] = go_terms

    return result