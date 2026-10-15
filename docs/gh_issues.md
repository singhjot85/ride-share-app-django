# LoadShare POC: GitHub Issues & Sub-issues Breakdown

Every item below is a GitHub issue with a title, a description and labels; each issue is split into sub-issues small enough to finish in one to two days.

## How to use this doc

- **Phase:** a GitHub milestone (and a `phase:` label), not an issue. It groups the issues that ship together.
- **Issue:** one deliverable inside a phase (for example, "Driver route publishing API"). It has a title, a description with acceptance criteria, and labels.
- **Sub-issue:** one concrete task under an issue. It uses the same three fields and is added through GitHub's sub-issues feature on the parent issue.
- **IDs:** each item carries a short ID (`P1-03` for an issue, `P1-03a` for its sub-issue). The ID is only for this doc and for cross-references; do not put it in the GitHub title.
- **Titles:** start with a verb and name the outcome, for example "Build route publishing endpoint".
- **Descriptions:** one or two sentences of what and why, then the acceptance criteria as a `- [ ]` list.
- **Dependencies:** where an issue needs another one first, it says "Depends on" with the ID.
- **Creating them:** create parent issues first, then sub-issues, then link each sub-issue to its parent. The labels in the next section must exist in the repository before you start.

## Label scheme

Labels use a `group: value` format so they sort together in GitHub. Every issue and sub-issue gets exactly one `type`, one `area`, one `phase` and one `priority` label; the two extra labels are optional. Add more `area:` values as the team needs them.

| Label | Description |
| --- | --- |
| `type: feature` | A user-visible capability |
| `type: task` | Engineering work with no direct user-visible change |
| `type: spike` | Time-boxed investigation that ends in a decision or a finding |
| `type: chore` | Setup, tooling, config, housekeeping |
| `type: docs` | Documentation, runbooks, READMEs |
| `type: test` | Tests and test data |
| `type: bug` | Something that is broken |
| `area: backend` | Django, DRF, Celery, business logic |
| `area: database` | Schema, migrations, PostGIS queries |
| `area: android` | Native Android driver app |
| `area: web` | React sender web app |
| `area: ops-panel` | Django admin customisation |
| `area: infra` | Docker, EC2, CI/CD, monitoring |
| `area: integrations` | MSG91, FCM, Razorpay, routing engine, map tiles |
| `area: product` | Decisions, policy and pilot planning with no code |
| `phase: 0` to `phase: 5` | The POC phase the item belongs to. Use phase: post-poc for work reserved for after the POC (six phase labels plus one) |
| `priority: high` | Blocks the phase exit criteria |
| `priority: medium` | Needed for the phase but not blocking |
| `priority: low` | Nice to have; drop first if the phase slips |
| `risk: critical` | Optional. One of the two make-or-break risks (background location, routing accuracy) |
| `blocked` | Optional. Waiting on an outside party (for example SMS DLT approval) |

Create the labels once in the repository, then use the same names in every issue below.

## Issues by phase

The six phases come from the POC plan (about 10-11 weeks). Rows starting with a plain ID are issues; rows starting with an arrow are their sub-issues.

### Phase 0: Decisions and foundation (\~1 week)

