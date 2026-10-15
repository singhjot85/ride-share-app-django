# Route-Based Parcel Delivery Platform: Plan Review, POC Scope & Tech Stack

## 1. Review of the plan

The requirements document is a v1 product spec, not a POC: about 100 requirements across nine modules, plus a ₹5 Cr/month GMV target. A POC should test the riskiest assumptions, and those are not technical:

1. Will truck drivers publish routes and accept part-loads?
2. Will senders trust a stranger's truck with cargo?
3. Does matching produce a usable pickup and drop, given that trucks cannot detour into city lanes?

| Issue | Why it matters | Fix |
| --- | --- | --- |
| Detour radius of 5-15 km (FR-4.1) | A 14ft+ truck cannot realistically detour 10 km for one parcel. Real part-load trucking runs yard-to-yard or hub-to-hub. | Use pickup/drop points on or near the route (transport yards or fixed stops), radius 3-5 km. Decide who handles first/last mile. |
| Direction not specified | A parcel whose drop is behind the pickup along the route is not a match. Naive implementations miss this. | Matching must check that pickup comes before drop along the route (Phase 2). |
| FMCSA SAFER and VAHAN mixed | FMCSA is US-only; this looks like copied boilerplate. | Pick India. Drop FMCSA. |
| Tech table errors | "Web: React Native / Vue" (RN is not a web framework), "Push: Telegram" (not push), "Truck Routing: GPS / mobile location" (not a routing engine). | Commit to one choice per layer (section 4). |
| Escrow (FR-7.4) | Holding customer funds is regulated in India (RBI payment aggregator rules). | Post-POC, use a gateway with split/hold features (e.g. Razorpay Route). Verify current rules with a lawyer. |
| Legal gaps | Nothing on goods-carriage permits (can a driver legally carry third-party goods for hire?), consignment note/LR, or the e-Way Bill value threshold. | Add to the compliance list. Do not build for it in the POC, but get answers before the pilot. |
| Missing requirements | Weight verification at pickup (a major dispute source), loading/unloading responsibility, cancellation penalties, no-show policy. | Add a lightweight version in Phase 3. |
| Hazardous parcels (FR-2.6) | A liability magnet. | Prohibit entirely at the start. |
| Premature NFRs | 10,000 concurrent users, 99.5% uptime, WCAG AA, RTO/RPO targets. | Defer all of them. |

Cold-start risk: a two-sided marketplace is worthless without supply. Plan the pilot on one corridor with 10-20 drivers you onboard personally, and run it concierge-style (manual help alongside the app). The software only needs to make that pilot work.

Minor: section numbering skips 6.

## 2. Minimum POC scope in phases

The POC is about 10-11 weeks in six phases. Assumptions: 3-4 developers, a single-corridor pilot, an Android driver app, a web client for senders, Django admin as the ops panel, and no ML/DL. Phases 3 and 4 can overlap if you have a dedicated Android developer.

