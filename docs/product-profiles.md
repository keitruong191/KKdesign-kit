# Product profiles and authority

Product profiles are scoped project records, not DS defaults. DS scanning alone cannot establish a product's users, permissions, supported capabilities or current release behavior.

Inputs by topic:

1. Existing PRODUCT.md, explicit task requirements and confirmed product decisions: purpose, users, terminology, constraints.
2. PRDs and requirement records: workflows, capabilities and intended behavior. Separate approved-but-unimplemented requirements from shipped observations.
3. The designated Figma instance or trustworthy current captures: incumbent presentation, modes, typography and deliberate overrides.
4. Source/configuration/runtime: technical constraints, window behavior, actual interaction evidence.
5. DS: component/token identities and values, not product capability.
6. Scoped lessons: recurring pitfalls and verification requirements.

Every decision records `status` (`confirmed`, `observed`, `inferred`, `open`, `superseded`), `scope`, source IDs and `recheckWhen`. Local sources can pin SHA-256; remote sources pin a known revision where available and never invent one. `confirmed` and `observed` need evidence. An observation is not automatically owner approval.

Profile source locations are relative to the project root. Lesson evidence is relative to `design/`; task evidence is relative to the task folder. Missing context remains open. Do not convert another platform's behavior, a DS example size or one dialog into a universal default.

B2 init discovers and reuses existing product context, drafts profiles from explicit evidence and leaves unknown facts open. See [project kits](project-kits.md) for the context input, per-platform selection and review/apply lifecycle. Refresh preserves existing profiles. Surface modes belong to the surface/task, not a product-wide mode. macOS has its own profile; it is not treated as iOS or Android.
