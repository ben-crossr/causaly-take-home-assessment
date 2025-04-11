import pandas as pd
from typing import Set
from app.models import Node, Relationship


def parse_gaf(gaf_path: str, kegg_gene_set: Set[str]) -> tuple[list[Node], list[Relationship]]:
    """
    Parse a GAF file but only keep rows if gene symbol is in the KEGG gene set.
    """
    df = pd.read_csv(gaf_path, sep="\t", comment="!", header=None)

    df = df[df[2].isin(kegg_gene_set)]

    nodes: list[Node] = []
    relationships: list[Relationship] = []

    for _, row in df.iterrows():
        gene_symbol = row[2]
        go_id = row[4]
        go_term_name = row[10] if pd.notnull(row[10]) else go_id

        gene_node_id = f"GENE:{gene_symbol}"
        go_node_id = f"GO:{go_id}"

        nodes.append(Node(id=gene_node_id, name=gene_symbol, type="gene"))
        nodes.append(Node(id=go_node_id, name=go_term_name, type="go_term"))

        relationships.append(Relationship(
            start_node_id=gene_node_id,
            end_node_id=go_node_id,
            type="annotated_with",
            provenance="GO",
            score=None
        ))

    return nodes, relationships
