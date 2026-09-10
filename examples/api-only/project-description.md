# Project Description

## 1. What are we building

A link shortening API. Clients authenticate, submit a long URL, and receive a
short code. Requests to the short code redirect. There is no user interface —
this service is consumed by other applications.

## 2. Users and roles

| Role | Description | Can do | Cannot do |
|---|---|---|---|
| API client | An authenticated application | Create, list, delete its own links | See or delete another client's links |
| Anonymous | Anyone following a short link | Be redirected | Anything else |

## 3. Platforms

- [ ] Web application (browser)
- [ ] Admin portal
- [ ] Mobile — iOS
- [ ] Mobile — Android
- [ ] Desktop
- [x] Backend / server
- [x] Public API
- [ ] CLI

## 4. Core capabilities

- [x] User accounts and authentication
- [ ] More than one permission level
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

- Authenticate with an API key
- Create a short link from a long URL
- Follow a short link and be redirected
- List the calling client's links
- Delete one of the calling client's links

## 6. Technology

| Area | Required technology | Hard constraint? |
|---|---|---|
| Backend | | No — factory chooses |
| Database | | No — factory chooses |

## 7. Constraints

A client must never be able to read or delete another client's links, even by
guessing an id. Short codes must not be guessable in sequence. The redirect
must reject URLs pointing at internal addresses.

## 8. Explicitly out of scope

A web interface, analytics, custom domains, link expiry, QR codes, bulk
import, rate-limit tiers.

## 9. Reference material

None supplied.

## 10. Existing code

None.