Exit criteria: schema agreed; `docker compose up` works for everyone; map tile and routing providers chosen.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P0-01 | Decide pilot corridor and pickup/drop model | Fix the geography and stop model so matching has something concrete to work against. Done when the decision is written into `docs/`. | `type: task` `area: product` `phase: 0` `priority: high` |
| P0-01a | ↳ Choose the pilot corridor | Pick one highway corridor where 10-20 drivers can be onboarded personally. Record the city pair and typical trip length. | `type: task` `area: product` `phase: 0` `priority: high` |
| P0-01b | ↳ Define pickup and drop points | Use transport yards or fixed on-route stops with a 3-5 km match radius. List the initial stops with coordinates. | `type: task` `area: product` `phase: 0` `priority: high` |
| P0-01c | ↳ Decide first and last mile responsibility | State who moves the parcel from the sender to the pickup point and from the drop point to the receiver. | `type: task` `area: product` `phase: 0` `priority: medium` |
| P0-02 | Define pricing and parcel rules | Settle the commercial rules the app will enforce, so Phases 2 and 5 do not stall on policy questions. | `type: task` `area: product` `phase: 0` `priority: high` |
| P0-02a | ↳ Define the pricing formula | Flat rupees per kg by route segment, plus a platform fee. Give one worked example. | `type: task` `area: product` `phase: 0` `priority: high` |
| P0-02b | ↳ Define parcel rules | Capacity in kg only. Hazardous goods prohibited. Set a maximum weight and size per parcel. | `type: task` `area: product` `phase: 0` `priority: medium` |
| P0-02c | ↳ Define cancellation and no-show policy | A lightweight version, needed before Phase 3 builds cancellation. | `type: task` `area: product` `phase: 0` `priority: low` |
| P0-03 | Design the domain model and state machine | Agree the data model and booking lifecycle before any migration is written. | `type: task` `area: database` `phase: 0` `priority: high` |
| P0-03a | ↳ Draw the ERD | Cover User, Vehicle, Route, ParcelRequest, Booking and StatusEvent, with PostGIS fields marked. | `type: docs` `area: database` `phase: 0` `priority: high` |
| P0-03b | ↳ Define the booking state machine | States: Requested, Accepted, Picked Up, In Transit, Delivered, Completed, Cancelled, Rejected/Expired. Define allowed transitions and who triggers each. | `type: docs` `area: backend` `phase: 0` `priority: high` |
| P0-03c | ↳ Review and record the schema | Team review, then save as `docs/architecture/data-models.md`. | `type: docs` `area: backend` `phase: 0` `priority: medium` |
| P0-04 | Set up the repository and local environment | One command brings up the full backend stack for every developer. | `type: chore` `area: infra` `phase: 0` `priority: high` |
| P0-04a | ↳ Create the repository structure | Add `backend/`, `frontend/`, `android/` and `docs/`, with the three READMEs. | `type: chore` `area: infra` `phase: 0` `priority: high` |
| P0-04b | ↳ Write the Docker Compose setup | Services: Django, Postgres with PostGIS, Redis, Celery worker and Celery beat. | `type: chore` `area: infra` `phase: 0` `priority: high` |
| P0-04c | ↳ Split settings and add `.env.example` | Settings in `config/`, split into constants, variables and resolvers. No secrets in the repo. | `type: chore` `area: backend` `phase: 0` `priority: medium` |
| P0-04d | ↳ Add the CI pipeline | Lint and run tests on every pull request. | `type: chore` `area: infra` `phase: 0` `priority: medium` |
| P0-05 | Set up the staging environment | A shared box where real devices can reach the API. | `type: chore` `area: infra` `phase: 0` `priority: medium` |
| P0-05a | ↳ Provision the EC2 instance | One VM in ap-south-1 with Docker installed and a locked-down security group. | `type: chore` `area: infra` `phase: 0` `priority: medium` |
| P0-05b | ↳ Add the deploy pipeline | Deploy `main` to staging automatically after CI passes. | `type: chore` `area: infra` `phase: 0` `priority: medium` |
| P0-05c | ↳ Add a domain and HTTPS | Needed for FCM, Razorpay callbacks and real-device testing. | `type: chore` `area: infra` `phase: 0` `priority: low` |

Phase 0, continued: accounts, spikes and compliance.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P0-06 | Set up third-party accounts | Create every external account early, since some have approval delays. | `type: task` `area: integrations` `phase: 0` `priority: high` |
| P0-06a | ↳ Start MSG91 DLT registration | Submit sender ID and OTP templates. This has the longest lead time of any item in the POC. | `type: task` `area: integrations` `phase: 0` `priority: high` `blocked` |
| P0-06b | ↳ Create the Firebase project and FCM credentials | Needed for driver push notifications in Phase 3. | `type: task` `area: integrations` `phase: 0` `priority: medium` |
| P0-06c | ↳ Choose and sign up for a map tile provider | Use a provider's free tier, not the public OSM tile server. | `type: task` `area: integrations` `phase: 0` `priority: medium` |
| P0-06d | ↳ Get OpenRouteService and Razorpay test credentials | ORS with the HGV profile; Razorpay in test mode. | `type: task` `area: integrations` `phase: 0` `priority: medium` |
| P0-07 | Spike: background location on a budget Android phone | Prove the driver app can keep sending location for a full trip. If this fails, the plan changes. | `type: spike` `area: android` `phase: 0` `priority: high` `risk: critical` |
| P0-07a | ↳ Build a minimal foreground location service | A throwaway app that sends a ping to a test endpoint every 15-30 seconds. | `type: spike` `area: android` `phase: 0` `priority: high` `risk: critical` |
| P0-07b | ↳ Run a 6+ hour test on a budget phone | Record the gaps between pings and battery drain with the screen off. | `type: spike` `area: android` `phase: 0` `priority: high` `risk: critical` |
| P0-07c | ↳ Write up findings and a go/no-go | State what broke, which phone settings were needed, and whether to proceed. | `type: docs` `area: android` `phase: 0` `priority: high` `risk: critical` |
| P0-08 | Spike: routing geometry on the pilot corridor | Prove the routing provider returns sane truck routes for the chosen corridor. | `type: spike` `area: integrations` `phase: 0` `priority: high` `risk: critical` |
| P0-08a | ↳ Request HGV routes for the corridor | Call ORS for several origin and destination pairs on the corridor. | `type: spike` `area: integrations` `phase: 0` `priority: high` `risk: critical` |
| P0-08b | ↳ Check geometry against known highways | Compare the returned lines with the real highway and note any wrong turns or restricted roads. | `type: spike` `area: integrations` `phase: 0` `priority: high` `risk: critical` |
| P0-08c | ↳ Record findings and confirm the routing provider | Keep ORS or switch. This also settles the engine the spreadsheet marks as assumed. | `type: docs` `area: integrations` `phase: 0` `priority: medium` `risk: critical` |
| P0-09 | Compile open compliance questions | Not built in the POC, but answers are needed before the pilot goes live. | `type: docs` `area: product` `phase: 0` `priority: low` |
| P0-09a | ↳ List the legal questions | Goods-carriage permits for third-party goods, consignment note, e-Way Bill threshold, and rules on holding customer funds. | `type: docs` `area: product` `phase: 0` `priority: low` |
| P0-09b | ↳ Get answers from a transport or tax professional | Record the answers and any changes they force on the pilot design. | `type: task` `area: product` `phase: 0` `priority: low` |

