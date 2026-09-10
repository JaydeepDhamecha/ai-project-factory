# {{PROJECT_NAME}} — Platform Requirements

> Owner: `project-architect` · Defines the support floor. Anything outside it
> is out of scope and is not tested.

## Target platforms

{{PLATFORMS}}

<!-- OMIT IF: NOT web -->
## Web

| Aspect | Requirement |
|---|---|
| Browsers | |
| Minimum versions | |
| JavaScript required | |
| Accessibility target | |

### Viewports

{{BREAKPOINTS}}

| Name | Width | Tested |
|---|---|---|

A viewport listed here is tested by `project-playwright`. A viewport not
listed is not claimed to work.

<!-- OMIT IF: NOT mobile -->
## Mobile

| Aspect | Requirement |
|---|---|
| Platforms | {{PLATFORMS_MOBILE}} |
| Minimum OS versions | |
| Device classes | |
| Orientation support | |
| Distribution | |

### Mobile verification

Mobile builds are verified by `project-mobile` and `project-qa`. Playwright
does not test native mobile — where no device or emulator is available, the
status is `NOT_TESTED` or `BLOCKED` with the reason recorded, never `PASS`.

<!-- OMIT IF: NOT desktop -->
## Desktop

| Aspect | Requirement |
|---|---|
| Operating systems | |
| Minimum versions | |
| Packaging | |

<!-- OMIT IF: NOT backend -->
## Server

| Aspect | Requirement |
|---|---|
| Runtime version | |
| Operating system | |
| Resource floor | |

<!-- OMIT IF: NOT offline -->
## Connectivity

| Condition | Required behaviour |
|---|---|
| Online | |
| Degraded | |
| Offline | |
| Reconnect | |

## Explicitly unsupported

Listed so that a failure there is a known limitation, not a defect.
