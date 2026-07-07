# Supabase Server SDK Setup

This setup is for request handlers that use `withSupabase` from `@supabase/server`.

## Install

Run locally or in Cloud Shell:

```bash
npm install @supabase/server
```

Commit the resulting `package.json` and `package-lock.json` changes after review.

## Environment variables

Copy real values from the Supabase dashboard Connect dialog.

Do not commit secret values.

```txt
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
SUPABASE_JWKS_URL=
```

## Handler example

See:

```txt
examples/supabase-server-handler.mjs
```

The example uses:

```js
import { withSupabase } from "@supabase/server"
```

and creates a user-authenticated handler with `ctx.supabase` for RLS-scoped access.

## Auth modes

Supported modes from the integration note:

```txt
user
publishable
secret
none
```

For non-user modes on Supabase Edge Functions, set `verify_jwt = false` for that function in `supabase/config.toml`.

## Governance boundary

- `ctx.supabase` is RLS-scoped.
- `ctx.supabaseAdmin` bypasses RLS and must be used only in explicitly trusted server contexts.
- Do not expose admin or secret-key behavior to browser/client code.
- This setup does not establish truth adjudication.

Standing semantics:

```txt
authority=false
truthClaim=false
```
