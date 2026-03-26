# Fleet — SvelteKit Frontend

A SvelteKit frontend for the Fleet mobility management REST API.

## Project Structure

```
src/
├── app.css                  # Global design tokens & base styles
├── app.html                 # HTML shell
├── lib/
│   ├── api/
│   │   ├── client.ts        # Base fetch wrapper (auth headers, error handling)
│   │   ├── auth.ts          # Login / signup / me endpoints
│   │   ├── entities.ts      # Drivers, Cars, DisabledUsers, Requests, Reviews
│   │   └── index.ts
│   ├── stores/
│   │   ├── auth.ts          # Token + user store (persisted in localStorage)
│   │   ├── notifications.ts # Toast notification store
│   │   └── index.ts
│   └── components/
│       └── Toast.svelte     # Toast notification UI
└── routes/
    ├── +layout.svelte       # Root layout (mounts Toast)
    ├── +page.svelte         # Redirects → /dashboard or /login
    ├── login/
    │   └── +page.svelte     # Login page
    ├── signup/
    │   └── +page.svelte     # Signup page
    └── (app)/
        └── dashboard/
            └── +page.svelte # Dashboard stub (auth-guarded)
```

## Setup

```bash
npm install
```

## Configuration

Copy `.env.example` to `.env` and set your backend URL:

```env
PUBLIC_API_BASE_URL=http://localhost:8000
```

## Dev server

```bash
npm run dev
```

## Auth flow

- `POST /auth/login` → receives `{ access_token, token_type }`, stores token in `localStorage`
- `POST /auth/signup` → same response, auto-logs in
- All subsequent API calls include `Authorization: Bearer <token>` automatically

## API modules

Every resource follows the same pattern:

```ts
import { driversApi } from '$lib/api/entities';

const drivers = await driversApi.list();
const driver  = await driversApi.get(1);
const created = await driversApi.create({ name: 'Alice' });
const updated = await driversApi.update(1, { phone: '...' });
await driversApi.delete(1);
```

Same interface for: `carsApi`, `disabledApi`, `driveRequestsApi`, `shopRequestsApi`, `reviewsApi`.
