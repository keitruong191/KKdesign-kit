# KKdesign-kit contributor contract

This repository contains an installable skill and its shared project contracts.
Keep command availability and external-tool requirements accurate.
Keep the shared contracts independent of Figma, Git hosting, a particular DS, and local memory tools.
Use Python 3.9+ and `requirements.txt`. Run `python -m unittest discover -s tests -v` after core changes.
Keep all committed examples synthetic. Do not add customer registries, private Figma IDs, product evidence, credentials, local machine paths, or copied upstream binaries.
Do not infer native behavior or human approval from a schema check.
Codex and Claude Code consume the same project data; harness discovery and
installation are handled by the installer, and hooks remain separate and opt-in.
