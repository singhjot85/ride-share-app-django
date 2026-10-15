FROM postgres:14

COPY ./create_multiple_database.sh /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/create_multiple_database.sh
