# 1. Bring up Tyk Control Plane
(
    cd control-plane || exit
    docker-compose up -d
)

# 2. Bring up Keycloak Compose
(
    cd keycloak || exit
    docker-compose up -d
)

# 3. Bring up OAuth2 Proxy Compose
(
    cd oauth2-proxy || exit
    docker-compose up -d
)

# 4. Bring up Nginx Compose
(
    cd nginx || exit
    docker-compose up -d
)

# 5. Bring up atlas
(
    cd atlas || exit
    docker-compose up -d
)