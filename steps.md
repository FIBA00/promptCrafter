# Steps i followed when creating backend for future reference

1. i created the uv init .
2. installed necessary packages like fastapi, sqlalchemy, pydantic, alembic etc.
3. created database connection using psql in local machine :

    ```bash
    <!-- command to create new database -->
        CREATE DATABASE promptcrafter;
    <!-- command check the database created -->
        \l

    ```

4. then created my request and response schemas using pydantic in schema/schemas.py use BaseModels, never forget to create separate classes for request and response. and if you set the response to be exact schema dont forget on return of the end point to return the exact schema object.

5. then created my database models in models/models.py using sqlalchemy ORM never forget to import the Base from db/database.py and inherit it in your models. also set the __tablename__ attribute for each model. create one relationships if needed. ex: user to history one to many relationship.

6. then created the database connection in db/database.py using sqlalchemy create_engine and sessionmaker. never forget to set the DATABASE_URL from environment variable.

7. dont forget to use create all method to create the tables in the database.

    ```python
    Base.metadata.create_all(bind=engine)
    ```

NOTE: later use alembic for migrations.

## Steps i followed to setup alembic for database migrations

1. then initialize alembic for database migration using `alembic init alembic`. this will create a folder named alembic and a file named alembic.ini.

2. then configure the alembic.ini file to point to your database url. and configure the env.py file in alembic folder to point to your models Base. so that alembic can detect the changes in your models.

    ```bash
    <!-- sepcific lines to be edited in the init file -->
    # in alembic.ini file
    sqlalchemy.url = <your_database_url> may come from azure or aws rds or local psql
    # in alembic/env.py file
    from backend.db.database import Base  # import your Base
    target_metadata = Base.metadata  # set the target metadata

    ```

3. then create the initial migration using `alembic revision --autogenerate -m "Initial migration"`. this will create a migration file in alembic/versions folder.

4. then apply the migration to the database using `alembic upgrade head`. this will create the tables in your database. from now on you will use alembic to manage your database schema.

### steps to check postgres issue and edit databases

```bash  sudo -u postgres psql -d template1 -c "\l"``` : to list all databases

```bash sudo -u postgres psql -d template1 -c "ALTER USER postgres PASSWORD 'newpassword';"``` : to change password of postgres user

```bash sudo -u postgres psql -d template1 -c "\du"``` : to list all users

```bash sudo -u postgres psql -d template1 -c "DROP DATABASE dbname;"``` : to drop a database

```bash sudo -u postgres psql -d template1 -c "CREATE DATABASE dbname;"``` : to create a database
