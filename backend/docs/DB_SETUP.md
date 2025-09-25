# KRAI v0.6 Database Setup

The web backend now works with a dedicated PostgreSQL schema (`krai_mrp_v06`) that stores
normalized footwear models, SUPER-BOM, materials and warehouse data.

## 1. Create database & user (once)

```sql
CREATE DATABASE krai_mrp_v06;
CREATE USER krai_user WITH PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE krai_mrp_v06 TO krai_user;
```

Update `.env` (or environment variables) with the connection string, e.g.

```
DATABASE_URL=postgresql://krai_user:change-me@localhost:5432/krai_mrp_v06
```

## 2. Create tables

From the project root run:

```bash
python -m backend.app.db.init_db
```

This will create all SQLAlchemy-managed tables (models, materials, references, warehouse, etc.).
The command is idempotent — you can rerun it safely.

## 3. Seed reference data (optional)

Insert baseline materials, cutting parts and reference items through the API (`/references`,
`/materials`) or via SQL scripts. Without data the frontend will render empty tables but stay
functional.

## 4. Verify

Start the FastAPI server (or the full application) and hit:

```
GET http://localhost:8001/api/v1/models
```

You should receive an empty paginated result, meaning the schema is ready for use.

