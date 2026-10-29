# Graphify — explicit dependency and traceability graph

**ACTIVE.** Graph edges are documented by Markdown links and curated `edges.tsv` metadata. Run `python tools/knowledge.py graph`; use `--output knowledge-system/graphify/RELATIONSHIPS.md` for a checked-in snapshot if desired.

- `doc-link`: validated relative Markdown link.
- `evidence`: claim → capture/native observation and its provenance.
- `blocks`: failed condition → milestone.
- `depends-on`: decision/task → prerequisite.
- `tests`: mechanism → specific acceptance evidence.

Graphify never guesses edges from similar titles. Add new manual relationships to [edges.tsv](edges.tsv), label hypothesis separately in Vault. If a referenced node is removed, `doctor` fails. `graph` and `route` are stdlib-only offline tools.