| Phase | Duration | Goal and scope | Exit criteria |
| --- | --- | --- | --- |
| 0. Decisions and foundation | \~1 week | Fix the pilot corridor, pickup/drop model (yards or on-route points) and pricing (flat ₹/kg by segment). Define the domain model and state machine (User, Vehicle, Route, ParcelRequest, Booking, StatusEvent). Set up repo, docker-compose (Django, Postgres+PostGIS, Redis), CI, staging box. Start SMS DLT registration now. | Schema agreed; `docker-compose up` works for everyone; map tile and routing providers chosen. |
| 1. Accounts and ops back-office | \~2 weeks | Phone + OTP login with Driver and Sender roles. Driver profile with vehicle and document photo uploads. Manual KYC: admin approves in Django admin (no third-party KYC API). Django admin for users, routes, bookings. | A driver can sign up, upload documents and be approved by an admin. |
| 2. Routes and matching (the heart of the POC) | \~2 weeks | Driver creates a route (origin, destination, optional waypoints), departure time, capacity (kg only), price; stored as a PostGIS LineString from the routing engine. Sender creates a parcel request. Rule-based matching: `ST_DWithin` of pickup and drop to the route; `ST_LineLocatePoint(pickup) < ST_LineLocatePoint(drop)` for direction; capacity and time-window filters; simple weighted score of distance, price and departure time. Sender sees matches on a map; driver sees requests with Accept/Reject. | On seeded corridor data a request returns the right drivers in under 2 s; hand-checked cases pass, including a wrong-direction case that must not match. |
| 3. Booking lifecycle and notifications | \~2 weeks | Trimmed pipeline: Requested, Accepted, Picked Up, In Transit, Delivered, Completed, plus Cancelled and Rejected/Expired. OTP proof of pickup and delivery plus one photo each. Request auto-expiry via Celery beat. FCM push to drivers; SMS or in-app updates to senders. Phone numbers revealed after acceptance with a call/WhatsApp deep link (no in-app chat or masked calling). Cancellation with reason; append-only status log with actor and timestamp. | A full booking runs end to end on staging with real devices. |
| 4. Live tracking | \~2 weeks | Android foreground location service sends batched pings every 15-30 s with an offline queue. Latest position in Redis, breadcrumbs in Postgres. Sender web page polls every 10-15 s and shows the truck on a map with a basic ETA from the routing engine. | A real truck trip shows location updates with acceptable gaps; battery impact measured. |
| 5. Simple money and pilot hardening | \~1-2 weeks | Price breakdown before booking (base x weight, platform fee). Payment recorded offline/UPI outside the app, or Razorpay test mode to prove the integration; no escrow or payouts. Simple PDF receipt. Sentry, basic logs, seed-data script, short runbook. | Pilot launches with 10-20 real drivers; route-publish rate, match rate and completed trips are tracked. |

## 3. Explicitly out of the POC

None of these validates the core hypotheses, so they wait until after the pilot. Ratings and reviews are the first thing to add right after it.

- Ratings and reviews, disputes and claims workflow, insurance
- Escrow and payouts, third-party KYC, e-Way Bill
- Recurring routes and shipments, broadcast requests
- In-app chat, masked calling, geofence alerts
- Languages beyond Hindi and English, iOS
- Fraud detection, analytics dashboards
- Kubernetes and Kafka
- All ML/DL (matching is rule-based)

## 4. Tech stack review

Your team's skills fit this project: Django, PostGIS, Redis, Celery and native Kotlin for the driver app is a solid, boring stack, and boring is correct here. Pick one option per layer.

