from app.agent.tools import (
    get_gene_pathways,
    get_go_terms,
    get_downstream_genes,
    get_downstream_go_terms
)
from app.agent.prompts import SYSTEM_PROMPT, GENE_QUERY_TEMPLATE
from app.utils.openai_client import generate_response


class PlanningAgent:
    def __init__(self, graph):
        self.graph = graph
        self.tools = {
            "get_pathways": {
                "func": get_gene_pathways,
                "description": "Identify disease pathways the gene is involved in (helps answers disease and pathway questions)."
            },
            "get_go_terms": {
                "func": get_go_terms,
                "description": "Identify Gene Ontology terms (processes, functions, components) linked to the gene."
            },
            "get_downstream_genes": {
                "func": get_downstream_genes,
                "description": "Identify genes that are downstream in the KEGG causal graph."
            },
            "get_downstream_go_terms": {
                "func": get_downstream_go_terms,  # meta-tool
                "description": "Identify downstream genes in KEGG, then retrieve GO terms for each to get downstreadm GO terms."
            },
        }

    def plan_and_execute(self, query: str) -> str:
        """
        Respond to a question by planning steps, executing them, and summarizing the results in a final response.
        """
        # Step 1: Extract gene symbol from user query
        gene = self._extract_gene(query)
        if gene == "<NO_GENE>":
            raise ValueError("Could not extract a HGNC gene symbol from the query.")

        # Step 2: Decide which tools to run
        tool_plan = self._choose_tools(query)

        # Step 3: Execute the selected tools
        context = {"gene": gene}
        for tool_name in tool_plan:
            tool = self.tools.get(tool_name)
            if tool:
                result = tool["func"](self.graph, gene)
                context[tool_name] = result

        # Step 4: reformat get_downstream_go_terms if present
        downstream_go_summary = "None"
        if "get_downstream_go_terms" in context:
            downstream_go_data = context["get_downstream_go_terms"]
            downstream_go_summary = _format_downstream_go_dict(downstream_go_data)

        # Step 5: Create the final prompt, incorporating the user’s original query
        prompt = GENE_QUERY_TEMPLATE.format(
            user_query=query,
            gene=gene,
            pathways=", ".join(context.get("get_pathways", [])) or "None",
            go_terms=", ".join(context.get("get_go_terms", [])) or "None",
            downstream_genes=", ".join(context.get("get_downstream_genes", [])) or "None",
            downstream_go_terms=downstream_go_summary
        )

        # Step 6: use LLM of choice to generate final response to user query.
        return generate_response(prompt=prompt, instructions=SYSTEM_PROMPT)

    @staticmethod
    def _extract_gene(query: str) -> str:
        """
        Uses an LLM to extract a gene symbol from the user's question.
        Returns <NO_GENE> if no valid gene is found.
        """
        instruction = (
            "You are an assistant that extracts gene symbols from user questions. "
            "Reply with the gene symbol only. If none is found, reply with <NO_GENE>."
        )
        response = generate_response(
            prompt=query,
            instructions=instruction,
        )
        gene_symbol = response.strip()
        if gene_symbol == "<NO_GENE>":
            return "<NO_GENE>"
        return f"GENE:{gene_symbol}"

    def _choose_tools(self, query: str) -> list[str]:
        """
        Decide which tools are required to answer user's query.
        Returns a list of tool names.
        """
        tool_list = "\n".join([
            f"- {name}: {spec['description']}" for name, spec in self.tools.items()
        ])

        instruction = (
            "You are a planner that chooses which of the following tools are useful "
            "to answer the user's biomedical question.\n"
            f"Available tools:\n{tool_list}\n\n"
            "Reply with a comma-separated list of tool names (no explanation).\n"
            "If none are useful, reply with an empty string."
        )

        response = generate_response(
            prompt=query,
            instructions=instruction,
        )
        return [tool.strip() for tool in response.strip().split(",") if tool.strip()]


def _format_downstream_go_dict(data: dict[str, list[str]]) -> str:
    """
    Convert a dict of downstream_gene -> list of GO terms
    """
    if not data:
        return "None"

    lines = []
    for gene, go_terms in data.items():
        if go_terms:
            gos_str = ", ".join(go_terms)
            lines.append(f"{gene}: {gos_str}")
        else:
            lines.append(f"{gene}: No GO terms")

    return "; ".join(lines)
