FROM postgres:15

COPY postgresql.conf /etc/postgresql/postgresql.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
