SYSTEM_PROMPT = """You are a biomedical research assistant. 
You help generate hypotheses about gene involvement in disease by analyzing disease pathways (KEGG) and gene ontology (GO) data."""

GENE_QUERY_TEMPLATE = """
User Query: {user_query}

Gene: {gene}
Disease Pathways: {pathways}
Direct GO Terms: {go_terms}
Downstream Genes: {downstream_genes}
Downstream Genes' GO Terms: {downstream_go_terms}

Question:
Please answer the user's query in light of the Disease pathways and GO (Gene Ontology) context above.
"""
