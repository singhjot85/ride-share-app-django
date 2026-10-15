
NOTE: AGENTS are not meant to read this, only for reference

# Requirements Document: Heavy-Duty Route-Based Parcel Delivery Platform

Below is a structured, prioritized requirements list organized by category. I've used **MoSCoW prioritization** (Must / Should / Could / Won't) so you can phase the build.

---

## 1. Functional Requirements

### 1.1 User Management & Authentication

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-1.1 | System shall support two distinct user roles: **Driver** (truck/heavy vehicle operator) and **Sender** (parcel requester) | Must |
| FR-1.2 | Users shall register/login via phone number + OTP and/or email | Must |
| FR-1.3 | Users shall be able to switch roles if they operate as both | Should |
| FR-1.4 | System shall support KYC verification (Aadhaar/PAN/GST for India, or equivalent) | Must |
| FR-1.5 | Drivers shall submit vehicle registration, driving license, and vehicle fitness certificate | Must |
| FR-1.6 | System shall support profile management (photo, contact, company details) | Must |
| FR-1.7 | System shall support password reset and account recovery flows | Must |

---

### 1.2 Driver — Route Publishing Module

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-2.1 | Driver shall be able to create a route by selecting **origin** and **destination** on a map | Must |
| FR-2.2 | Driver shall be able to add **intermediate stop points** (waypoints) | Must |
| FR-2.3 | Driver shall specify **departure date/time** and **estimated arrival window** | Must |
| FR-2.4 | Driver shall specify **available capacity** (weight in kg/ton, volume in cft/m³, dimensions) | Must |
| FR-2.5 | Driver shall specify **vehicle type** (e.g., 7ft truck, 14ft, 19ft, trailer, container) | Must |
| FR-2.6 | Driver shall specify **accepted parcel types** (general, fragile, perishable, hazardous — with restrictions) | Should |
| FR-2.7 | Driver shall set **price per kg** or **flat rate per segment** | Must |
| FR-2.8 | Driver shall be able to edit/cancel a published route before any booking is confirmed | Must |
| FR-2.9 | Driver shall be able to view all incoming delivery requests for their routes | Must |
| FR-2.10 | Driver shall be able to **accept or reject** each request | Must |
| FR-2.11 | Driver shall be able to set recurring routes (daily/weekly) | Could |
| FR-2.12 | Driver shall be able to mark route as "Full" or "Unavailable" temporarily | Should |

---

### 1.3 Sender — Parcel Request Module

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-3.1 | Sender shall enter **pickup location** and **drop-off location** | Must |
| FR-3.2 | Sender shall enter **parcel details**: weight, dimensions, type, description | Must |
| FR-3.3 | Sender shall upload **photos of the parcel** (optional but recommended) | Should |
| FR-3.4 | Sender shall specify **pickup date/time window** and **delivery deadline** | Must |
| FR-3.5 | System shall display **matching drivers** whose routes pass through/near the sender's pickup and drop points | Must |
| FR-3.6 | System shall rank matches by: **proximity to route, price, departure time, driver rating, capacity fit** | Must |
| FR-3.7 | Sender shall view driver profile (rating, vehicle type, verification badges, past trips) | Must |
| FR-3.8 | Sender shall send a **delivery request** to selected driver(s) | Must |
| FR-3.9 | Sender shall be able to send requests to **multiple drivers** simultaneously (broadcast) | Should |
| FR-3.10 | Sender shall be able to track request status: Pending → Accepted → Rejected → Expired | Must |
| FR-3.11 | Sender shall be able to cancel a request before pickup | Must |
| FR-3.12 | Sender shall be able to schedule **recurring shipments** | Could |

---

