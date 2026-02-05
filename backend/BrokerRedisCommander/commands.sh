# Redis commander is a client not a host, the redis instance is the host
docker build -t redis-commander .

docker run -d -p 8081:8081 --name redis_commander --link redis_broker:redis_broker --env REDIS_HOSTS=local:redis_broker:6379 redis-commander