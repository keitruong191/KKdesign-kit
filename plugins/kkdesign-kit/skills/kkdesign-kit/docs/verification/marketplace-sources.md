# WWA-11 persistent marketplace source verification

This record identifies the final review snapshot after publication; the canonical
build's copy precedes the evidence-only commit which fills in the measured IDs.
Use [source provenance](../marketplace-sources.md) and the provider guides for
review-channel commands and boundaries. The review branches are mutable and are
not represented as immutable pins. Authenticated menu/Setup, human consent and
non-dev usability, production approval and unmeasured platforms remain pending.

The opt-in remote probe is `scripts/smoke_remote_marketplaces.py`. It requires
both installed provider CLIs, Python 3.9+ with requirements.txt, approved network
access and a fresh output outside source. Pass the recorded Codex and Claude
refs with `--codex-ref` and `--claude-ref`, plus `--output`. It uses separate
clean homes/profiles, unrelated CWDs with spaces, native remote clones, fresh
native discovery without a user/model prompt, direct installed-cache Setup and
helpers without PATH Python, then native removal and preservation checks.
Its consent flag applies only to its disposable synthetic runtime provisioning;
this does not measure an agent explaining consent to a person. Raw logs are
private outside source and must not be committed.
