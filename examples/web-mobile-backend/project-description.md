# Project Description

## 1. What are we building

A shared shopping list for a household. Several people edit the same list from
phones and the web, including while offline in a shop with no signal. Changes
appear on other devices as they happen.

## 2. Users and roles

| Role | Description | Can do | Cannot do |
|---|---|---|---|
| Household member | Anyone invited to the household | Add, tick off, edit, delete items | Remove another household |

## 3. Platforms

- [x] Web application (browser)
- [ ] Admin portal
- [x] Mobile — iOS
- [x] Mobile — Android
- [ ] Desktop
- [x] Backend / server
- [ ] Public API
- [ ] CLI

## 4. Core capabilities

- [x] User accounts and authentication
- [ ] More than one permission level
- [x] Persistent data storage
- [ ] File or media upload
- [x] Offline use
- [x] Realtime updates / push
- [ ] Notifications
- [ ] Background or scheduled jobs
- [ ] Reporting, dashboards or export
- [ ] Payments
- [ ] Multiple languages
- [ ] Multiple organisations

## 5. Main features

- Sign up, log in, join a household by invite
- Add an item to the list
- Tick an item off; untick it
- Edit and delete items
- See other people's changes without reloading
- Work offline in a shop and sync on reconnect

## 6. Technology

| Area | Required technology | Hard constraint? |
|---|---|---|
| Mobile | One codebase for both platforms | Yes — a two-person project cannot maintain two |

## 7. Constraints

Two people ticking the same item offline must not produce a duplicate or lose
an edit. The conflict rule must be stated, not left to chance.

## 8. Explicitly out of scope

Price tracking, store layouts, barcode scanning, recipes, budgets, more than
one list per household.

## 9. Reference material

None supplied.

## 10. Existing code

None.
