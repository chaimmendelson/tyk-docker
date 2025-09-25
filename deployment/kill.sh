# 1. Remove all containers attached to the shared Tyk network
docker network inspect tyk-network -f '{{range $id, $c := .Containers}}{{$id}} {{end}}' \
    | xargs -r docker rm -f

# 2. Tear down Tyk Control Plane
(
    cd control-plane || exit
    docker-compose down
)

# 3. Tear down Keycloak Compose
(
    cd keycloak || exit
    docker-compose down
)

# 4. Tear down OAuth2 Proxy Compose
(
    cd oauth2-proxy || exit
    docker-compose down
)

# 5. Tear down Nginx Proxy Compose
(
    cd ngnix-proxy || exit
    docker-compose down
)

# 6. Tear down atlas
(
    cd atlas || exit
    docker-compose down
)