# Database

SecureLens defaults to a local SQLite file (`securelens.db`, created
automatically). Swap `DATABASE_URL` in `.env` to point at Postgres/MySQL
instead — `schema.sql` in this folder documents the table SQLAlchemy
creates, for reference or manual provisioning.
