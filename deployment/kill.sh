# 1. Remove all containers attached to the shared Tyk network
docker network inspect tyk-pro-docker-demo_tyk -f '{{range $id, $c := .Containers}}{{$id}} {{end}}' \
    | xargs -r docker rm -f

# 2. Tear down Tyk Compose (including Mongo) 
(
    cd tyk-pro-docker-demo || exit
    docker-compose -f docker-compose.yml -f docker-compose.mongo.yml down
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
