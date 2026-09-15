# services/

Local Tyk stack, split into independent docker-compose "stacks" that can be
started individually or combined.

```
services/
├── .env                 # secrets/versions, gitignored — copy from .env.example
├── .env.example          # template for .env
├── certs/                # TLS certs (gitignored)
├── confs/                # per-service config/env files, mounted into containers
│   ├── nginx/
│   ├── oauth2-proxy/
│   └── tyk/
│       ├── control-plane/
│       └── data-plane/
├── docker/                # one compose file per stack
│   ├── docker-compose.general.yml            # shared network (always included)
│   ├── docker-compose.tyk.control-plane.yml  # gateway, redis, dashboard, mdcb, pump, mongo
│   ├── docker-compose.tyk.data-plane.yml     # gateway, redis
│   ├── docker-compose.nginx.yml              # reverse proxy / TLS termination
│   ├── docker-compose.oauth2.yml             # oauth2-proxy
│   └── docker-compose.keycloak.yml           # keycloak + postgres
└── scripts/
    ├── compose.sh         # entry point — start/stop only the stacks you want
    └── copy-volume.sh     # copy+delete a docker volume (used for one-off migrations)
```

## Setup

```bash
cp services/.env.example services/.env
# fill in DASH_LICENSE / MDCB_LICENSE and adjust versions
```

## Starting stacks

Run everything from inside `services/` via `scripts/compose.sh`. It wraps
`docker compose`, so any normal compose subcommand works (`up`, `down`,
`logs`, `ps`, `restart`, `exec`, ...) — just prefix it with which stack(s) you
want via `-s`.

```bash
cd services

# only the control plane
./scripts/compose.sh -s control-plane up -d

# control plane + nginx in front of it
./scripts/compose.sh -s control-plane,nginx up -d

# just the data plane
./scripts/compose.sh -s data-plane up -d

# everything (same as before, still the default with no -s)
./scripts/compose.sh up -d

# tear down one stack without touching the others
./scripts/compose.sh -s keycloak down

# follow logs for a subset
./scripts/compose.sh -s control-plane logs -f
```

Available stack names: `control-plane`, `data-plane`, `nginx`, `oauth2`,
`keycloak`, or `all`.

nginx expects (via `confs/nginx/nginx.conf`) to proxy `*.docker.local` /
`sso.docker.local` hostnames to whichever of the above stacks are running —
add those hosts to `/etc/hosts` pointing at `127.0.0.1` to use them. After any
`compose.sh` run, nginx is restarted (if present) so it re-resolves upstream
containers that just changed.

## Known gotchas

- `confs/tyk/data-plane/pump.env` exists but no compose service currently
  uses it — the data plane has no pump wired up. Add a `tyk-data-plane-pump`
  service to `docker-compose.tyk.data-plane.yml` if you need one.
- `docker-compose.oauth2.yml` has a hardcoded `--client-secret` and
  `--cookie-secret` committed in the file (not `.env`) — fine for local dev,
  but don't reuse those values anywhere real.
