# Review lenses
> Selectively adapted and modified by KKdesign-kit from Impeccable 4.8.0. See [attribution and license](../../docs/review-attribution.md).

Use only lenses relevant to the scoped task. A checklist is a prompt to inspect, not a certification.

## Product and design-system references

- Identify the source and revision of each relevant product reference (behavior, audience, terms, commitments) and design-system source (tokens, text styles, components, variants, modes). Keep their authority distinct.
- Confirm that each visual reference is for the actual platform, surface, and state. A product image or iPhone mockup does not authorize macOS interaction patterns.
- Inspect the component instance and its selected variant, properties, overrides, and bindings. Look for detached/local values that visually mimic a canonical style but no longer track system updates.
- Compare all required theme/mode and component states, not only the default/hero frame. Record missing source evidence instead of guessing.

## Hierarchy and cognitive load

- Ask what users should notice first, next, and last; inspect whether scale, position, contrast, grouping, and wording support that order.
- Count simultaneous decisions and visibly competing actions. Check whether related choices are grouped and whether advanced/rare actions crowd the main task.
- Trace recognition versus recall: are labels, selected values, progress, constraints and consequences visible at the point of choice?
- Follow the full task end-to-end, including handoffs, interruptions and return. Identify context the user must retain mentally.

## Copy and recovery

- Read primary and secondary actions in sequence, including destructive and irreversible actions. Are outcomes explicit and differentiated?
- For validation/failure, locate the cause, affected input, preserved work, corrective action, retry and escalation route. Verify that recovery is possible without starting over.
- Check empty, loading, partial, success, permission-denied, unavailable and offline messages only where the experience actually has those states.
- Treat factual claims and product promises as constraints: recommend wording changes, but do not invent product behavior or replace owner-approved copy during review.

## Visual and accessibility inspection

- Compare spacing, typography, color, shape, iconography, imagery, and component behavior to canonical references at the correct surface scale.
- Evaluate contrast with actual foreground/background pairs in the assessed mode. A color swatch or light-theme reading does not establish contrast in another mode.
- Check text resizing, localization expansion, keyboard/focus path, non-color status cues, labels/reading order, touch/click target dimensions and reduced-motion behavior in the evidence source that can establish each.
- Test long content and dynamic values. Look for clipping, overlap, hidden controls, awkward truncation, unbounded growth, broken scroll, and actions stranded below a fixed region.
- Distinguish appearance from semantics and interaction: screenshots cannot prove accessible names, keyboard operation, focus order, error announcements, or screen-reader behavior.

## Evidence confidence

For every assertion, label it as observed, inferred, or unknown and identify the artifact/revision/state. Prefer the smallest evidence set that resolves the user-impacting question. If the review depends on a live/native/canvas capability that was not exercised, say exactly what remains unverified and how to verify it; do not substitute a source scan, fixture, or mockup.