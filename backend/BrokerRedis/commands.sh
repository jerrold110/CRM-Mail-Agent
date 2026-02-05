docker build -t redis .

docker run -d -p 6379:6379 --name redis_broker redis