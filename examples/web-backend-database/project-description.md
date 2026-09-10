# Project Description

## 1. What are we building

A book club coordination site. Members propose books, vote on what to read
next, and discuss the current book. One organiser per club manages the
schedule and can remove content.

## 2. Users and roles

| Role | Description | Can do | Cannot do |
|---|---|---|---|
| Member | Anyone who has joined | Propose, vote, comment, edit own comment | Change the schedule, remove others' content |
| Organiser | Runs the club | Everything a member can, plus set the schedule and remove content | Delete the club |

## 3. Platforms

- [x] Web application (browser)
- [ ] Admin portal
- [ ] Mobile — iOS
- [ ] Mobile — Android
- [ ] Desktop
- [x] Backend / server
- [ ] Public API
- [ ] CLI

## 4. Core capabilities

- [x] User accounts and authentication
- [x] More than one permission level
- [x] Persistent data storage
- [ ] File or media upload
- [ ] Offline use
- [ ] Realtime updates / push
- [ ] Notifications
- [ ] Background or scheduled jobs
- [ ] Reporting, dashboards or export
- [ ] Payments
- [ ] Multiple languages
- [ ] Multiple organisations

## 5. Main features

- Sign up, log in, log out
- Propose a book
- Vote on proposals; one vote per member per round
- See the current book and the reading schedule
- Comment on the current book
- Organiser: set the schedule, close a voting round, remove a comment

## 6. Technology

| Area | Required technology | Hard constraint? |
|---|---|---|
| Database | Relational | Yes — the data is relational and the constraints matter |

## 7. Constraints

Members must not see another club's data. A member must not be able to vote
twice in a round, including by replaying the request.

## 8. Explicitly out of scope

Email notifications, mobile apps, book metadata lookup from an external
service, ratings, reading progress tracking, multiple clubs per account.

## 9. Reference material

None supplied.

## 10. Existing code

None.
