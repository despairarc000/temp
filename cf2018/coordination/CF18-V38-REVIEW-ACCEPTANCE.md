# v3.8 report review acceptance

Base d04cfe9a1e54f8c5e01e5839476e84beb834468a,2026-10-31.
Read actual uploaded report, hash it; do not replace v3.8 with old v1.6 summaries.
Separate phone observations, probe classifications and native control results.
Preserve confirmed progression; no guessed reply or another automatic phone run.
Test compression/encryption independence only with synthetic data and pinned
original native helper. Never create keys; encrypted no-key controls must fail.
If report redaction/classifier source prevents operation identification, state
that exact evidence gap rather than declaring encryption or repeating scans.