### Phase 1: Accounts and ops back-office (\~2 weeks)

Exit criteria: a driver can sign up, upload documents and be approved by an admin.

Backend and ops panel.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P1-01 | Build phone and OTP login | Users sign in with a phone number and a one-time code, as either a Driver or a Sender. Depends on P0-06a for live SMS; use a console backend until then. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-01a | ↳ Create the User model with roles | Phone number as the identifier; roles Driver and Sender. | `type: task` `area: database` `phase: 1` `priority: high` |
| P1-01b | ↳ Build OTP request and verify endpoints | Code expiry, attempt limits and rate limiting per phone number. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-01c | ↳ Add the MSG91 SMS client | Behind a service interface so a console backend can replace it in development and tests. | `type: task` `area: integrations` `phase: 1` `priority: high` |
| P1-01d | ↳ Add token auth and role permissions | Issue tokens after verification; enforce role checks on every endpoint. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-01e | ↳ Test the login flow | Unit tests with SMS mocked, plus one end-to-end test. | `type: test` `area: backend` `phase: 1` `priority: medium` |
| P1-02 | Build driver profile and vehicle details | A driver records who they are and what they drive, so admins can verify them. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-02a | ↳ Create the DriverProfile and Vehicle models | Vehicle type, registration number, capacity in kg. | `type: task` `area: database` `phase: 1` `priority: high` |
| P1-02b | ↳ Build profile and vehicle endpoints | Create, read and update for the signed-in driver only. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-02c | ↳ Add document photo upload | Licence, registration and vehicle photos. Keep storage behind an interface so S3 can replace local files after the POC. | `type: feature` `area: backend` `phase: 1` `priority: high` |
| P1-02d | ↳ Validate uploads | Allowed file types and a maximum size; reject everything else with a custom error. | `type: task` `area: backend` `phase: 1` `priority: medium` |
| P1-03 | Build manual KYC approval in Django admin | An admin reviews documents and approves or rejects the driver. No third-party KYC service. | `type: feature` `area: ops-panel` `phase: 1` `priority: high` |
| P1-03a | ↳ Add a verification status to drivers | States: Pending, Approved, Rejected, each with a reason and a reviewer. | `type: task` `area: database` `phase: 1` `priority: high` |
| P1-03b | ↳ Build admin review screen and actions | Show documents inline; approve and reject actions that require a reason. | `type: feature` `area: ops-panel` `phase: 1` `priority: high` |
| P1-03c | ↳ Block unapproved drivers from publishing routes | A permission check Phase 2 will use. | `type: task` `area: backend` `phase: 1` `priority: high` |
| P1-03d | ↳ Tell the driver the outcome | Send an SMS on approval or rejection. | `type: feature` `area: integrations` `phase: 1` `priority: medium` |
| P1-04 | Set up Django admin as the ops panel | The ops team can find and fix data without developer help. | `type: task` `area: ops-panel` `phase: 1` `priority: medium` |
| P1-04a | ↳ Register users, vehicles and documents | Searchable lists with useful filters. | `type: task` `area: ops-panel` `phase: 1` `priority: medium` |
| P1-04b | ↳ Create staff roles and permissions | Separate groups for admins and support staff. | `type: task` `area: ops-panel` `phase: 1` `priority: low` |
| P1-05 | Lay API foundations | Shared conventions every later endpoint relies on. | `type: chore` `area: backend` `phase: 1` `priority: high` |
| P1-05a | ↳ Add the OpenAPI schema | drf-spectacular, served at `/api/schema/`. | `type: chore` `area: backend` `phase: 1` `priority: medium` |
| P1-05b | ↳ Add custom errors and pagination | One error format; pagination on every list endpoint. | `type: chore` `area: backend` `phase: 1` `priority: high` |
| P1-05c | ↳ Add test base classes and fixtures | Authenticated API client helpers and seed users. | `type: test` `area: backend` `phase: 1` `priority: medium` |

