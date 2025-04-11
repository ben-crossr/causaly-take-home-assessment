## Ben Vozza's Take Home Assessment for Causaly

#### More details (such as limitations/improvements) found in the pdf submitted alongside the repo.

#### This README.md is one of the improvements to make.

#### This repository demonstrates a workflow that:
- Parses KEGG KGML files to extract disease- and pathway-related gene relationships.
- Parses GO (Gene Ontology) data, filtered by genes present in KEGG.
- Builds a knowledge graph using NetworkX.
- Implements an LLM-powered agentic system to generate hypotheses about gene involvement in diseases based on KEGG + GO data.

### How to run

- Install requirements: 
`poetry install`
- Prepare your data:
  - Place KGML (.xml) files in `data/KGML`
  - Place goa_human.gaf file in `data/GO`
- Set your OpenAI API key:
`export OPENAI_API_KEY=xxxxx` or define it in .env.
- In `app/main.py`, edit the `user_query` variable to any question about a gene.
```python
user_query = "What diseases is gene INS associated with?"
```
- run entrypoint in app/main.py