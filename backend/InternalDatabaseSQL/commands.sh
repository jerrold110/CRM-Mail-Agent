docker build -t company-sql-database .

docker run -d -p 5432:5432 --name int_db company-sql-database
docker start int_db

#docker exec -it int_db bash
docker exec -it int_db psql -U admin -d company
docker stop int_db

#### Postgres commands ####
\q quit session
\l list all databases
\c change 
\dt list all tables in current database
\dt+
\du list all users
\?