Phase 1, client apps.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P1-06 | Build the driver sign-up flow in the Android app | A new driver can register, upload documents and see their approval status. | `type: feature` `area: android` `phase: 1` `priority: high` |
| P1-06a | ↳ Create the Android project | Kotlin, Jetpack Compose, navigation, networking layer and build variants for staging. | `type: chore` `area: android` `phase: 1` `priority: high` |
| P1-06b | ↳ Build the OTP login screens | Phone entry, code entry, resend and error states. | `type: feature` `area: android` `phase: 1` `priority: high` |
| P1-06c | ↳ Build the profile and vehicle screens | Collect driver and vehicle details. | `type: feature` `area: android` `phase: 1` `priority: high` |
| P1-06d | ↳ Build document capture and upload | Take or pick a photo, compress it, upload it, and retry on a weak network. | `type: feature` `area: android` `phase: 1` `priority: high` |
| P1-06e | ↳ Show the approval status | Pending, Approved or Rejected, with the rejection reason. | `type: feature` `area: android` `phase: 1` `priority: medium` |
| P1-07 | Build the sender sign-up flow on the web | A sender can sign in on the web app with their phone number. | `type: feature` `area: web` `phase: 1` `priority: high` |
| P1-07a | ↳ Create the React app | React, TypeScript and Vite, with the folder structure from the frontend README. | `type: chore` `area: web` `phase: 1` `priority: high` |
| P1-07b | ↳ Add Hindi and English translations | A language switch and a locale file structure the later screens will reuse. | `type: task` `area: web` `phase: 1` `priority: medium` |
| P1-07c | ↳ Set up the API service layer and auth store | One shared API instance; no direct requests from components. | `type: task` `area: web` `phase: 1` `priority: high` |
| P1-07d | ↳ Build the OTP login screens | Phone entry, code entry, resend and error states. | `type: feature` `area: web` `phase: 1` `priority: high` |

### Phase 2: Routes and matching (\~2 weeks)

Exit criteria: on seeded corridor data, a request returns the right drivers in under 2 seconds; hand-checked cases pass, including a wrong-direction case that must not match.

