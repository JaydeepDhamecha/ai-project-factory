# Project Description

## 1. What are we building

A personal recipe collection site. A single person saves recipes they find,
tags them, and searches their own collection later. Everything runs in the
browser; there is no account and no server.

## 2. Users and roles

| Role | Description | Can do | Cannot do |
|---|---|---|---|
| Visitor | The only user; it is their own device | Add, edit, delete, tag, search recipes | Share with anyone else |

## 3. Platforms

- [x] Web application (browser)
- [ ] Admin portal
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
- [ ] Notifications
- [ ] Background or scheduled jobs
- [ ] Reporting, dashboards or export
- [ ] Payments
- [ ] Multiple languages
- [ ] Multiple organisations

Recipes are kept in browser storage. This is not a database in the sense that
would require a database agent, and the description says so deliberately.

## 5. Main features

- Add a recipe: title, ingredients, method, tags
- Edit and delete a recipe
- Browse all recipes
- Filter by tag
- Search by title or ingredient

## 6. Technology

| Area | Required technology | Hard constraint? |
|---|---|---|
| Web | | No — factory chooses |

## 7. Constraints

Must work on a phone-sized screen. No build step the author cannot run
locally.

## 8. Explicitly out of scope

Accounts, sharing, sync across devices, importing from other sites, photo
upload, printing, meal planning, shopping lists.

## 9. Reference material

None supplied.

## 10. Existing code

None.
