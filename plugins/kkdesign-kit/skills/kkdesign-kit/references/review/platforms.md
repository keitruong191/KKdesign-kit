# Platform-specific design review
> Selectively adapted and modified by KKdesign-kit from Impeccable 4.8.0. See [attribution and license](../../docs/review-attribution.md).

Assess each requested platform separately; a shared product name or responsive layout does not make platform behavior equivalent. Record platform, OS/device family and version when known, input method, viewport/window size, appearance mode, and evidence type. If only one platform is inspected, label the others not assessed.

## macOS desktop

Inspect window resizing and minimum useful size, menu-bar and window controls, keyboard-first paths, focus visibility/order, shortcuts, pointer precision, contextual menus, drag/drop where present, system appearance and text scaling, and behavior across supported macOS versions. Check desktop-specific layout and window management rather than assuming an iPad/iPhone layout is sufficient. Verify behavior in the app/runtime for claims about native menus, focus, keyboard, or system integration.

## iOS

Inspect touch targets, reachability, safe areas, dynamic type, VoiceOver order/labels, orientation and compact layouts, system bars/gestures, keyboard obstruction, interruptions, and permission prompts. Check motion/reduced-motion and light/dark appearance where supported. A static frame cannot establish gesture, VoiceOver, keyboard, or lifecycle behavior.

## Android

Inspect touch targets, edge-to-edge/system bars, back behavior, window size classes and foldables if in scope, font scaling, TalkBack order/labels, keyboard resize/pan, permission rationale, lifecycle/recreation, and supported appearance modes. Confirm platform-specific navigation and system affordances in the actual app; do not borrow iOS conventions by default.

## Web (when in scope)

Inspect responsive breakpoints, keyboard and pointer paths, focus, browser zoom, semantic reading order, loading/error behavior, and supported browser/theme combinations. A source detector can report patterns in source/markup; it cannot establish the rendered result, Figma structure, native behavior, or performance by itself.

## Cross-platform comparison

For each platform independently, inspect required task flow, product context, design-system authority, variant/state coverage, long/localized content, contrast and accessibility evidence. Reuse a shared visual language only where evidence and platform conventions support it; log intentional divergence. Never aggregate an untested platform into a pass because another platform passed.