Backend and data.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P2-01 | Build route publishing | An approved driver publishes a route with a departure time, spare capacity and price. Depends on P0-08c and P1-03c. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-01a | ↳ Create the Route model | Origin, destination, optional waypoints, departure time, capacity in kg, price, and a PostGIS LineString. | `type: task` `area: database` `phase: 2` `priority: high` |
| P2-01b | ↳ Add the routing engine client | Fetch the HGV route from OpenRouteService behind a service interface so OSRM or Valhalla can replace it later. | `type: task` `area: integrations` `phase: 2` `priority: high` |
| P2-01c | ↳ Build route create, list and cancel endpoints | Geometry is generated server-side from the routing engine, never trusted from the client. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-01d | ↳ Handle routing failures | Timeouts and provider errors give the driver a clear message and are logged. | `type: task` `area: backend` `phase: 2` `priority: medium` |
| P2-02 | Build parcel requests | A sender describes a parcel and where it should go. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-02a | ↳ Create the ParcelRequest model | Pickup and drop points, weight, description, desired date window. | `type: task` `area: database` `phase: 2` `priority: high` |
| P2-02b | ↳ Build parcel request endpoints | Create, list and cancel, for the owning sender only. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-02c | ↳ Enforce parcel rules | Reject over-weight parcels and prohibited goods, using the rules from P0-02b. | `type: task` `area: backend` `phase: 2` `priority: medium` |
| P2-03 | Build rule-based matching | Given a parcel request, return suitable routes, best first. No ML. | `type: feature` `area: database` `phase: 2` `priority: high` `risk: critical` |
| P2-03a | ↳ Match by distance to the route | `ST_DWithin` of pickup and of drop against the route line, within the 3-5 km radius from P0-01b. | `type: feature` `area: database` `phase: 2` `priority: high` |
| P2-03b | ↳ Match by direction | Pickup must come before drop along the route, using `ST_LineLocatePoint`. A wrong-direction parcel must not match. | `type: feature` `area: database` `phase: 2` `priority: high` `risk: critical` |
| P2-03c | ↳ Filter by capacity and time window | Remaining kg must cover the parcel; departure must fall in the sender's window. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-03d | ↳ Add a weighted score | Combine distance, price and departure time into one ranking. | `type: feature` `area: backend` `phase: 2` `priority: medium` |
| P2-03e | ↳ Add spatial indexes and measure speed | GiST indexes on route geometry; confirm results return in under 2 seconds on seeded data. | `type: task` `area: database` `phase: 2` `priority: high` |
| P2-04 | Build the corridor seed script and matching tests | A repeatable dataset to prove matching works and keep it working. | `type: test` `area: backend` `phase: 2` `priority: high` |
| P2-04a | ↳ Write the seed script | Realistic drivers, routes and parcels along the pilot corridor. | `type: chore` `area: backend` `phase: 2` `priority: high` |
| P2-04b | ↳ Write hand-checked matching cases | Include wrong direction, too far from the route, over capacity and wrong date. | `type: test` `area: backend` `phase: 2` `priority: high` |

Phase 2, requests and client apps.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P2-05 | Build the driver request inbox with accept and reject | Drivers see parcel requests that match their routes and respond to each. Full booking states arrive in Phase 3; here a response is stored on the request. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-05a | ↳ Link matched requests to routes | Store which requests were offered to which routes and the driver's response. | `type: task` `area: database` `phase: 2` `priority: high` |
| P2-05b | ↳ Build inbox, accept and reject endpoints | A driver can only act on requests offered to their own routes. | `type: feature` `area: backend` `phase: 2` `priority: high` |
| P2-06 | Build route publishing in the Android app | A driver creates a route on the phone. | `type: feature` `area: android` `phase: 2` `priority: high` |
| P2-06a | ↳ Build the route form | Origin, destination, optional waypoints, departure, capacity in kg and price. | `type: feature` `area: android` `phase: 2` `priority: high` |
| P2-06b | ↳ Show the route on a map | Draw the returned geometry and let the driver confirm it. | `type: feature` `area: android` `phase: 2` `priority: medium` |
| P2-06c | ↳ List and cancel my routes | Upcoming and past routes with a cancel action. | `type: feature` `area: android` `phase: 2` `priority: medium` |
| P2-07 | Build the request inbox in the Android app | A driver reviews matching requests and answers them. | `type: feature` `area: android` `phase: 2` `priority: high` |
| P2-07a | ↳ Build the request list and detail screens | Show pickup, drop, weight, price and where the parcel sits on the route. | `type: feature` `area: android` `phase: 2` `priority: high` |
| P2-07b | ↳ Add accept and reject actions | Confirm before sending; show a clear result. | `type: feature` `area: android` `phase: 2` `priority: high` |
| P2-08 | Build parcel requests and match results on the web | A sender creates a request and sees matching drivers on a map. | `type: feature` `area: web` `phase: 2` `priority: high` |
| P2-08a | ↳ Set up the map component | Leaflet or MapLibre with the chosen tile provider, wrapped in one reusable component. | `type: task` `area: web` `phase: 2` `priority: high` |
| P2-08b | ↳ Build the parcel request form | Pickup and drop selection from the pilot stops, weight, description and date window. | `type: feature` `area: web` `phase: 2` `priority: high` |
| P2-08c | ↳ Build the match results view | Ranked list with the route drawn on the map and the pickup and drop points marked. | `type: feature` `area: web` `phase: 2` `priority: high` |
| P2-08d | ↳ Handle empty and error states | No matches, routing errors and slow responses, in Hindi and English. | `type: task` `area: web` `phase: 2` `priority: low` |

### Phase 3: Booking lifecycle and notifications (\~2 weeks)

Exit criteria: a full booking runs end to end on staging with real devices.

