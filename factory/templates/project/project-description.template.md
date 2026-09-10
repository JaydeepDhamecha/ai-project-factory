# Project Description

> Copy this file to `input/project-description.md` and fill it in.
> Everything is optional except **1. What are we building**. The factory
> derives what you leave out and records each derivation as an assumption in
> `docs/assumptions.md`.
>
> Prose is fine. Do not feel obliged to fill every table — an empty row is
> read as "not specified", which is more useful to the factory than a guess.

---

## 1. What are we building

<!-- Required. Two or three sentences. What the product is, who it is for,
     and the problem it solves. -->

## 2. Users and roles

<!-- Who uses it. If more than one role exists, say what each may and may not
     do — this drives the authorisation matrix and the `authzRoles` capability. -->

| Role | Description | Can do | Cannot do |
|---|---|---|---|

## 3. Platforms

<!-- Tick what is genuinely required. Anything unticked is not built. -->

- [ ] Web application (browser)
- [ ] Admin portal (separate back-office UI)
- [ ] Mobile — iOS
- [ ] Mobile — Android
- [ ] Desktop
- [ ] Backend / server
- [ ] Public API
- [ ] CLI

## 4. Core capabilities

- [ ] User accounts and authentication
- [ ] More than one permission level
- [ ] Persistent data storage
- [ ] File or media upload
- [ ] Offline use
- [ ] Realtime updates / push
- [ ] Notifications (email, push, in-app)
- [ ] Background or scheduled jobs
- [ ] Reporting, dashboards or export
- [ ] Payments
- [ ] Multiple languages
- [ ] Multiple organisations sharing one deployment

## 5. Main features

<!-- A list is enough. The factory turns these into dependency-ordered
     vertical slices and will tell you the order it chose, and why. -->

## 6. Technology

<!-- Leave blank to let the factory choose and justify a stack.
     Anything you state here is binding and overrides the factory's choice. -->

| Area | Required technology | Hard constraint? |
|---|---|---|
| Web | | |
| Mobile | | |
| Backend | | |
| Database | | |
| Hosting | | |

## 7. Constraints

<!-- Deadlines, compliance (GDPR, HIPAA, PCI), accessibility targets,
     browser or device support floors, existing systems to integrate with,
     things that must not change. -->

## 8. Explicitly out of scope

<!-- The most valuable section in this file. Anything listed here will not be
     built, and the factory will not "helpfully" infer it. -->

## 9. Reference material

<!-- List what you have put in input/references/ and say what each file is
     authoritative for. A file described as "the real spec" outranks one
     described as "rough sketch" when they disagree. -->

| File | What it is | Authoritative for |
|---|---|---|

## 10. Existing code

<!-- If this repository will also contain, or connect to, an existing
     codebase, say so here and describe what already works. -->
