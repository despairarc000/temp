# Owner's test setup

Original game + original OBB -> PCAPdroid VPN, CrossFire selected and Termux EXCLUDED -> SOCKS5 127.0.0.1:1080 in Termux -> local fake server127.0.0.1:8080/8085 -> sanitized TXT in Downloads.

Termux runs BOTH redirector and fake server. Stop old probes before starting another; one VPN/probe. Current diagnostics divert only known game IP AND port, preserve non-target passthrough, use unique IDs and four accepted sessions. Default offline tests open no live game listener; phone opt-in is manual.

Latest V3.8.1 test already completed. Do not ask owner to repeat it. [Full setup](../../cf2018/coordination/CURRENT_HANDOFF.md), [existing kit steps](../../cf2018/coordination/V381_TERMUX_STEPS.txt). A scheduled/cloud run does not provide a phone or shared disk.

Owner update preference (2026-11-01): use **Progress made:** and **Next: research/test** so research, offline checks and phone milestones are easy to follow; recommend an intelligence level at the end of each turn. Latest optional test: [one second-service ACK](../../cf2018/knowledge-system/vault/research/SECOND_SERVICE_ACK_EXPERIMENT.md).