| Layer | POC choice | Pros | Cons | Post-POC |
| --- | --- | --- | --- | --- |
| Backend | Django + DRF + GeoDjango | Team knows it; free admin panel; native PostGIS integration | Sync-first; WebSockets need Channels | Stay with a modular monolith; split tracking or matching only if measurements justify it |
| Database | Postgres + PostGIS | Right tool for line/point queries; one DB to operate | Breadcrumb volume grows fast | Managed Postgres (RDS); partition breadcrumbs by time or add TimescaleDB |
| Cache and queue | Redis (cache, Celery broker, latest-location store) | Already known; one service, three jobs | Not durable as a primary store | Keep; separate broker and cache instances at scale |
| Async jobs | Celery + Celery beat | Known; handles expiry, notifications, receipts | Operational quirks (retries, visibility) | Keep |
| Driver app | Native Android (Kotlin) | Best control of background location and foreground services, the make-or-break feature; team knows Kotlin; Android dominates this user base | No iOS; two codebases if iOS is added | If iOS is needed, evaluate Kotlin Multiplatform or Flutter then |
| Sender client | Responsive web / PWA | No app store; fast iteration; shareable link | Limited push on iOS web; weaker UX than native | Native sender app if retention data justifies it |
| Web framework | One of Vue or React | Team knows both | Using both doubles maintenance | If a toss-up, I lean React (larger map-library and hiring ecosystem); otherwise whichever the majority is faster in |
| Ops panel | Django admin | Zero build cost | Plain; limited workflows | Custom admin UI once workflows stabilize |
| Maps | Leaflet or MapLibre + a tile provider | Free; no lock-in | The public OSM tile server prohibits heavy or commercial use | Use a provider's free tier (MapTiler, Stadia, etc.) now; self-host tiles or pay later |
| Routing | OpenRouteService (HGV profile) or self-hosted OSRM | ORS has truck profiles and a free tier (check current limits); self-hosted OSRM is free and fast | The public OSRM demo server is not for production; OSRM needs memory for an India extract and has only a basic truck profile | Self-hosted Valhalla (truck costing) or OSRM, or a paid provider like HERE if you need accurate truck restrictions |
| Push | FCM | Free; standard on Android | Google dependency | Keep |
| SMS/OTP | MSG91 or a similar Indian provider | DLT-compliant; cheap | DLT registration takes time; cost scales with volume | Keep; add WhatsApp Business templates later |
| Payments | Razorpay test mode, or offline recording | Good docs; a marketplace/split product exists | Compliance around holding funds | Razorpay Route or equivalent for split settlements |
| KYC | Manual admin review | Zero cost; you learn what fails | Does not scale | Signzy, Karza or Digio; DigiLocker needs onboarding approval |
| Infra | One VM (EC2 ap-south-1) + docker-compose | Cheap, simple, debuggable | Single point of failure | Managed K8s or ECS when you have a real uptime need |

## 5. Where the document's stack should be pushed back on

- **Telegram as push:** not appropriate for truckers or senders. Use FCM plus SMS.
- **Kafka/SNS:** overkill. Celery plus Redis covers the POC and likely the first year.
- **Kubernetes now:** the team knows it, but it is operational overhead that validates no hypothesis. Docker-compose on one VM is enough; revisit for autoscaling or zero-downtime deploys.
- **WebSockets now:** start with polling. A 10-15 s refresh is invisible for a truck at highway speed; add Django Channels or SSE later.
- **Three alternatives per row:** a stack table full of "A / B / C" means the decision has not been made. Pick one.

## 6. Opinion and first spikes

The biggest technical risks are background location reliability on cheap Android phones and routing accuracy with truck restrictions, not the choice of web framework. Run two spikes before Phase 2:

1. A foreground service keeps sending pings for 6+ hours on a budget phone.
2. Your routing provider returns sane geometry for the pilot corridor.

If either fails, the plan changes.

## 7. Final POC tech stack (decided)

The stack below is final for the POC. Items marked post-POC have scope reserved in the design but are not built in the 10-11 week plan.

| Layer | Choice | When |
| --- | --- | --- |
| Backend | Django + DRF + GeoDjango, drf-spectacular for the OpenAPI schema | POC |
| Async jobs | Celery + Celery beat (Redis broker) | POC |
| Cache and latest driver location | Redis | POC |
| Database | Postgres + PostGIS | POC |
| Driver app | Native Android: Kotlin, Jetpack Compose, Room offline queue, foreground location service, WorkManager | POC |
| Sender web (and later admin UI) | React + TypeScript (Vite), Hindi and English | POC |
| Ops panel | Django admin | POC |
| Maps | Leaflet or MapLibre + a tile provider (not the public OSM tile server) | POC |
| Routing engine | OpenRouteService (HGV profile) to start; self-hosted OSRM or Valhalla later | POC |
| Push | FCM | POC |
| SMS/OTP | MSG91 (start DLT registration early) | POC |
| Payments | Razorpay test mode | POC |
| Deployment | Docker Compose on a single EC2 VM (ap-south-1) | POC |
| Error tracking | Sentry | Post-POC |
| File storage | S3 for documents and proof photos | Post-POC |
| Backups | Automated daily Postgres backups to S3 | Post-POC |

Out of scope for now: Kubernetes, Kafka, WebSockets (polling first), third-party KYC, escrow and payouts, ratings, iOS, and all ML/DL.