### 1.4 Matching & Discovery Engine

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-4.1 | System shall match parcels to routes where the **pickup and drop points fall within a configurable detour radius** (e.g., 5–15 km) of the driver's route | Must |
| FR-4.2 | System shall filter matches by **available capacity** (weight + volume) | Must |
| FR-4.3 | System shall filter matches by **timing compatibility** (pickup window vs. driver's ETA at that point) | Must |
| FR-4.4 | System shall filter by **parcel type compatibility** with vehicle | Must |
| FR-4.5 | System shall compute a **match score** combining distance, price, time, and rating | Must |
| FR-4.6 | System shall display matches on a **map view** with route overlay | Must |
| FR-4.7 | System shall support **corridor search** (sender defines a route corridor, not just points) | Could |
| FR-4.8 | System shall notify drivers of high-match requests via push notification | Should |

---

### 1.5 Booking & Order Lifecycle

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-5.1 | Booking shall be created only after driver accepts the request | Must |
| FR-5.2 | System shall generate a unique **Booking ID / Tracking Number** | Must |
| FR-5.3 | Order status pipeline: **Requested → Accepted → Pickup Scheduled → Picked Up → In Transit → Out for Delivery → Delivered → Completed** | Must |
| FR-5.4 | Each status change shall trigger a notification to both parties | Must |
| FR-5.5 | System shall support **cancellation** with reason at defined stages | Must |
| FR-5.6 | System shall support **rescheduling** of pickup/delivery | Should |
| FR-5.7 | System shall log all status changes with timestamp and actor | Must |

---

### 1.6 Tracking & Communication

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-6.1 | Sender shall see **real-time driver location** on a map during transit | Must |
| FR-6.2 | System shall show **ETA** based on current location and route | Must |
| FR-6.3 | System shall send **geofence-based notifications** (e.g., "Driver is 30 min away") | Should |
| FR-6.4 | In-app chat between driver and sender | Must |
| FR-6.5 | **Masked calling** (phone numbers hidden until booking confirmed) | Should |
| FR-6.6 | Push notifications for all key events | Must |
| FR-6.7 | SMS/WhatsApp fallback for users without smartphones | Should |
| FR-6.8 | Proof of Pickup (OTP or photo) | Must |
| FR-6.9 | Proof of Delivery (OTP + photo + signature) | Must |
| FR-6.10 | Trip history for both users | Must |

---

### 1.7 Payments & Financials

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-7.1 | System shall display **price breakdown** before booking (base fare + per-kg + detour charge) | Must |
| FR-7.2 | Support **online payment** (UPI, card, net banking, wallet) | Must |
| FR-7.3 | Support **cash on delivery** as fallback | Should |
| FR-7.4 | **Escrow mechanism**: funds held until delivery confirmed | Should |
| FR-7.5 | Automatic payout to driver after delivery confirmation | Should |
| FR-7.6 | Commission/platform fee deduction | Must |
| FR-7.7 | Invoice/receipt generation (PDF) | Must |
| FR-7.8 | Refund handling for cancellations and disputes | Must |
| FR-7.9 | Driver wallet and earnings dashboard | Must |
| FR-7.10 | GST/tax compliance and reporting | Must (India) |

---

### 1.8 Ratings, Reviews & Trust

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-8.1 | Sender shall rate driver after delivery (1–5 stars + text) | Must |
| FR-8.2 | Driver shall rate sender after delivery | Should |
| FR-8.3 | Ratings displayed on profiles | Must |
| FR-8.4 | System shall flag users with consistently low ratings | Should |
| FR-8.5 | **Dispute resolution** workflow with evidence upload | Must |
| FR-8.6 | Damage/loss claim filing and tracking | Must |
| FR-8.7 | Insurance integration or optional cargo insurance add-on | Could |

---

### 1.9 Admin & Operations Panel

| ID | Requirement | Priority |
|:---|:---|:---|
| FR-9.1 | Admin shall view/manage all users (drivers + senders) | Must |
| FR-9.2 | Admin shall approve/reject KYC and vehicle documents | Must |
| FR-9.3 | Admin shall view/manage all bookings and routes | Must |
| FR-9.4 | Admin shall resolve disputes and process refunds | Must |
| FR-9.5 | Admin shall configure pricing rules, commission %, and detour radius | Must |
| FR-9.6 | Admin dashboard with analytics (trips, revenue, active users, match rate) | Must |
| FR-9.7 | Admin shall suspend/ban users | Must |
| FR-9.8 | Audit logs for all admin actions | Should |
| FR-9.9 | Fraud detection alerts (double brokering, fake documents) | Should |

---

## 2. Non-Functional Requirements

### 2.1 Performance & Scalability

| ID | Requirement | Target |
|:---|:---|:---|
| NFR-1.1 | Matching algorithm response time | < 2 seconds |
| NFR-1.2 | Map/route rendering | < 3 seconds |
| NFR-1.3 | API response time (p95) | < 500 ms |
| NFR-1.4 | Concurrent users supported (initial) | 10,000 |
| NFR-1.5 | Uptime | 99.5% |
| NFR-1.6 | Horizontal scalability for matching service | Must |

### 2.2 Security

| ID | Requirement |
|:---|:---|
| NFR-2.1 | All data in transit encrypted via TLS 1.2+ |
| NFR-2.2 | PII and payment data encrypted at rest (AES-256) |
| NFR-2.3 | Role-based access control (RBAC) on all APIs |
| NFR-2.4 | Rate limiting and DDoS protection |
| NFR-2.5 | Secure OTP and session management |
| NFR-2.6 | Compliance with India's DPDP Act / GDPR (if applicable) |
| NFR-2.7 | Regular security audits and penetration testing |
| NFR-2.8 | Document verification via third-party KYC APIs |

### 2.3 Reliability & Availability

| ID | Requirement |
|:---|:---|
| NFR-3.1 | Graceful degradation if GPS/maps API fails |
| NFR-3.2 | Offline queue for status updates (driver app) |
| NFR-3.3 | Automated backups (daily) with point-in-time recovery |
| NFR-3.4 | Disaster recovery plan with RTO < 4 hours, RPO < 1 hour |

### 2.4 Usability

| ID | Requirement |
|:---|:---|
| NFR-4.1 | Driver app must be usable by users with low digital literacy |
| NFR-4.2 | Support Hindi + English + regional languages |
| NFR-4.3 | Minimal steps to publish a route (< 5 taps for repeat routes) |
| NFR-4.4 | Large touch targets and voice input for drivers |
| NFR-4.5 | Accessibility compliance (WCAG 2.1 AA) |

### 2.5 Compatibility

| ID | Requirement |
|:---|:---|
| NFR-5.1 | Mobile apps: Android 8+ and iOS 14+ |
| NFR-5.2 | Web app: Chrome, Firefox, Safari, Edge (latest 2 versions) |
| NFR-5.3 | Responsive design for tablets |

---

## 3. Technical Requirements

### 3.1 Platform & Stack

| Layer | Recommended Options |
|:---|:---|
| Mobile (Driver) | React Native / Flutter / Kotlin |
| Mobile (Sender) | React Native / Flutter / Kotlin |
| Web (Admin + Sender) | React Native / Vue |
| Backend API | Django |
| Database | PostgreSQL + PostGIS (geospatial) |
| Cache | Redis |
| Queue | Celery / Kafka or SNS |
| Maps | OpenStreetMap + Leaflet / Mapbox |
| Truck Routing | GPS / moblie locaion / HERE Truck Routing / PTV / custom OSRM with truck profile |
| Push Notifications | Telegram / OpenSource Alternative / Firebase Cloud Messaging |
| SMS/OTP | OpenSource Alternative / Twilio / MSG91 / AWS SNS |
| Payments | Razorpay / Stripe / PayU |
| KYC | DigiLocker / Signzy / Karza |
| Cloud | AWS |
| Containerization | Docker + Kubernetes |

### 3.2 Integrations

| ID | Integration | Purpose |
|:---|:---|:---|
| TR-1 | FMCSA SAFER / VAHAN | Carrier/vehicle verification |
| TR-2 | ELD/GPS providers | Real-time truck tracking |
| TR-3 | Payment gateway | Online payments + escrow |
| TR-4 | SMS/WhatsApp API | OTP + notifications |
| TR-5 | KYC API | Aadhaar/PAN/GST verification |
| TR-6 | e-Way Bill (India) | GST compliance for goods movement |
| TR-7 | Insurance API | Cargo insurance add-on |
| TR-8 | Maps + Truck Routing API | Route calculation with truck constraints |
| TR-9 | Analytics (Mixpanel/GA) | User behavior tracking |

---

## 4. Data Requirements

| ID | Requirement |
|:---|:---|
| DR-1 | Store user profiles, KYC documents, vehicle details |
| DR-2 | Store routes with polyline geometry (PostGIS) |
| DR-3 | Store bookings, status history, and audit trails |
| DR-4 | Store payments, invoices, and payout records |
| DR-5 | Store ratings, reviews, and dispute records |
| DR-6 | Store GPS tracking breadcrumbs (with retention policy) |
| DR-7 | Data retention policy compliant with local regulations |
| DR-8 | Right to deletion / data export for users |

---

## 5. Legal & Compliance Requirements

| ID | Requirement |
|:---|:---|
| LR-1 | Terms of Service and Privacy Policy |
| LR-2 | Carrier onboarding compliance (motor carrier number, insurance) |
| LR-3 | Cargo liability and insurance terms |
| LR-4 | GST compliance and e-Way Bill generation |
| LR-5 | DPDP Act (India) / GDPR compliance |
| LR-6 | Prohibited items policy (hazmat, illegal goods) |
| LR-7 | Dispute resolution and arbitration terms |
| LR-8 | Platform liability limitations |

---

## 7. Key Risks & Mitigation

| Risk | Mitigation |
|:---|:---|
| **Trust deficit** between strangers | KYC, ratings, insurance, escrow |
| **Fraud / double brokering** | FMCSA/VAHAN verification, audit logs |
| **Low driver adoption** | Incentives, zero commission initially, simple UX |
| **Route matching accuracy** | PostGIS + truck routing API + detour radius tuning |
| **Regulatory changes** | Legal counsel, modular compliance layer |
| **Payment disputes** | Escrow, clear terms, dispute workflow |
| **Cargo damage claims** | Insurance integration, photo proof, claims workflow |

---

## 8. Success Metrics (KPIs)

| Metric | Target (Year 1) |
|:---|:---|
| Registered drivers | 5,000 |
| Registered senders | 20,000 |
| Monthly active routes | 10,000 |
| Match rate (requests → bookings) | > 40% |
| Average detour per match | < 10 km |
| On-time delivery rate | > 90% |
| Average rating | > 4.2 |
| GMV (Gross Merchandise Value) | ₹5 Cr/month |
| Driver retention (30-day) | > 50% |

---

This requirements document gives you a complete blueprint. You can now take this and:
1. **Prioritize** based on your budget and timeline.
2. **Convert** each requirement into user stories for sprint planning.
3. **Estimate** effort per module for cost calculation.
4. **Validate** with real truck drivers and shippers before building.

Would you like me to convert this into a **sprint-wise backlog**, a **cost estimate**, or a **technical architecture diagram** next?
