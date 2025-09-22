cd tyk-pro-docker-demo && docker-compose -f ./docker-compose.yml -f ./docker-compose.mongo.yml up -d && cd ..
cd keycloack && docker-compose up -d && cd .. && cd oauth2-proxy && docker-compose up -d && cd ..