Backend.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P3-01 | Build the booking model and state machine | A booking moves through a fixed set of states, and every change is recorded. Uses the design from P0-03b. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-01a | ↳ Create the Booking and StatusEvent models | StatusEvent is append-only and stores the actor and a timestamp. | `type: task` `area: database` `phase: 3` `priority: high` |
| P3-01b | ↳ Implement the transition rules | Requested, Accepted, Picked Up, In Transit, Delivered, Completed, plus Cancelled and Rejected/Expired. Reject any transition not allowed. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-01c | ↳ Build booking endpoints | Create from an accepted request, read, and trigger each transition with the right role. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-01d | ↳ Test every transition | A table-driven test covering allowed and forbidden transitions. | `type: test` `area: backend` `phase: 3` `priority: high` |
| P3-02 | Build proof of pickup and delivery | Each handover is confirmed by a one-time code and a photo. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-02a | ↳ Generate and verify handover codes | A code for pickup and another for delivery, valid only for that booking. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-02b | ↳ Store proof photos | One photo at pickup and one at delivery, attached to the status event. | `type: feature` `area: backend` `phase: 3` `priority: medium` |
| P3-02c | ↳ Record verified weight at pickup | A lightweight weight check, since weight is a common dispute. | `type: feature` `area: backend` `phase: 3` `priority: medium` |
| P3-03 | Build request expiry and cancellation | Stale requests close themselves, and either side can cancel with a reason. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-03a | ↳ Add the Celery beat expiry task | Expire requests that no driver answers within a set time. | `type: feature` `area: backend` `phase: 3` `priority: high` |
| P3-03b | ↳ Build cancellation with reason | Follow the policy from P0-02c. | `type: feature` `area: backend` `phase: 3` `priority: medium` |
| P3-04 | Build notifications | The right person hears about each change. | `type: feature` `area: integrations` `phase: 3` `priority: high` |
| P3-04a | ↳ Register device tokens | Store the FCM token per driver device and refresh it when it changes. | `type: task` `area: backend` `phase: 3` `priority: high` |
| P3-04b | ↳ Send FCM push to drivers | A Celery task triggered by booking events. | `type: feature` `area: integrations` `phase: 3` `priority: high` |
| P3-04c | ↳ Send SMS or in-app updates to senders | Choose SMS for key events and in-app for the rest. | `type: feature` `area: integrations` `phase: 3` `priority: medium` |
| P3-04d | ↳ Reveal phone numbers after acceptance | Return the other party's number with a call and WhatsApp deep link. No in-app chat. | `type: feature` `area: backend` `phase: 3` `priority: medium` |

Phase 3, client apps.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P3-05 | Build the booking flow in the Android app | A driver runs a booking from acceptance to completion. | `type: feature` `area: android` `phase: 3` `priority: high` |
| P3-05a | ↳ Receive push notifications | Register the FCM token, show notifications, and open the right booking when tapped. | `type: feature` `area: android` `phase: 3` `priority: high` |
| P3-05b | ↳ Build the active booking screen | Shows current state and only the actions allowed next. | `type: feature` `area: android` `phase: 3` `priority: high` |
| P3-05c | ↳ Build pickup and delivery confirmation | Enter the handover code, take the proof photo and record the weight. | `type: feature` `area: android` `phase: 3` `priority: high` |
| P3-05d | ↳ Add an offline queue for actions | Room-backed queue so confirmations made without a signal are sent later. | `type: feature` `area: android` `phase: 3` `priority: medium` |
| P3-06 | Build the booking flow on the web | A sender books a driver and follows the booking. | `type: feature` `area: web` `phase: 3` `priority: high` |
| P3-06a | ↳ Build the booking confirmation screen | Show price, route and the driver's details after acceptance. | `type: feature` `area: web` `phase: 3` `priority: high` |
| P3-06b | ↳ Build the booking status timeline | Show each recorded status event with its time. | `type: feature` `area: web` `phase: 3` `priority: high` |
| P3-06c | ↳ Show handover codes and the contact options | Display the code the sender gives the driver and the call and WhatsApp links. | `type: feature` `area: web` `phase: 3` `priority: medium` |
| P3-06d | ↳ Add cancellation | Cancel with a reason, following the policy. | `type: feature` `area: web` `phase: 3` `priority: medium` |
| P3-07 | Run an end-to-end booking on staging | Prove the whole flow with real phones before moving on. | `type: test` `area: infra` `phase: 3` `priority: high` |
| P3-07a | ↳ Write the end-to-end test script | Step by step from sign-up to completed booking, listing the expected state at each step. | `type: test` `area: backend` `phase: 3` `priority: high` |
| P3-07b | ↳ Run it on real devices | At least two real phones, one in each role, on mobile data. File a bug for each failure. | `type: test` `area: android` `phase: 3` `priority: high` |

