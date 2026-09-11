# Responsive and orientation rules

> Normative. Referenced by `designer`, `web`, `mobile`, `playwright`, `qa`,
> `reviewer`, the Definition of Done (§5, §6) and GATE-PW.

A user interface is **not** finished when it renders correctly at the width the
developer happened to have open. Every UI the factory produces — web **and**
native mobile — must work across the device classes it claims to support, in
**both portrait and landscape**.

Responsiveness is not a feature that can be descoped. It is a correctness
property, like validating a form or handling a 500. A layout that breaks at
390 px or on rotation is a **defect**, not a backlog item.

---

## 1. Scope — when these rules apply

| Capability | Applies |
|---|---|
| `web` or `adminPortal` | Yes — all of §3, §4, §5 |
| `mobile` | Yes — all of §3, §4, §6 |
| `desktop` | §3 and §4 for resizable windows |

`responsive` is `true` whenever any of those capabilities is true. `discovery`
does not ask the user whether they want a responsive UI, and does not infer
`false` from silence in the description. Only an explicit, recorded user
statement that a single fixed viewport is required may set it `false`, and that
statement is cited in `docs/assumptions.md`.

---

## 2. The viewport matrix

`docs/design-system.md` and `docs/platform-requirements.md` declare the matrix.
In the absence of a project-specific decision, this is the default, and every
row is tested:

### Web

| Class | Portrait | Landscape | Notes |
|---|---|---|---|
| Small phone | 360 × 740 | 740 × 360 | The narrowest supported width. Base styles target this. |
| Large phone | 414 × 896 | 896 × 414 | |
| Tablet | 768 × 1024 | 1024 × 768 | Where the layout typically changes shape |
| Laptop | 1280 × 800 | — | |
| Desktop | 1440 × 900 | — | |
| Wide | 1920 × 1080 | — | Container max-width must hold; no infinite line lengths |

### Native mobile

| Class | Portrait | Landscape |
|---|---|---|
| Phone | 390 × 844 | 844 × 390 |
| Small phone | 360 × 640 | 640 × 360 |
| Tablet | 810 × 1080 | 1080 × 810 |

A viewport that is not in the matrix is not claimed to work. A viewport that
**is** in the matrix and was not exercised is `NOT_TESTED`, never `PASS`.

Breakpoint numbers in the manifest (`breakpoints`) are the authority for CSS
media queries; the matrix above is the authority for *what gets tested*. They
are related but not the same thing — testing only at the breakpoint boundaries
misses the widths real devices actually use.

---

## 3. Layout rules — mandatory

1. **No horizontal page scroll** at any supported width. Overflow is permitted
   only inside an element explicitly designated scrollable (a wide table, a
   code block, a chart) and that element must show it is scrollable.
2. **Mobile-first.** Base styles target the narrowest supported width;
   breakpoints add capability upward. A desktop layout retrofitted with
   `max-width` overrides is the usual cause of a broken phone view.
3. **No fixed-width layout containers.** No `width: 1200px`, no `min-width`
   greater than the narrowest supported viewport, on any element in the layout
   chain. Fluid units, grid, or flex — with wrapping enabled.
4. **Media is fluid.** Images, video, iframes, canvases and embeds never exceed
   their container.
5. **Navigation adapts.** Below the navigation breakpoint the full navigation
   collapses to a drawer, sheet or bottom bar. The collapsed control must
   *open*, be operable, close, and trap focus while open. A hamburger icon that
   renders but does nothing is a defect, not a responsive layout.
6. **Tables declare a strategy.** Each data table picks one and documents it:
   horizontal scroll inside a bounded container, column priority (hide
   lower-priority columns as width drops), or card/stacked rows. "It overflows
   the page" is not a strategy.
7. **Forms collapse to one column** below the tablet breakpoint. Labels are not
   truncated. The submit control is reachable while the on-screen keyboard is
   open.
8. **Dialogs, modals, drawers and sheets fit the viewport** at every size,
   including short landscape. They scroll internally; their primary action is
   never pushed off-screen or under a fixed footer.
9. **Touch targets** are at least 44 × 44 CSS px with at least 8 px separation
   on any touch-capable viewport.
10. **Text remains legible and complete.** No essential content hidden by
    truncation. Browser zoom to 200 %, and OS text-size scaling on mobile, must
    not lose content or function.
11. **Fixed and sticky chrome is budgeted.** Combined fixed header and footer
    must not exceed 25 % of the short-side viewport dimension. In phone
    landscape, headers unpin, shrink or collapse rather than eating the screen.
