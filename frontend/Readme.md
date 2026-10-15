# LoadShare Frontend

React + TypeScript web app for senders (and later, an admin UI). Built with Vite, available in Hindi and English.

> The driver app is a separate native Android (Kotlin) project in `android/`. The ops panel for the POC is Django admin.

## Tech Stack

- **Framework:** React + TypeScript
- **Build tool:** Vite
- **Maps:** Leaflet or MapLibre + a tile provider (not the public OSM tile server)
- **i18n:** Hindi and English
- **HTTP:** Axios, wrapped in service modules

## Folder Structure

```
src/
|- assets/          # Static assets and global styles
|- components/
|   |- common/      # Generic, app-agnostic components (Button, Card, Modal ...)
|   |- layout/      # Components that compose generic ones (HeroSection, ParcelSummary ...)
|   |- view/        # View-specific components, only when layout components are not enough
|- config/          # Config types and defaults
|- layouts/         # Page shells that can render multiple views
|- routes/          # Route definitions (public and private)
|- services/        # API layer (axios instance + one module per feature)
|- stores/          # Global state
|- views/           # Page-level, routed components
|- locales/         # Hindi and English translations
|- App.tsx
|- main.tsx
```

> Folder names are indicative and may change as the POC evolves.

## Getting Started

```bash
cd frontend
npm install
cp .env.example .env     # set the backend API URL
npm run dev
```

Other scripts:

```bash
npm run build      # production build
npm run preview    # preview the production build
npm run lint
npm run test
```

## Core Conventions

**Components: three tiers**
- *Generic:* dumb, app-agnostic, unaware of positioning (Button, Card, Modal).
- *Layout:* combine generic components into a ready-to-use block.
- *View:* only when really needed (for example, forms). Place them in a folder named after the view.
- Components never contain business logic. They emit events and the view handles them.
- Make components configurable with sensible defaults rather than building one-offs.

**Views and routing**
- Views hold the page structure and the business logic.
- Lazy-load route components; use nested routes where a view acts as a layout shell.
- Keep public (unauthenticated) and private (authenticated) routes in separate files.

**Services and state**
- All external communication goes through service modules; never call `fetch` or `axios` directly from components or stores.
- Configure the base URL, interceptors and error handling once, in the shared API instance.
- Stores orchestrate data (call services, cache, expose state). Avoid keeping large or sensitive data in them.

**Styling and assets**
- Prefer the component library's built-in props and utilities; write custom CSS only as a last resort, and scope it to the component.
- Declare design tokens (CSS variables) in one place.
- Prefer icons over images. If an image is needed, load it from a static store by URL instead of committing it.

**Configuration**
- Text, content and behaviour switches come from config, with defaults so the UI is never empty. Most config is expected to come from the backend.

## Documentation

Detailed frontend documentation lives in the project's `docs/` directory.