### Phase 4: Live tracking (\~2 weeks)

Exit criteria: a real truck trip shows location updates with acceptable gaps; battery impact is measured.

Backend.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P4-01 | Build the location ingestion API | The driver app sends batches of location points, and the server stores them cheaply. Depends on P0-07c. | `type: feature` `area: backend` `phase: 4` `priority: high` |
| P4-01a | ↳ Create the breadcrumb model | Booking, point, timestamp and accuracy. Plan for time-based growth. | `type: task` `area: database` `phase: 4` `priority: high` |
| P4-01b | ↳ Build the batch ingestion endpoint | Accept many points per request; ignore duplicates and out-of-order points. | `type: feature` `area: backend` `phase: 4` `priority: high` |
| P4-01c | ↳ Keep the latest position in Redis | One key per active booking, with an expiry. | `type: feature` `area: backend` `phase: 4` `priority: high` |
| P4-01d | ↳ Store breadcrumbs asynchronously | Write to Postgres from a Celery task so the request stays fast. | `type: task` `area: backend` `phase: 4` `priority: medium` |
| P4-02 | Build the tracking read API | A sender fetches the truck's latest position and an ETA. | `type: feature` `area: backend` `phase: 4` `priority: high` |
| P4-02a | ↳ Build the latest-position endpoint | Read from Redis; allowed only for the sender on that booking. | `type: feature` `area: backend` `phase: 4` `priority: high` |
| P4-02b | ↳ Add a basic ETA | Ask the routing engine for the time from the last point to the drop point, cached for a short time. | `type: feature` `area: integrations` `phase: 4` `priority: medium` |
| P4-02c | ↳ Build the trip history endpoint | Return breadcrumbs for a finished booking, for ops use. | `type: feature` `area: backend` `phase: 4` `priority: low` |

Client apps.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P4-03 | Build the location service in the Android app | The app keeps reporting location for the whole trip, even in the background. | `type: feature` `area: android` `phase: 4` `priority: high` `risk: critical` |
| P4-03a | ↳ Build the foreground location service | A persistent notification, with pings every 15-30 seconds while a booking is in transit. | `type: feature` `area: android` `phase: 4` `priority: high` `risk: critical` |
| P4-03b | ↳ Batch pings and send them with WorkManager | Send in groups to save battery and data. | `type: feature` `area: android` `phase: 4` `priority: high` |
| P4-03c | ↳ Queue pings offline in Room | Hold points while there is no signal and upload when it returns. | `type: feature` `area: android` `phase: 4` `priority: high` |
| P4-03d | ↳ Handle permissions and battery restrictions | Guide the driver through location permission and vendor battery settings found in the P0-07 spike. | `type: feature` `area: android` `phase: 4` `priority: high` `risk: critical` |
| P4-03e | ↳ Start and stop with the booking state | Begin on pickup, end on delivery, and never leave the service running after a trip. | `type: task` `area: android` `phase: 4` `priority: medium` |
| P4-04 | Build the live tracking page on the web | A sender watches the truck move toward the drop point. | `type: feature` `area: web` `phase: 4` `priority: high` |
| P4-04a | ↳ Poll for the latest position | Refresh every 10-15 seconds, and stop when the tab is hidden or the booking ends. | `type: feature` `area: web` `phase: 4` `priority: high` |
| P4-04b | ↳ Show the truck and the route on the map | Truck marker, route line, and pickup and drop points. | `type: feature` `area: web` `phase: 4` `priority: high` |
| P4-04c | ↳ Show the ETA and last-seen time | Make a stale position obvious. | `type: feature` `area: web` `phase: 4` `priority: medium` |
| P4-05 | Run a real trip and measure it | The proof that tracking works on the road. | `type: test` `area: android` `phase: 4` `priority: high` `risk: critical` |
| P4-05a | ↳ Run a real truck trip with tracking on | Record every gap longer than a minute, with where and why. | `type: test` `area: android` `phase: 4` `priority: high` `risk: critical` |
| P4-05b | ↳ Measure battery and data use | Report percent battery per hour and megabytes per trip. | `type: test` `area: android` `phase: 4` `priority: medium` |

### Phase 5: Simple money and pilot hardening (\~1-2 weeks)