12. **Safe areas are honoured** in both orientations — notch, status bar, home
    indicator, rounded corners. Landscape insets are on the **left and right**;
    a layout that only pads the top is not safe-area correct.

---

## 4. Orientation rules — mandatory

1. **Both orientations are supported by default**, on every screen, on web and
   on native mobile.
2. **Locking is an exception that must be recorded.** A screen may be locked to
   one orientation only when the reason is written into
   `docs/platform-requirements.md` (for example a camera, scanner or signature
   capture screen). A locked screen is still tested in its permitted
   orientation, and the lock is enforced in code, not assumed.
3. **Rotation preserves state.** After rotating, the following survive: form
   input, scroll position (within a reasonable tolerance), the open modal or
   drawer, list selection, pagination position, media playback position, and
   the current route. Rotation must never navigate away, remount a screen so
   that typed input is lost, or crash.
4. **Landscape on a phone is a first-class layout, not a squeeze.** Vertical
   space is scarce: long forms and dashboards scroll rather than compress;
   multi-column layouts may be used where they help; nothing critical is
   clipped below the fold without a visible scroll affordance.
5. **Rotation is exercised while the UI is in a non-trivial state** — mid-form,
   modal open, list scrolled — not only on a freshly loaded screen. Rotating an
   empty screen proves very little.
6. **The on-screen keyboard in landscape** must not cover the focused field or
   the submit control. This is the most commonly missed landscape defect.

---

## 5. Web-specific

- A `<meta name="viewport" content="width=device-width, initial-scale=1">` tag
  is present. Its absence makes every other rule in this file untestable.
- User scaling is **not** disabled (`user-scalable=no` and `maximum-scale=1`
  are prohibited — they are also an accessibility failure).
- Hover-only affordances have a touch equivalent. A control that only reveals
  its action on `:hover` is unreachable on a touch device.
- `dvh`/`svh` (or an equivalent) rather than `100vh` where the mobile browser
  chrome would otherwise cause clipping or a double scrollbar.
- Orientation on web is exercised by resizing the browser viewport to the
  landscape dimensions in the matrix — this is what `project-playwright` does.

---

## 6. Native-mobile-specific

- The app declares support for both orientations in its platform
  configuration (`Info.plist` `UISupportedInterfaceOrientations`, the Android
  manifest / `configChanges`, or the framework equivalent) unless §4.2 applies.
- Android configuration changes must not silently destroy state. Either the
  state is hoisted out of the Activity/Composable lifecycle, or rotation is
  handled explicitly — it is never left to chance.
- Tablet layouts are verified, not assumed from phone layouts. A phone layout
  stretched to 1080 px with a single centred column is reported as such.
- Split-screen / multi-window on Android and iPad must not crash the app; if it
  is unsupported, that is declared in `docs/platform-requirements.md`.
- `SafeAreaView` (or platform equivalent) wraps screens, with the landscape
  left/right insets applied.

---

## 7. Evidence

Responsiveness is claimed only from observation.

| Producer | Evidence |
|---|---|
| `project-designer` | `docs/design-system.md` §Breakpoints and §Orientation — the layout change at each breakpoint, and the landscape treatment |
| `project-web` | `evidence/implementation/<feature>/responsive-check.md` — each viewport class × orientation, observed |
| `project-playwright` | `evidence/playwright/responsive/<screen>-<class>-<orientation>.png` plus `evidence/playwright/responsive-matrix.md` |
| `project-mobile` | `evidence/qa/mobile/<feature>/orientation/<platform>-<class>-<orientation>.png` and a rotation-state note |

A row of the matrix with no artefact is `NOT_TESTED`. A matrix cell is never
inferred from an adjacent one — 768 px passing says nothing about 360 px.

---

## 8. Defect classification

| Symptom | Minimum severity |
|---|---|
| Horizontal page scroll at a supported width | HIGH |
| Primary action unreachable at a supported viewport or orientation | CRITICAL |
| Navigation unusable below the nav breakpoint | CRITICAL |
| Content clipped or overlapped on rotation | HIGH |
| State lost on rotation (form input, open modal) | HIGH |
| Modal action off-screen in landscape | HIGH |
| Touch target below 44 px on a touch viewport | MEDIUM |
| Table overflowing the page with no strategy | HIGH |
| Safe-area inset ignored in landscape | MEDIUM |
| Keyboard covering the focused field in landscape | HIGH |

These go through `.claude/skills/bug-fix-loop/SKILL.md` like any other defect.
"Known responsive limitation" is not a status — it is either fixed, or it is an
open defect with a severity and an owner.
