# services/

Local Tyk stack, split into independent docker-compose "stacks". Which
stacks are actually running is controlled by `ENABLE_*` flags in `.env` —
`scripts/compose.sh` reads them and reconciles: disabled stacks get `down`,
enabled stacks get `up` (or whatever subcommand you pass).

Each stack lives in its own folder: a `docker-compose.*.yml` file plus
(where needed) a `confs/` folder of config/env files mounted into its
containers. The shared CA cert lives one level up, at `../ca/` (repo root),
since it's trusted by more than just these stacks.

```
services/
├── .env                  # secrets/versions/enable-flags, gitignored — copy from .env.example
├── .env.example          # template for .env
├── scripts/
│   ├── compose.sh         # entry point — reconciles stacks per .env's ENABLE_* flags
│   └── copy-volume.sh     # copy+delete a docker volume (used for one-off migrations)
├── general/
│   └── docker-compose.general.yml   # shared network (always included)
├── kong/
│   └── docker-compose.kong.yml       # Kong Gateway (enterprise) + postgres — ENABLE_KONG
├── nginx/
│   ├── certs/                        # TLS certs served by nginx (gitignored)
│   ├── confs/                        # nginx.conf, domainNotFound.html
│   └── docker-compose.nginx.yml      # reverse proxy / TLS termination — ENABLE_NGINX
├── sso/
│   ├── confs/                         # (currently unused, placeholder)
│   └── docker-compose.keycloak.yml   # keycloak + postgres — ENABLE_SSO
└── tyk-stack/
    ├── control-plane/
    │   ├── confs/                     # gateway/dashboard/mdcb env files
    │   └── docker-compose.control-plane.yml  # gateway, redis, dashboard, mdcb, mongo — ENABLE_CONTROL_PLANE
    ├── data-plane/
    │   ├── confs/                     # gateway env file
    │   └── docker-compose.data-plane.yml     # gateway, redis — ENABLE_DATA_PLANE
    └── oauth2/
        ├── confs/custom-templates/    # oauth2-proxy error pages
        └── docker-compose.oauth2.yml  # oauth2-proxy — ENABLE_OAUTH2
```

## Setup

```bash
cp services/.env.example services/.env
# fill in DASH_LICENSE / MDCB_LICENSE, adjust versions, and set ENABLE_* flags
```

## Starting stacks

Run everything from inside `services/` via `scripts/compose.sh`. It wraps
`docker compose`, so any normal compose subcommand works (`up`, `down`,
`logs`, `ps`, `restart`, `exec`, ...).

```bash
cd services

# reconcile: down whatever's disabled in .env, up -d whatever's enabled
./scripts/compose.sh

# same reconciliation, but with an explicit subcommand instead of the "up -d" default
./scripts/compose.sh logs -f

# bypass the .env flags entirely and target specific stacks directly
# (nothing gets torn down — useful for one-off checks on a normally-disabled stack)
./scripts/compose.sh -s control-plane,nginx logs -f
```

Toggle stacks by editing `ENABLE_NGINX` / `ENABLE_SSO` / `ENABLE_CONTROL_PLANE`
/ `ENABLE_DATA_PLANE` / `ENABLE_OAUTH2` / `ENABLE_KONG` in `.env`, then re-run
`./scripts/compose.sh` — it brings up what you turned on and tears down what
you turned off. The `-s` flag (stack names above, comma-separated) skips this
reconciliation and just runs your subcommand against exactly the stacks you
name, regardless of their `.env` flag.

nginx expects (via `nginx/confs/nginx.conf`) to proxy `*.docker.local` /
`sso.docker.local` hostnames to whichever of the above stacks are running —
add those hosts to `/etc/hosts` pointing at `127.0.0.1` to use them. When
`ENABLE_NGINX=true`, nginx is restarted at the end of every `compose.sh` run
so it re-resolves upstream containers that just changed.

## Known gotchas

- The data plane has no pump wired up. Add a `tyk-data-plane-pump` service to
  `tyk-stack/data-plane/docker-compose.data-plane.yml` if you need one.
- `tyk-stack/oauth2/docker-compose.oauth2.yml` has a hardcoded
  `--client-secret` and `--cookie-secret` committed in the file (not `.env`)
  — fine for local dev, but don't reuse those values anywhere real.
- Kong is Enterprise mode and needs a real `KONG_LICENSE_DATA` in `.env` to
  start — without one, `kong-gateway` will exit right after `kong-bootstrap`
  completes. `kong/docker-compose.kong.yml` also hardcodes `KONG_PASSWORD:
  handyshake` (the RBAC admin password) directly in the file, same caveat as
  oauth2's secrets above. Admin API on :8001/:8444, Admin GUI on :8002/:8445,
  proxy on :8000/:8443.
