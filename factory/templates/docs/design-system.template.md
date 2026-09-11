# {{PROJECT_NAME}} — Design System

> Owner: `project-designer` · Where reference images exist, every token below
> cites the image it came from. Where they do not, the token is marked
> `ASSUMED` and appears in `docs/assumptions.md`.

## Provenance

| Token group | Source | Confidence |
|---|---|---|
| Colour | | |
| Typography | | |
| Spacing | | |
| Components | | |

Confidence: `EXTRACTED` (visible in a supplied reference) · `DERIVED`
(inferred from what is visible) · `ASSUMED` (no source; a default was chosen).

## Colour

| Token | Value | Role | Source | Contrast checked |
|---|---|---|---|---|

Every foreground/background pair used for text records its contrast ratio and
the standard it meets. A pair that fails is a defect, not a style choice.

### Theme

| Aspect | Light | Dark | Notes |
|---|---|---|---|

## Typography

| Token | Family | Size | Weight | Line height | Used for |
|---|---|---|---|---|---|

## Spacing and layout

| Token | Value | Used for |
|---|---|---|

Grid, container widths, and gutters.

<!-- OMIT IF: NOT responsive -->
### Breakpoints and viewport behaviour

{{BREAKPOINTS}} · Orientations: {{ORIENTATIONS}}

Rules: `factory/rules/responsive-rules.md`. Each row states what the layout
*becomes* — a breakpoint with no stated layout change is not a specification.

| Name | Min width | Columns | Navigation | Tables | Modals | Layout change |
|---|---|---|---|---|---|---|

### Orientation

Both orientations are supported on every screen unless a lock is recorded in
`docs/platform-requirements.md` with a reason.

| Class | Portrait layout | Landscape layout | What changes on rotation |
|---|---|---|---|

Phone landscape is designed, not inherited: state what unpins, what collapses,
what becomes two columns, and what scrolls when vertical space is scarce.

### Adaptive component behaviour

| Component | Narrow viewport | Short landscape |
|---|---|---|
| Primary navigation | | |
| Data table | | |
| Modal / dialog | | |
| Drawer / sheet | | |
| Form | | |
| Toolbar / action bar | | |

| Touch rule | Value |
|---|---|
| Minimum touch target | 44 × 44 px |
| Minimum separation | 8 px |
| Safe-area insets | all four edges; left/right in landscape |

## Components

| Component | Variants | States | Source | Implemented in |
|---|---|---|---|---|

States must cover, where applicable: default, hover, focus, active, disabled,
loading, error, empty. A component documented without its states is
incomplete — those states are exactly what browser testing will exercise.

## Interaction and motion

| Aspect | Rule |
|---|---|
| Transition duration | |
| Easing | |
| Reduced motion | |

## Accessibility

| Requirement | Target | Verified |
|---|---|---|
| Contrast | | |
| Focus visibility | | |
| Keyboard reachability | | |
| Labels and roles | | |
| Motion preference respected | | |

## Reference comparison

| Screen | Reference | Implementation | Deviation | Accepted |
|---|---|---|---|---|

Evidence: `evidence/design/token-extraction.md`,
`evidence/playwright/visual-comparison.md`.

Deviations from a supplied design are recorded and justified, never silently
introduced.
