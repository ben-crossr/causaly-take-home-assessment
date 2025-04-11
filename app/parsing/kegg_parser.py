import xml.etree.ElementTree as ET
from pathlib import Path

from app.models import Node, Relationship


def get_valid_gene_symbol(symbols: list[str], fallback: str) -> str:
    """
    Returns the first symbol in the list that is not all numbers.
    uses a fallback string if no such symbol is found.
    """
    for symbol in symbols:
        if not symbol.isdigit():
            return symbol
    return fallback


def parse_kgml(file_path: str) -> tuple[list[Node], list[Relationship]]:
    """
    Parses a single KGML file for kegg data, and builds nodes and relationships
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    pathway_id = root.attrib.get("name", "unknown").replace("path:", "")
    pathway_title = root.attrib.get("title", "Unknown Pathway")

    nodes: list[Node] = []
    relationships: list[Relationship] = []
    relationship_id_to_gene_ids = {}

    # Create a pathway node
    pathway_node_id = f"PATHWAY:{pathway_id}"
    nodes.append(Node(id=pathway_node_id, name=pathway_title, type="pathway"))

    # Parse all entries
    for entry in root.findall("entry"):
        relationship_id = entry.attrib["id"]
        entry_type = entry.attrib.get("type", "")
        name = entry.attrib.get("name", "")
        graphics = entry.find("graphics")
        label = graphics.attrib.get("name", "") if graphics is not None else name

        if entry_type == "gene":
            gene_ids = [gid.split(":")[-1] for gid in name.strip().split()]
            gene_symbols = [sym.strip() for sym in label.split(",")]

            for i, gid in enumerate(gene_ids):
                gene_symbol = get_valid_gene_symbol(gene_symbols, gid)
                other_ids = [sym for sym in gene_symbols if sym != gene_symbol] if len(gene_symbols) > 1 else None

                node_id = f"GENE:{gene_symbol}"
                nodes.append(Node(
                    id=node_id,
                    name=gene_symbol,
                    type="gene",
                    other_identifiers=other_ids
                ))

                if relationship_id not in relationship_id_to_gene_ids:
                    relationship_id_to_gene_ids[relationship_id] = []
                relationship_id_to_gene_ids[relationship_id].append(node_id)

                relationships.append(Relationship(
                    start_node_id=node_id,
                    end_node_id=pathway_node_id,
                    type="involved_in",
                    provenance="KEGG"
                ))

    # Parse relations
    for relation in root.findall("relation"):
        entry1 = relation.attrib["entry1"]
        entry2 = relation.attrib["entry2"]
        rel_type = relation.attrib.get("type", "")

        if entry1 not in relationship_id_to_gene_ids or entry2 not in relationship_id_to_gene_ids:
            continue

        subtypes = relation.findall("subtype")
        subtypes = [sub.attrib.get("name") for sub in subtypes if sub.attrib.get("name")]

        for source in relationship_id_to_gene_ids[entry1]:
            for target in relationship_id_to_gene_ids[entry2]:
                for subtype in subtypes or [None]:
                    relationships.append(Relationship(
                        start_node_id=source,
                        end_node_id=target,
                        type=rel_type,
                        subtype=subtype,
                        provenance="KEGG"
                    ))

    return nodes, relationships


def parse_all_kgml_in_dir(directory_path: str) -> tuple[list[Node], list[Relationship]]:
    """
    Iterate over all kgml files in the given directory and parses them.
    """
    all_nodes: list[Node] = []
    all_relationships: list[Relationship] = []

    for file in Path(directory_path).glob("*.xml"):
        nodes, relationships = parse_kgml(str(file))
        all_nodes.extend(nodes)
        all_relationships.extend(relationships)

    return all_nodes, all_relationships