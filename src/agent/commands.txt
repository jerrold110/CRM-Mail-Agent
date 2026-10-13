docker build -t agent_service_w_queue .

docker run -d -p 80:80 --name agent agent_service_w_queue

docker exec -it bash