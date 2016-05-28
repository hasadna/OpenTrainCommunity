% sudo -u postgres psql
CREATE USER guest  WITH ENCRYPTED PASSWORD 'guest';
GRANT CONNECT ON DATABASE production to guest;
\c train2
GRANT USAGE ON SCHEMA public to guest;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO guest;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO guest;
