# WorkHub — User Manual

**Requirement:** REQ-036 (End-User Documentation — user guide and role-specific workflows).
**Applies to:** the build in this repository as of 2026-09-11.
**Owner:** `project-product`.

> **How to read this manual.** Everything described below was checked against the
> code that is actually in the build, and against `evidence/playwright/routes.md`,
> which lists the screens reached in a real browser. Buttons, headings and messages
> are quoted exactly as they appear on screen.
>
> Some things the project's requirements ask for are **not in this release**. They are
> not described as if they worked — they are listed, plainly, in
> [Known limitations in this release](#12-known-limitations-in-this-release). Read that
> section before you plan work around this build.
>
> Every claim in this manual is traced to a file or a route in
> `evidence/release/user-manual-sources.md`.

---

## Contents

1. [What WorkHub is](#1-what-workhub-is)
2. [The three roles](#2-the-three-roles)
3. [Getting started](#3-getting-started)
4. [Finding your way around](#4-finding-your-way-around)
5. [The Dashboard](#5-the-dashboard)
6. [Employees](#6-employees)
7. [Projects](#7-projects)
8. [Tasks](#8-tasks)
9. [Reports](#9-reports)
10. [Your account — Settings and your password](#10-your-account--settings-and-your-password)
11. [The mobile app](#11-the-mobile-app)
12. [Known limitations in this release](#12-known-limitations-in-this-release)

---

## 1. What WorkHub is

WorkHub is an employee and task management platform for a single organisation. It
keeps four things in one place:

- **People** — a directory of everyone in the organisation, with their role, department and status.
- **Projects** — a named piece of work with a start date, an end date, an owner and a team.
- **Tasks** — the individual units of work inside a project, each with an assignee, a due date, a priority and a status.
- **Reporting** — a dashboard of live figures, and a Reports screen for managers and administrators.

It comes in two clients that talk to the same API:

| Client | What it is | Where it runs |
|---|---|---|
| **Web app** | The full application. Everything in this manual except where noted. | A browser, at `http://localhost:5173` in local development |
| **Mobile app** | A companion app — read, comment, change task status, create tasks, manage people if you are an Admin. Narrower than the web app. See [section 11](#11-the-mobile-app). | iOS / Android through Expo |

Work statuses are the same vocabulary everywhere: a project or a task is **Pending**,
**In Progress** or **Completed**; a task's priority is **Low**, **Medium** or **High**.

---

## 2. The three roles

Your role is set on your account and decides what you see. It appears under your name
in the top-right of the web app, and on the **Profile** tab in the mobile app. You
cannot change your own role — only an Admin can.

The application enforces each rule in three independent places: the navigation hides
what you may not use, the route refuses it if you type the address by hand, and the API
refuses it even if the screen were wrong.

### Admin

**Can do everything the product offers in this release:**

- Add, edit and delete employees, and set anyone's role and status.
- Create, edit and **delete** projects, and add or remove project team members.
- Create, edit, assign and delete tasks anywhere in the organisation.
- See every project and every task.
- Open **Reports** and export CSVs.
- Change their own profile and password.

**Cannot:** configure the organisation itself. There is no organisation-settings area
in this release (see [Known limitations](#12-known-limitations-in-this-release)).

### Manager

**Can:**

- Create and edit projects, and add or remove team members on the projects they manage.
- Create, edit, assign and delete tasks.
- Open **Reports** and export CSVs.
- Browse the employee directory.
- Change their own profile and password.

**Cannot:**

- **Delete a project.** The delete control is not shown to a Manager; project deletion is Admin-only.
- **Add, edit or delete an employee.** On the **Employees** table a Manager sees an em dash (`—`) in the **Actions** column, and there is no **Add Employee** button.
- Act outside their own scope: a Manager sees the projects they own or are a member of, not the whole organisation.

### Employee

**Can:**

- See the projects they are a member of, and the tasks they can see through those projects.
- **Change the status** of a task assigned to them, from the task's own page.
- Add comments to tasks.
- Browse the employee directory (read-only).
- Change their own profile and password.

**Cannot:**

- Create, edit or delete projects, tasks or employees. Where a manager sees Edit and Delete, an Employee sees a **View** link instead.
- Change a task's assignee, due date or priority — even on their own task. The task page says so: *"This task is assigned to you — you can change its status. Only a manager or administrator can change the assignee, due date or priority."*
- Open **Reports**. The link is absent from the navigation, and going to `/reports` directly shows *"403 — Access denied / Reports are available to managers and administrators only."*

### Summary

| | Admin | Manager | Employee |
|---|---|---|---|
| Add / edit / delete employees | Yes | No | No |
| Browse employee directory | Yes | Yes | Yes |
| Create / edit projects | Yes | Yes | No |
| Delete projects | Yes | **No** | No |
| Add / remove project team members | Yes | Yes | No |
| Create / edit / delete tasks | Yes | Yes | No |
| Change status of a task assigned to you | Yes | Yes | **Yes** |
| Change a task's assignee / due date / priority | Yes | Yes | No |
| Comment on tasks | Yes | Yes | Yes |
| Open Reports and export CSV | Yes | Yes | **No** |
| Change your own profile and password | Yes | Yes | Yes |
| Configure the organisation | **Not in this release** | No | No |

---

## 3. Getting started

### 3.1 Starting the application (local development)

The full, verified procedure is in `docs/deployment.md` — follow that, not this summary.
In short: start PostgreSQL, configure and migrate the backend, run the API on
`http://localhost:8000`, then run the web client on `http://localhost:5173`.

### 3.2 Demo accounts

If the demo dataset has been loaded (`manage.py seed_demo`, development only), these
accounts exist:

| Sign in as | Role | Notes |
|---|---|---|
| `jaydeep@example.com` | Admin | |
| `tarun@example.com` | Manager | Owns four projects |
| `neha@example.com` | Manager | Owns two projects |
| `priya@example.com` | Employee | Member of three projects |
| `sanjay@example.com` | Employee | Member of one project |
| `rahul@example.com` | Employee | **Inactive — cannot sign in at all.** Useful for checking the inactive-account message |

**The password is not printed in this manual, deliberately.** All seeded accounts share
one password, defined as `DEMO_PASSWORD` in
`backend/apps/common/management/commands/seed_demo.py`; the seed command also prints it
to the console when it finishes. That value is a committed credential and a recorded
security finding (**SEC-F-006 / SEC-F-010** in `docs/security.md`) — treat it as a local
development convenience only, and never let a seeded account exist anywhere real.

### 3.3 Signing in

1. Open the web app. Any address you were trying to reach without a session sends you to `/login`.
2. The page is headed **"Welcome Back"** with **"Sign in to your account"** underneath.
3. Fill in **Email address** and **Password**.
4. Leave **Remember me** ticked to stay signed in after closing the browser; untick it to be signed out when the tab closes.
5. Press **Sign In**.

You land on the **Dashboard** — unless you were bounced here from somewhere else, in
which case WorkHub returns you to the page you originally asked for.

If your details are refused you see: *"Invalid email or password. If your account is
inactive, contact an administrator."* Both fields are marked, and the same message
covers a deactivated account — an inactive user cannot sign in whatever their password.

### 3.4 Registering your own account

From the sign-in page, follow **"Don't have an account? Register"**.

The page is headed **"Create Account"** / **"Join WorkHub"** and asks for **First name**,
**Last name**, **Email address**, **Department** (marked *Optional*), **Password** and
**Confirm password**. A strength meter sits under the password field; the **Create
Account** button stays disabled until the password is rated Good or Strong. The minimum
is 8 characters.

**A self-registered account is always created with the Employee role.** Only an Admin
can promote it to Manager or Admin afterwards.

### 3.5 If you have forgotten your password

1. On the sign-in page, follow **Forgot password?**.
2. The page is headed **"Forgot Password?"** / *"Enter your email and we'll send you a reset link"*. Enter your email and press **Send Reset Link**.
3. You then see *"Check your email for a password reset link. The link is valid for one hour."*
4. Follow the link in the email. It opens **"Reset Password"** / *"Choose a new password"*, already carrying your token.
5. Enter **New password** and **Confirm new password**, then press **Reset Password**. On success: *"Your password has been reset. Redirecting you to sign in…"* and you are taken back to sign-in.

If you have a token but not the link, the success screen offers
**"I already have a reset token"**, which opens the same page with a **Reset token**
field (*"Taken from the reset link in your email"*) for you to paste it into.

> **In local development** the reset email is usually not sent by a real mail server — it
> is printed to the API server's console, token and all. That is the
> `EMAIL_BACKEND=...console.EmailBackend` setting in `backend/.env`. Real delivery needs
> SMTP configured; see `docs/deployment.md`.

---

## 4. Finding your way around

### 4.1 The sidebar

The web app has a fixed left sidebar (on a narrow screen it becomes a drawer behind the
menu button). Its entries, in order:

| Entry | Goes to | Who sees it |
|---|---|---|
| **Dashboard** | `/dashboard` | Everyone |
| **Employees** | `/employees` | Everyone |
| **Projects** | `/projects` | Everyone |
| **Tasks** | `/tasks` | Everyone |
| **Reports** | `/reports` | **Admin and Manager only** |
| **Settings** | `/settings` | Everyone |

### 4.2 The top bar

- **Search box** (placeholder **"Search…"**). Typing a term and pressing Enter opens the **Tasks** list filtered to that term. It searches tasks — it is not an all-content search.
- **Bell icon.** Labelled *Notifications*. In this release it simply takes you to the Dashboard; there is no notification list and no push notification. See [Known limitations](#12-known-limitations-in-this-release).
- **Your name, role and avatar.** Opens a menu with two items: **Settings** and **Log out**.

There is also a **Skip to content** link for keyboard and screen-reader users, revealed
when you tab into the page.

### 4.3 Every address in the web app

| Address | Screen |
|---|---|
| `/login` | Sign in |
| `/register` | Create an account |
| `/forgot-password` | Request a reset link |
| `/reset-password` | Set a new password with a token |
| `/` | Redirects to `/dashboard` |
| `/dashboard` | Dashboard |
| `/employees` | Employee directory |
| `/projects` | Project list |
| `/projects/<id>` | One project |
| `/tasks` | Task list |
| `/tasks/<id>` | One task |
| `/reports` | Reports — Admin and Manager only |
| `/settings` | Your profile and password |
| anything else | A **404 / Page not found** page, with **Back to Dashboard** and **Sign In** buttons |

Useful addresses that the app's own controls produce, and which you can bookmark:
`/tasks?mine=true` (only your tasks), `/tasks?status=pending`,
`/tasks?status=completed`, `/projects?status=in_progress`.

Sessions survive a reload and a bookmarked deep link. If your session has expired, you
are returned to sign-in and then forwarded to the page you asked for.

---

## 5. The Dashboard

**Everyone** has a dashboard, at `/dashboard`. The figures on it are scoped to you: an
Admin sees the organisation, a Manager sees their own projects and team, an Employee
sees their own work.

It greets you by name — *"Welcome back, **Priya**!"* — followed by a line that depends
on your role ("Here's how the whole organisation is tracking today.", "Here's where
your projects and your team stand today.", "Here's what is on your plate today.").

**Quick links.** Up to four cards under the greeting, each leading somewhere you are
allowed to go: *My tasks*, *Projects*, *Employees* (Admin and Manager), *Reports*
(Admin and Manager), *Account settings* (Employee).

**The four summary cards.** Each is clickable and opens the matching filtered list.
Their labels differ by role, because their meaning differs by role:

| Admin and Employee see | Manager sees |
|---|---|
| Total Employees | Active Projects |
| Active Projects | Team Size |
| Open Tasks | Open Tasks |
| Completed Tasks | My Completed Tasks |

A Manager's **Team Size** counts the distinct members of the projects they own — **including
the Manager** — not the organisation's headcount. So a Manager who leads two people sees
**3**, and that number will be smaller than the Admin's Total Employees whenever anyone in the
company is outside the Manager's projects. **My Completed Tasks** counts tasks assigned to
that Manager, and opens the list filtered the same way.

> This card was labelled **Team Members** until 17 September 2026. The number it shows did not
> change; the wording did, because "Team Members" read as *your team, not counting you* and the
> card had always counted you. On the **mobile app** the same figure appears under the simpler
> label **Employees**.

**My Urgent Tasks.** A short list of your most urgent open tasks, each with its priority
and due date, with **View All** leading to `/tasks?mine=true`. Always shown to an
Employee; shown to others when they have any. When empty: *"Nothing urgent right now"*.

**Task Overview.** A doughnut chart split into **Completed**, **In Progress** and
**Pending**. Before any tasks exist: *"No tasks yet"*.

**Recent Activities.** A scrolling feed of what has happened, newest first, with
**View All** leading to the task list. The feed is scoped to what you may see.

**Get started.** On a brand-new, empty account the dashboard shows a **Get started**
card — *"There is nothing here yet. Here is where to begin."* — with next steps suited
to your role, rather than four zeroes and nothing to do.

The dashboard **refreshes itself about every 8 seconds** while it is open, so a task or
comment created by someone else appears without you reloading. Figures already on screen
stay on screen while it refreshes.

---

## 6. Employees

**Address:** `/employees`. Heading **"Employees"**, subtitle *"Manage your team members"*.

**Everyone can browse this directory.** Only an **Admin** can change it.

### Finding someone

- **Search employees…** matches name, email and department as you type.
- **All roles** is a dropdown filtering to **Admin**, **Manager** or **Employee**.
- Results are paginated, 10 to a page.

The table columns are **Name**, **Email**, **Role**, **Status** and **Actions**. The name
cell shows the person's department beneath their name. **Status** is **Active** or
**Inactive** — an inactive person cannot sign in.

If nothing matches you get *"No employees found matching '…'"* with a **Clear search**
or **Clear filters** button to put the list back.

### Adding someone (Admin)

1. Press **Add Employee** at the top right.
2. Fill in the dialog: **First name**, **Last name**, **Email address**, **Department**, **Role** (Employee / Manager / Admin), **Status** (Active / Inactive) and **Password** (*"At least 8 characters"*).
3. Press **Create Employee**. A toast confirms **"Employee created."**

### Editing someone (Admin)

Press the pencil icon on their row. The same dialog opens as **Edit Employee**, with the
password field relabelled **New password** and hinted *"Leave blank to keep the current
password"* — so you can edit details without touching their password. Press **Save
Changes**; a toast confirms **"Employee updated."**

This is also how you change someone's **role** or deactivate them: set **Role** or set
**Status** to *Inactive*.

### Removing someone (Admin)

Press the bin icon. A confirmation asks: *"Remove <name> from WorkHub? Their record is
archived, not destroyed."* Press **Delete** to confirm. The record is archived rather
than erased, so history that refers to it stays readable.

You cannot delete your own account — the button is disabled, with the explanation *"You
cannot delete your own account"*.

### What a Manager and an Employee see

The same table, without the **Add Employee** button, and with an em dash (`—`) in the
**Actions** column. Read-only.

---

## 7. Projects

**Address:** `/projects`. Heading **"Projects"**, subtitle *"Create and manage your
projects"*.

You see the projects you own or are a member of; an Admin sees all of them.

### The list

- **Search projects…** matches the project name.
- **All statuses** filters to **Pending**, **In Progress** or **Completed**. The filter is kept in the address, so a filtered list can be bookmarked or shared.
- Columns: **Name**, **Description**, **Status**, **Manager**, **Start Date**, **End Date**, **Actions**. Under each name is a count such as *"7/12 tasks done"*.
- Paginated, 10 to a page.

### Creating a project (Admin, Manager)

Press **New Project** and fill in **Project name**, **Description**, **Status**, **Start
date** and **End date**. Press **Create Project**; a toast confirms **"Project
created."**

### Editing a project (Admin, Manager)

Press the pencil icon on the row, change what you need, press **Save Changes**. Toast:
**"Project updated."**

### Deleting a project (Admin only)

Press the bin icon. The confirmation reads *"Delete "<name>"? Its tasks are archived with
it."* Press **Delete**. **A Manager has no delete control** — only an Admin can delete a
project.

### Inside a project

Click a project name to open it. At the top, **Back to Projects**, then the project's
name, description and status badge, and four figures: **Start Date**, **End Date**,
**Owner**, **Tasks Completed** (shown as completed/total).

**Team Members (N).** Each member's name, role badge and email.

- **Admin and Manager** can remove a member with the × button — except the project's owner, who cannot be removed this way.
- **Admin and Manager** add a member with the **Select an employee…** dropdown and the **Add** button. Toast: **"Team member added."** People already on the project are not offered again.
- An Employee sees the list without these controls.

**Project Tasks.** Every task in the project, each with its priority and status, linking
through to the task. If the project has no tasks yet you see *"No tasks in this
project"*, and — if you may create one — a **New Task** button that opens the task
dialog with this project already chosen.

---

## 8. Tasks

**Address:** `/tasks`. Heading **"Tasks"**, subtitle *"Track work across every project"*.

### The list

- **Search tasks…** matches the task title. The top-bar search lands here too.
- **All statuses** — Pending / In Progress / Completed.
- **All priorities** — High / Medium / Low.
- **My tasks** — a checkbox limiting the list to tasks assigned to you.
- Columns: **Title**, **Project**, **Assigned To**, **Due Date**, **Priority**, **Status**, **Actions**.
- A task past its due date shows its date in red with **(overdue)** after it.
- Paginated, 10 to a page. Every filter is kept in the address and can be bookmarked.

### Creating a task (Admin, Manager)

Press **New Task**. The dialog asks for **Title**, **Description**, **Project**,
**Assigned to**, **Status**, **Priority** and **Due date**. An assignee is required when
creating. Press **Create Task**; toast: **"Task created."**

You can also create a task from inside a project — see [section 7](#7-projects) — which
pre-selects that project.

### Editing and deleting a task (Admin, Manager)

The pencil icon opens the same dialog as **Edit Task** (submit button **Save Changes**).
The bin icon asks *"Delete "<title>"? This also archives its comments."* and then
**Delete**.

An **Employee** sees a **View** link in the **Actions** column instead — no edit, no
delete.

### Inside a task

Click a task title. You get **Back to Tasks**, the task's title, and beneath it the
project it is in (a link) and who created it.

- **Status.** A dropdown at the top right. Usable by a Manager, an Admin, **and by the employee the task is assigned to**. Changing it saves immediately and confirms with **"Status updated."** If you may not change it, you see the status as a badge instead.
- **Description.** Or *"No description was provided for this task."*
- **Assigned To**, **Due Date**, **Priority.** Editable in place **by a Manager or an Admin only**; each saves as you change it. An Employee sees these as read-only values, plus the note *"This task is assigned to you — you can change its status. Only a manager or administrator can change the assignee, due date or priority."*

### Comments

At the bottom of a task is a **Comments** card: every comment with its author, how long
ago it was written, and its text. Everyone who can see the task can comment: type into
**Add a comment…** and press **Post**. An empty comment is refused with *"A comment
cannot be empty"*. Before the first comment: *"No comments yet"* / *"Start the
conversation about this task."*

Comments cannot be edited or deleted from the interface in this release — see
[Known limitations](#12-known-limitations-in-this-release).

---

## 9. Reports

**Address:** `/reports`. **Admin and Manager only.** Heading **"Reports"**, subtitle
*"Performance and analytics across your organisation"*.

An Employee has no **Reports** entry in the sidebar, and opening the address directly
shows *"403 — Access denied / Reports are available to managers and administrators
only."* A Manager's figures are scoped to their own projects and team.

The screen has five panels:

**Tasks by Status** — a bar for each status.

**Tasks by Priority** — a bar for each priority.

**Project Progress** — a table of every project you can report on.

- **Filter by project status** narrows it to one status.
- A line states **"Showing N of M projects"**, so a short table is always visible as a short table.
- Sortable columns: **Project**, **Status**, **Members**, **Tasks**, **Completion vs. schedule**. Plus a **Schedule** column showing how far ahead or behind the project is, with its start and end dates.
- The bar in **Completion vs. schedule** shows actual completion; a dark tick marks the progress the project's own dates imply for today. The panel explains this beneath the table.
- **Export CSV** downloads exactly what is on screen — the current filter and sort included — as `workhub-project-report-<date>.csv`. Columns: Project, Status, Members, Total Tasks, Completed Tasks, Completion %, Start Date, End Date, Expected % By Today, Variance (pts).

**Employee Performance** — one row per person, sorted by tasks completed, highest first.

- **"Showing N of M employees"**.
- Sortable columns: **Employee**, **Role**, **Department**, **Assigned**, **Completed**, **Completion Rate**.
- **Export CSV** downloads `workhub-employee-performance-<date>.csv`. Columns: Employee, Email, Role, Department, Assigned Tasks, Completed Tasks, Completion %.

**Tasks by Project** — a bar for each project's task count. A **Priority key:** at the
foot of the page shows the three priority badges.

> **If a report could not be loaded in full** you will see an orange warning:
> *"Partial report — N employees could not be loaded. Sorting and export cover only the
> rows shown."* with a **Retry** button. This is deliberate: a partial report announces
> itself rather than looking complete. If you see it, retry before trusting the numbers
> or the export.

~~**There is no date-range filter on the web Reports screen in this release.** Every
figure is all-time.~~ — **superseded 2026-09-17.** The filter **landed on 2026-09-16**,
after this passage was written. The passage was true when written and stale by the time
it shipped; it is struck through rather than deleted so the correction explains itself.

**What is actually there.** The **Employee Performance** card carries a date-range
filter: **From** and **To** date fields, an **Apply** button, and a **Clear** button once
a window is set. Applying a window re-reads the employee report for that window. A
**Period:** badge beside the fields shows the window *the server reports it applied* —
"All time" when there is none. If the server ever applied a different window from the one
you asked for, the card says so instead of presenting the figures under a filtered
heading.

**It covers one report, not the page.** Measured against a live API on 2026-09-17:
applying a window re-requests the **employee** report and nothing else. **Tasks by
Status**, **Tasks by Priority**, **Tasks by Project** and **Project Progress** are not
re-read and stay **all-time** whatever the dates say. The **Period:** badge therefore
describes the Employee Performance table only — read the other four panels as all-time.

Two details worth knowing. The window changes each employee's *figures*, not *who is
listed*: "Showing 28 of 28 employees" stays 28, with zeroes against anyone who had no
activity in the window. And the window is not part of the page address, so a browser
refresh returns the card to **All time**.

(The mobile app also has a date-range control, and its coverage is **different** from the
web's — do not read across from one client to the other. ~~Section 11's description of it
is **under review as of 2026-09-17** — it was not re-measured by this correction.~~
**Resolved 2026-09-17:** section 11 has now been re-measured and corrected. Mobile applies
its window to **all three** of its reports, which is *broader* than web's one-in-five. See
[section 11](#11-the-mobile-app).)

---

## 10. Your account — Settings and your password

**Address:** `/settings`, also reachable from **Settings** in your avatar menu. Heading
**"Settings"**, subtitle *"Your profile and account security"*.

**Every role can use this page** — Admin, Manager and Employee alike. It concerns your
own account and nothing else.

### Profile

Your avatar, name, email and role badge, then an editable form:

- **First name** (required)
- **Last name** (required)
- **Department**
- **Email address** — shown but greyed out, with the note *"Your email address is managed by an administrator."* Ask an Admin if it needs to change.

Press **Save Changes**. A toast confirms **"Profile updated."** These three fields are
the only ones this page can change: you cannot change your own role here, and nothing
you do here affects anyone else's record.

Beneath the form is a line naming your organisation, followed by *"Organisation-wide
settings are not part of this release."* That is accurate — see
[Known limitations](#12-known-limitations-in-this-release).

### Change Password

1. Enter your **Current password**.
2. Enter a **New password** — *"At least 8 characters"*. A strength meter appears as you type; the **Change Password** button stays disabled while the password is weak (*"Choose a stronger password to continue"*).
3. Repeat it in **Confirm new password**. A mismatch is refused with *"Passwords do not match"*.
4. Press **Change Password**. A toast confirms **"Password changed."**

> **Changing your password signs out every other session.** WorkHub ties every issued
> token to your current password, so changing it — or having an administrator change it,
> or resetting it by email — immediately invalidates every token issued before it, on
> every device. This is also the only reliable way to end a session you no longer
> control: see [Known limitations](#12-known-limitations-in-this-release).

### Signing out

Open your avatar menu and choose **Log out**. You are returned to the sign-in page and
your stored session is cleared from this browser, so protected pages are guarded again.

> **What signing out does not do.** There is no server-side sign-out in this release.
> Logging out clears the tokens in *your* browser, but does not invalidate them
> centrally: a token someone else had already captured stays usable for up to 24 hours
> (access) or 7 days (refresh). If you have signed out on a shared or lost device, or
> suspect a session was captured, **change your password** — that does invalidate them.
> This is recorded finding SEC-F-002 in `docs/security.md`.

---

## 11. The mobile app

The mobile app is a **companion** to the web app, not a replacement. It is built with
Expo (React Native) and runs on iOS and Android.

> **Honest status.** ~~The mobile app has **not been launched on a simulator, emulator or
> physical device** on the verified development host — that machine has no iOS simulator
> and no registered Android AVD (`docs/deployment.md`, deployment step 9). What follows
> describes the screens and behaviour that are **built in the code**; nobody has yet
> confirmed them running on a device.~~ — **superseded 2026-09-17.** That was true when it
> was written and is now false for Android. The app **has** been run on an Android
> emulator: AVD `WorkHub_Pixel4_API34`, Android 14, with 19 screenshots
> (`evidence/retest/10-mobile-android-emulator-20260911T074508Z.log`;
> `evidence/implementation/mobile/android-emulator-20260911T073507Z/`), plus a second
> session at `evidence/qa/mobile/orchestrator-device-verification-20260914T0620Z/`. What
> follows is therefore **observed running** on Android and **built in the code but never
> executed** on iOS — `xcrun simctl` is absent on this host (BLK-001, re-verified
> 2026-09-17;
> `evidence/retest/mobile-ios-simulator-BLOCKED-blk-001-20260914T051500Z.txt`). **No
> mobile store build exists**, on either platform: there is still no `eas.json` anywhere
> in the repository, and `mobile/app.json` carries bundle identifiers but no build
> profiles and no signing configuration.

### Running it

```
cd mobile
cp .env.example .env        # then set EXPO_PUBLIC_API_BASE_URL
npm start
```

`EXPO_PUBLIC_API_BASE_URL` must be an address the *device* can reach — `localhost` for
the iOS simulator, `10.0.2.2` for an Android emulator, your machine's LAN IP for a real
phone. Both the sign-in screen and the **Profile** tab display the API address the app
is using, which is the quickest way to diagnose "it cannot reach the server".

### Signing in

A **WorkHub** splash while the stored session is restored, then either the app or the
sign-in screen. Sign-in is headed **"Welcome Back"** / *"Sign in to your account"*, with
**Email address**, **Password** and a **Sign In** button. Your session is kept in the
device's secure storage.

**The mobile app has no Register, no Forgot password and no Change password.** Use the
web app for those.

### The four tabs

**Home.** Header **WorkHub**; the menu button opens your profile and the bell opens
**Recent Activities**. Greeting *"Hello, <first name>"* / *"Let's make today
productive!"*, then four tappable cards — **Employees**, **Projects**, **Tasks**,
**Completed** — each drilling into the matching screen. Admins and Managers also get a
**Reports & Analytics** card (*"Task, project and people performance"*). Then **Recent
Activities** with **View All**. Pull down to refresh.

**Projects.** A read-only list of the projects you can see, each with its status,
progress bar and task count. There is no project creation, editing or deletion on
mobile.

**Tasks.** Filter chips — **All**, **Pending**, **In Progress**, **Completed** — over a
list of tasks ordered by due date. Admins and Managers get a **+** button to create a
task. Pull down to refresh; the list also refreshes when you come back from a task.

**Profile.** Your details, with an **Edit** button that lets you change **First name**,
**Last name** and **Department** (**Save** / **Cancel**). Below that, read-only rows for
**Email**, **Department**, **Role**, your organisation **Name** and the **API** address,
and a **Log out** button that asks *"Are you sure you want to log out of WorkHub?"*
first.

### Other screens

**Task detail** (tap any task). The task's title, badges (including **Overdue**),
description; a **Details** card with **Project**, **Due date** and **Assigned to**; a
**Status** card; and **Comments (N)** with a composer and a **Post** button.

The **Status** picker appears if you are the assignee, a Manager or an Admin; an
employee sees the helper *"You can change the status of tasks assigned to you."*
Otherwise the status is read-only with *"Only the assignee, a manager or an
administrator can change this task's status."*

**Employees** (from the Home screen's Employees card). A searchable directory
(*"Search by name, email or department"*) with a role filter. An **Admin** gets a **+**
button to add someone, and edit and delete on each card — including the guard *"Cannot
delete / You cannot delete your own account."* Everyone else sees it read-only.

**Recent Activities.** The full activity feed.

**Reports** (Admin and Manager). Report chips — **Tasks**, **Projects**, **People** —
and date-range chips — **All time**, **Last 30 days**, **Last 90 days**, **This year**.
The share button hands the current report to your device's share sheet as CSV
(`workhub-tasks-report.csv`, `workhub-projects-report.csv`,
`workhub-people-report.csv`).

Two honest notes about mobile Reports, which the screen itself states:

- ~~**The date range only affects the Projects report.** For the Tasks and People reports the screen says *"The server returns all-time totals for this report — the date range is not applied to it yet."*~~ — **superseded 2026-09-17.** This was not merely stale, it was **inverted**: it credited the one report the server does *not* filter and denied the two it does. The quoted sentence no longer exists in the app — a repo-wide search for it now hits only this manual. **What actually happens:** the window is applied to **all three** reports (`mobile/app/reports.js:89` passes `rangeParams(range)` to every loader). **Tasks** and **People** are filtered **server-side** (`created_at` for tasks; `created_at`/`completed_at` for people). **Projects** is filtered **client-side**, by date overlap (`overlapsRange`, `mobile/src/utils/reportRange.js:31-36`), **because `/reports/projects` ignores date parameters altogether** — the client-side filter exists to compensate for the gap, not because projects is the only supported report. The on-screen note is now written per report by `rangeNoteFor` (`reportRange.js:81-90`) and says which dates each report is anchored on. Fixed as DEF-M-002 / DEF-032, with on-device proof (Tasks all-time 41 vs last-30-days 19) at `evidence/retest/10-mobile-android-emulator-20260911T074508Z.log:124-146`. Note that this makes mobile's date-range coverage **broader** than the web client's, which applies its window to the Employee Performance report only — see [Things that behave differently from the PRD](#things-that-behave-differently-from-the-prd).
- **The export is a share, not a file download.** The CSV goes to the system share sheet rather than being saved into your Files app; saving a real `.csv` would need Expo modules that are not installed in this project.

An Employee who reaches the Reports screen sees *"Reports are restricted"* / *"Reports
are available to managers and administrators."*

---

## 12. Known limitations in this release

This section is deliberately blunt. Everything below is either **absent from the build**
or **present but unverified**. Nothing here should be planned around as though it worked.

### Not built at all

| Item | What that means for you | Record |
|---|---|---|
| **Organisation-level settings** — *User Management*, *Organization*, *System Preferences* | There is **no organisation settings area**, for any role, including Admin. `/settings` is your own profile and password only, and says so: *"Organisation-wide settings are not part of this release."* Organisation-wide configuration, permission editing and audit logs do not exist. Deferred by an explicit product decision of 2026-09-10. | `evidence/qa/defects/DEF-008-settings-scope-and-access.md`; criterion AC-SET-1 |
| **Server-side sign-out** | There is no sign-out endpoint. **Log out** clears tokens in your browser or device only; tokens already captured elsewhere remain valid for up to 24 hours (access) / 7 days (refresh). To actually end sessions, change your password. | SEC-F-002, `docs/security.md` |
| **Notifications** | The bell in the web top bar just opens the Dashboard. There is no notification centre, no email notification for an assignment, and no mobile push. Any PRD workflow step that says "receive a notification" does not happen in this build. **Note added 2026-09-17:** until that date the bell also displayed a permanent red unread dot and announced *"Notifications, 1 unread"* to screen readers, from a hard-coded value with no data behind it — so this row was accurate while the interface contradicted it. The fabricated badge was removed (defect D-1); the bell now carries no indicator and is announced simply as *Notifications*. | Capability `notifications: false` in `.project/project.json`; `evidence/qa/fix-cycle16/D-1-GREEN-web.md` |
| **Team Activity report** | The Reports screen has Tasks by Status, Tasks by Priority, Project Progress, Employee Performance and Tasks by Project — and no Team Activity report. There is no such endpoint. The Dashboard's **Recent Activities** feed is an activity *feed*, not this report. | AC gap recorded against feature f06 |
| **Kanban board view** | Tasks are lists and tables only. There is no board or drag-and-drop view anywhere in either client. | AC gap recorded against feature f04 |
| ~~**Date-range filtering on web reports**~~ — **superseded 2026-09-17; moved** | ~~The web Reports screen has a project-status filter and sortable columns, but **no date range**; all figures are all-time. The PRD's "filter by date range" step is not implemented on web.~~ **This limitation was retired on 2026-09-17.** The filter **landed on 2026-09-16**, after this row was written, so "not built at all" became false and the row no longer belongs in this table. It is **not** fully delivered either: what remains true is a *partial* coverage limitation, restated under [Things that behave differently from the PRD](#things-that-behave-differently-from-the-prd) below. Re-measured against a live API. | `evidence/qa/fix-cycle15/U-01-date-range-remeasurement.md` |
| **Editing or deleting a comment** | Neither client offers a control to edit or delete a comment once posted, even your own. (The API has the capability; no screen uses it.) | AC gap recorded against feature f04 |
| **File attachments** | Nothing can be attached to a project, task or comment. | Capability `fileUpload: false` |
| **Offline use** | Both clients require a reachable API. There is no offline mode and no sync. | Capability `offline: false` |
| **Changing your password from the mobile app** | Mobile has no change-password, no registration and no forgotten-password flow. Use the web app. | `mobile/app/(tabs)/profile.js` |

### Built, but not verified against an acceptance criterion

These work in the interface; the project has no acceptance criterion covering them, so
no one has signed off on their behaviour. Treat them as functional but unproven.

- ~~**Deleting a task** (the bin icon on the Tasks list, and its confirmation).~~ — **superseded 2026-09-17; overstated.** Deletion is **partly** covered. The *denial* path has a criterion: **AC-RBAC-3** (`docs/acceptance-criteria.md:1476`) asserts "Employee cannot delete tasks (403)". What has no criterion is the **happy path** — an Admin or Manager successfully deleting a task, the confirmation dialog, and what the list does afterwards. So: the permission rule is signed off; the successful deletion is not.
- **Deleting a comment** via the API, and the permission rule that should govern it.
- **CSV export format.** Export is described in a criterion only in passing; neither the file format nor the download itself has a criterion of its own.
- **Report empty and error states**, and the report generation-time target.
- **Access-token expiry and silent refresh.** Your session renewing itself behind the scenes has no criterion.

### Things that behave differently from the PRD

- **Self-registration always creates an Employee.** There is no way to register as a Manager or an Admin; an Admin must change the role afterwards.
- **Every signed-in user can browse the whole employee directory.** The PRD describes an Employee's view of users as "Limited"; in this build the directory is not narrowed by role — only its *editing* is.
- **The web Reports date range covers one report out of five.** The date-range filter on the web Reports screen (added 2026-09-16) applies to the **Employee Performance** report **only**. **Tasks by Status**, **Tasks by Priority**, **Tasks by Project** and **Project Progress** are not re-read when a window is applied and remain **all-time**, so the PRD's "filter by date range" step is **partly** implemented on web rather than absent. Measured against a live API on 2026-09-17 — applying a window issued exactly one request, for the employee report. The API itself would honour a window on the task figures, but the web client does not send one; `/reports/projects` ignores date parameters altogether. The **mobile** client's coverage differs: ~~section 11's account of it is flagged as stale on 2026-09-17 and is awaiting its own re-measurement by the agent that owns `mobile/`.~~ **re-measured and corrected 2026-09-17** — mobile applies its window to **all three** of its reports, so on this point mobile is **ahead** of web, not behind it. See [section 11](#11-the-mobile-app). Recorded in `evidence/qa/fix-cycle15/U-01-date-range-remeasurement.md` and `evidence/qa/fix-cycle16/D-2-section11-mobile-date-range.md`.
- **Settings is available to every role.** An earlier criterion said a Manager should be refused `/settings`. That criterion was judged defective — it would have locked Managers and Employees out of their own passwords — and was rewritten on 2026-09-10 so that only *organisation-level* settings are Admin-only. Personal settings are correctly open to all three roles.

### Operational cautions

- **The demo password is committed to the repository** — ~~(`DEMO_PASSWORD` in `backend/apps/common/management/commands/seed_demo.py`)~~ **citation superseded 2026-09-17.** The conclusion stands; the file named was wrong. `backend/` is **gitignored and untracked** (`.gitignore:88` is `/backend/`; `git ls-files backend` returns **0** files), so the `DEMO_PASSWORD = "WorkHub#2026"` at `seed_demo.py:107` is on disk but was never committed. The password **is** committed, at a different path: `integration/probe_secf019_task_project_move.py:34`, which **is** tracked. Tracked as **SEC-F-023** and escalated to the user. Seeded accounts remain local-development only. Previously recorded as SEC-F-006 / SEC-F-010.
- **Password-reset email needs real SMTP** — ~~until it is configured, reset links are printed to the server console and no user will receive one.~~ **superseded 2026-09-17; the second half was inverted.** Reset links are **not** printed to the console, and that is a security control rather than a gap. `EMAIL_BACKEND` defaults to `django.core.mail.backends.smtp.EmailBackend` (`backend/config/settings.py:240-242`) **deliberately**: the reset token appears in the email and nowhere else, so the default backend is the *non-disclosing* one — *"A missing or empty configuration must fail to deliver, never fall back to disclosure — see SEC-F-001"* (`settings.py:236-238`). Console and file backends are **opt-in**, and choosing one with `DJANGO_DEBUG` off raises a `RuntimeWarning` naming the risk (`settings.py:266-274`). **So the real behaviour of an unconfigured install is: nothing is delivered and nothing is printed.** A reset that appears to do nothing means SMTP needs configuring — it does not mean the link is waiting in the server log.
- ~~**The mobile app has never been run on a device or simulator here**, and there is no store build configuration.~~ — **superseded 2026-09-17.** One claim covering three different facts, and it is now false for one of them. Split:
  - **Android — no longer a limitation.** The app has been run on an Android emulator (AVD `WorkHub_Pixel4_API34`, Android 14) with 19 screenshots captured: `evidence/retest/10-mobile-android-emulator-20260911T074508Z.log` and `evidence/implementation/mobile/android-emulator-20260911T073507Z/`, plus a second session at `evidence/qa/mobile/orchestrator-device-verification-20260914T0620Z/`.
  - **iOS — still a real limitation, and it has not gone away.** The app has **never** been launched on an iOS simulator or device. `xcrun simctl` is absent on this host (only CommandLineTools is installed), so it cannot be. Tracked as **BLK-001**, re-verified 2026-09-17; evidence `evidence/retest/mobile-ios-simulator-BLOCKED-blk-001-20260914T051500Z.txt`. Its status is `BLOCKED`, not `PASS` — the Android run above does **not** stand in for it.
  - **Store build configuration — still absent, on both platforms.** There is no `eas.json` anywhere in the repository. `mobile/app.json` declares bundle identifiers but no build profiles and no signing configuration, so neither an App Store nor a Play Store build can be produced from this tree.

  See [section 11](#11-the-mobile-app).
- **`manage.py runserver` is a development server** and must not be used to serve real users; see `docs/deployment.md`.

---

## Where to look next

| If you want | Read |
|---|---|
| What the product is meant to do | `docs/PRD.md`, `docs/project-overview.md` |
| The precise, testable behaviour expected of each screen | `docs/acceptance-criteria.md` |
| The API behind both clients | `docs/api-contract.md`, and Swagger UI at `/api/docs` |
| How to install, configure and run it | `docs/deployment.md` |
| What is known to be insecure or unfinished | `docs/security.md` |
| Which screens were actually reached in a real browser | `evidence/playwright/routes.md` |
| Where each statement in this manual came from | `evidence/release/user-manual-sources.md` |