Exit criteria: the pilot launches with 10-20 real drivers, and route-publish rate, match rate and completed trips are tracked.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| P5-01 | Show a price breakdown before booking | The sender sees what they will pay and why. Uses the formula from P0-02a. | `type: feature` `area: backend` `phase: 5` `priority: high` |
| P5-01a | ↳ Build the price calculation | Base rate times weight by segment, plus the platform fee, stored on the booking. | `type: feature` `area: backend` `phase: 5` `priority: high` |
| P5-01b | ↳ Show the breakdown on web and Android | The same figures on both clients, before and after booking. | `type: feature` `area: web` `phase: 5` `priority: high` |
| P5-02 | Record payments | Prove the payment integration without holding customer funds. No escrow, no payouts. | `type: feature` `area: integrations` `phase: 5` `priority: high` |
| P5-02a | ↳ Create the Payment model | Amount, method, status and a reference, linked to the booking. | `type: task` `area: database` `phase: 5` `priority: high` |
| P5-02b | ↳ Integrate Razorpay in test mode | Create an order, take a test payment and verify the signature. | `type: feature` `area: integrations` `phase: 5` `priority: high` |
| P5-02c | ↳ Add offline payment recording | Ops marks a booking as paid outside the app, such as by UPI, from Django admin. | `type: feature` `area: ops-panel` `phase: 5` `priority: medium` |
| P5-03 | Generate PDF receipts | A simple receipt for each completed booking. | `type: feature` `area: backend` `phase: 5` `priority: medium` |
| P5-03a | ↳ Build the receipt template and generator | Booking, route, parties, price breakdown and payment reference. | `type: feature` `area: backend` `phase: 5` `priority: medium` |
| P5-03b | ↳ Generate and send it with a Celery task | Triggered on completion; available to download from the web app. | `type: feature` `area: backend` `phase: 5` `priority: low` |
| P5-04 | Prepare for the pilot | Everything the team needs to run the pilot without surprises. | `type: chore` `area: infra` `phase: 5` `priority: high` |
| P5-04a | ↳ Add structured logging | Consistent logs with request and booking identifiers, readable on the staging box. | `type: chore` `area: infra` `phase: 5` `priority: medium` |
| P5-04b | ↳ Write the production deploy and seed scripts | A repeatable deploy and a script that loads the initial stops and an admin user. | `type: chore` `area: infra` `phase: 5` `priority: high` |
| P5-04c | ↳ Write the runbook | How to deploy, roll back, restart workers, read logs and handle common failures. | `type: docs` `area: infra` `phase: 5` `priority: high` |
| P5-04d | ↳ Build the driver onboarding checklist | A short guide for onboarding drivers in person, including Android battery settings. | `type: docs` `area: product` `phase: 5` `priority: medium` |
| P5-05 | Track pilot metrics | Measure whether the hypotheses hold. | `type: feature` `area: ops-panel` `phase: 5` `priority: high` |
| P5-05a | ↳ Define the three metrics | Route-publish rate, match rate and completed trips, with the exact definition of each. | `type: docs` `area: product` `phase: 5` `priority: high` |
| P5-05b | ↳ Build a metrics view in Django admin | Counts by day, pulled by a query, without a separate analytics system. | `type: feature` `area: ops-panel` `phase: 5` `priority: high` |
| P5-06 | Launch the pilot | Go live on the chosen corridor. Depends on the answers from P0-09b. | `type: task` `area: product` `phase: 5` `priority: high` |
| P5-06a | ↳ Run a pre-launch checklist | Staging passes the P3-07 flow, SMS is live, and the production environment is ready. | `type: task` `area: infra` `phase: 5` `priority: high` |
| P5-06b | ↳ Onboard the first drivers | Onboard 10-20 drivers personally and approve them in the admin. | `type: task` `area: product` `phase: 5` `priority: high` |
| P5-06c | ↳ Run the first week and log issues | Support bookings manually as needed and file a bug for every problem. | `type: task` `area: product` `phase: 5` `priority: high` |

### Reserved for after the POC

These are in the design but not in the 10-11 week plan. Create them in the backlog now so the design keeps room for them, and give them the `phase: post-poc` label.

| ID | Title | Description | Labels |
| --- | --- | --- | --- |
| PX-01 | Add Sentry error tracking | Capture errors from Django, Celery and the clients. | `type: chore` `area: infra` `phase: post-poc` `priority: medium` |
| PX-02 | Move file storage to S3 | Documents and proof photos, using the storage interface from P1-02c. | `type: task` `area: infra` `phase: post-poc` `priority: medium` |
| PX-03 | Automate daily Postgres backups to S3 | Scheduled dumps with a tested restore. | `type: chore` `area: infra` `phase: post-poc` `priority: high` |
| PX-04 | Add ratings and reviews | The first feature to add after the pilot. | `type: feature` `area: backend` `phase: post-poc` `priority: medium` |
