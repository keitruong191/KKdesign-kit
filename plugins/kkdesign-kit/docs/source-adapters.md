# Source adapters

`kkdesign_sources.py` reads design-system inputs without executing source content or changing a source checkout. It exports:

- `scan_sources(config, base) -> dict`: scan declarations in order and return a normalized source registry. `base` is the directory containing the user-supplied source configuration.
- `validate_registry(registry) -> list[str]`: return integrity diagnostics (an empty list means the registry's structural checks pass; it is not proof of design correctness or approval).

The runtime uses Python 3.9+ standard-library APIs only. A declaration has an `id` slug, `provider` (`local`, `git`, or `figma`), and `location`. Git may additionally specify `ref` and `subdir`; Figma may specify `nodeIds`. Local and Git locations are project-relative paths from `base`, never absolute paths. Git defaults to `HEAD` and the repository root. A subdirectory selects files at that committed tree path.

## Supported local/Git file formats

A source directory/tree contains `ds.json`, `tokens.json`, or both (but they may not both provide tokens). `ds.json` is the normalized interchange format:

```json
{
  "schemaVersion": "1.0.0",
  "tokens": [{"id": "color.brand", "name": "Brand", "data": {"$type": "color", "$value": "#2457A6"}}],
  "styles": [], "components": [], "variants": [], "modes": []
}
```

All five arrays are optional and default to empty. A category present with `[]` has `empty` coverage; an absent category has `undeclared` coverage. Each row requires a unique category-local `id`, a non-empty `name`, and an object `data`. Adapter output retains only these fields plus its `sourceId`; arbitrary source metadata is not propagated.

`tokens.json` accepts nested DTCG-style token groups and tokens: a token has `$value` and either its own `$type` or an inherited group `$type`, and may also contain `$description` or `$extensions`. Token IDs are dot-joined group/key paths; collisions caused by flattening are rejected. Names are the final path segment, and token data retains the effective type and explicitly supported DTCG fields. Only an explicit top-level `$modes` object produces mode assets; the adapter does not infer modes from names or values. DTCG styles, components, and variants are not inferred from tokens.

Local source directories reject symlink path components and symlink source files. Paths cannot be absolute or traverse outside `base`. Git first resolves the selected ref to an immutable commit, then uses argument-vector `git show` reads from that exact commit with inherited `GIT_*` variables removed. It does not check out files or run source scripts/hooks. A Git source is still local and must remain under `base`.

Example Git declaration (the repository must already exist under the config
directory; cloning/fetching/authentication is an explicit external step):

```json
{"sources":[{"id":"committed-ds","provider":"git","location":"repository","ref":"HEAD","subdir":"tokens"}]}
```

This reads committed `tokens/ds.json` and/or `tokens/tokens.json`. Dirty working
files are ignored. Git revision changes are ordinary refreshes; changing provider,
repository location or selected subdirectory needs an explicit migration plan.

Normalized asset data rejects credential-like object keys, credential-bearing URLs, and common absolute machine-path forms. Diagnostics identify the field path but never echo values. This is a best-effort persistence guard, not exhaustive secret detection; review input exports before storing them.

## Figma

Figma locations must be credential-free HTTPS URLs in the `www.figma.com/design/KEY/title` or `/file/KEY/title` form. Reads use the REST file and local-variable GET endpoints with an eight-second timeout and a 10 MiB per-response ceiling. Set `FIGMA_ACCESS_TOKEN` in the process environment; the token is never put in the registry, source location, or error text. `nodeIds` restricts the file request, subject to Figma's inclusion of ancestors and dependencies. Native component/set identities, property definitions and observed variant properties are retained. File style maps provide metadata, not resolved style definitions. Inaccessible variables produce `unavailable` coverage and explicit limitations.

The [file endpoint](https://developers.figma.com/docs/rest-api/file-endpoints/) is not a guaranteed exhaustive published-library inventory. Its components, variants and styles are reported as partial metadata. The [local variables endpoint](https://developers.figma.com/docs/rest-api/variables-endpoints/) requires an eligible Enterprise full member and `file_variables:read` permission. Variable modes preserve both native collection ID and mode ID; the composite registry identity `<collectionId>/<modeId>` avoids collisions across collections without inventing a Figma import key. Provider metadata never proves importability or live rendering.

### Offline Figma captures

For deterministic/offline ingestion, a `figma` declaration keeps its canonical Figma URL in `location` and may specify a project-relative `capture` JSON file. The file has `schemaVersion: "1.0.0"`, `kind: "figma-capture"`, native `fileKey`, optional `version`/`lastModified`, native `document`, arrays `components`, `componentSets`, and `styles`, and optional `variables` containing `variables` and `variableCollections` as arrays or ID-keyed objects. Native camelCase and snake_case IDs are accepted. Optional `captureCounts`, `missingNodeIds`, and `unavailableProperties` preserve evidence of incomplete capture: short inventories, unavailable properties, and missing nodes are marked `partial`, missing variables `unavailable`, omitted categories `undeclared`, and explicitly empty arrays `empty`. Records preserve only whitelisted native fields as asset data; asset IDs are selected from native `node_id`, `nodeId`, `id`, or `key` fields (no substitute IDs are generated). Missing `version` is stated as `unknown` and recorded as a limitation; the canonical file content hash remains available. Captures are read-only inputs and must themselves be produced through an authorized workflow. `examples/sources/figma-capture.json` is fabricated public test data, not an export.

The bundled `scripts/figma_capture.js` is a static read-only Plugin API exporter.
Set `FIGMA_NODE_IDS` to the explicitly authorized source nodes before executing it
in an authenticated Figma context. It makes no document mutations. Styles and
variables are capped at two each by default for bounded bridge responses; change
the explicit limits only when the transport can return the complete result.
Capture counts, unavailable properties, missing nodes and serialization limits
remain visible. Capture ingestion retains supported native style values and
component variant/property definitions and verifies `fileKey` against the
declared URL. REST revision is unknown when the Plugin API cannot expose it;
content hashes are not fabricated REST versions. Private captures stay outside
this repository; only the synthetic capture example is bundled.

The token reader supports the documented subset of the
[DTCG format](https://www.designtokens.org/TR/2025.10/format/), not arbitrary
Style Dictionary/JS/CSS/Swift source execution. Aliases are retained as authored,
not resolved into invented values. `$modes` is an explicit kit extension, not a
claim that the DTCG format defines a global mode map.

## Registry and precedence

The result has `schemaVersion: "1.0.0"`, `kind: "source-registry"`, five merged asset lists, ordered per-source snapshots, `precedence: "later-source-wins"`, and `overrides`. Each snapshot contains `id`, `provider`, credential-free `location`, provider revision, SHA-256 `contentHash`, UTC `capturedAt`, category `coverage`, `limitations`, and its own normalized assets. Asset identity is the source's native ID (Figma) or declared logical ID/path (local interchange/DTCG); same identity in a category is overlaid by the later source. Each overlay adds an `{category,id,fromSourceId,toSourceId}` record. Do not use `capturedAt` to compare source identity or determine whether design inputs changed.
Coverage values are `available`, `empty`, `partial`, `unavailable`, or `undeclared`; `partial` and `unavailable` always have limitations explaining the incomplete source. Snapshot integrity includes typed provenance, per-source asset ownership, category-local ID uniqueness, and exact recomputation of merged assets and overrides from ordered snapshots.

Example inputs in `examples/sources/` are entirely synthetic. They demonstrate local inputs and a later-source token override; they contain no private Figma data or credentials.
