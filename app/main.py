import os
import networkx as nx

from app.agent.planner import PlanningAgent
from app.graph.builder import build_graph
from app.parsing.kegg_parser import parse_all_kgml_in_dir
from app.parsing.go_parser import parse_gaf
from app.models import Node, Relationship


def load_graph(
    kegg_dir: str = None,
    go_file: str = None,
) -> nx.DiGraph:
    """
        - parse KEGG & GO data and build a fresh graph.
       - Filter GO to include only genes present in KEGG data.
    """
    all_nodes: list[Node] = []
    all_rels: list[Relationship] = []

    #  Parse KEGG data
    kegg_nodes, kegg_relationships = [], []
    if kegg_dir and os.path.isdir(kegg_dir):
        kegg_nodes, kegg_relationships = parse_all_kgml_in_dir(kegg_dir)
        all_nodes.extend(kegg_nodes)
        all_rels.extend(kegg_relationships)
    else:
        print("No valid KEGG directory found.")

    # Get all the gene symbols from the KEGG data
    kegg_gene_set = {
        node.name for node in kegg_nodes if node.type == "gene"
    }

    # 2) Parse GO (GAF) data and filter by KEGG genes
    go_nodes, go_relationships = [], []
    if go_file and os.path.isfile(go_file):
        go_nodes, go_relationships = parse_gaf(go_file, kegg_gene_set)
        all_nodes.extend(go_nodes)
        all_rels.extend(go_relationships)
    else:
        print("No valid GO file found.")

    return build_graph(all_nodes, all_rels)



def handle_query(query: str, graph: nx.DiGraph) -> str:
    """
    Takes a user query and the populated graph,
    uses the PlanningAgent to plan tool usage, use tools and return final LLM response
    """
    agent = PlanningAgent(graph)
    return agent.plan_and_execute(query)


if __name__ == "__main__":
    # Example usage: (modify here).
    kegg_dir = "../data/KGML"
    go_file = "../data/GO/goa_human.gaf"

    graph = load_graph(
        kegg_dir=kegg_dir,
        go_file=go_file,
    )

    # user_query = "What are the downstream impacts of gene INS in Type II diabetes and which GO terms are relevant?"
    user_query = "What diseases is gene INS associated with?"
    answer = handle_query(user_query, graph)

    print("Response:\n", answer)
