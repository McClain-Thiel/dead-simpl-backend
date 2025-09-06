# Minimal template for FastAPI, Supabase, SQLModel and Alembic


This is a minimal template for a FastAPI project with Supabase, SQLModel and Alembic.

## Features

- FastAPI for building APIs
- Supabase for authentication and database
- SQLModel for ORM
- Alembic for database versionning and migrations
- uv for dependency management

The project features a basic example of a bookmark application, supporting CRUD operations with Supabase authentication (including compatibility with Swagger's Auth).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/aipocket.git
    cd aipocket
    ```

2. Install UV:
    ```bash
    pip install uv
    ```
    You don't have to do that in a virtual environment, as UV is a standalone tool.
    UV will later on install the dependencies for you in a virtual environnement.

## Usage

1. Set up your environment variables for Supabase and database configuration or use an `.env` file based on the given example:
    ```bash
    cp .env.example .env
    ```

    Update the `.env` file with your Supabase URL, Supabase key, database URL, and database URL for migrations.

2. (Optional) In case you perform modifications to `models.py` (ie. modification to the DB scheme): Generate a new Alembic migration:
    ```bash
    uv run alembic revision --autogenerate -m "Your message here"
    ```

3. Run the database migrations:
    ```bash
    uv run alembic upgrade head
    ```

4. Start the FastAPI server:
    ```bash
    uv run uvicorn app.main:app --reload --reload-dir app
    ```
    At the first run, UV will create a virtual environment and install the dependencies inside it.

5. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Local Development with Docker and Supabase

To run the application locally using Docker and a local Supabase instance, follow these steps:

1.  **Start Local Supabase:**
    Ensure you have the Supabase CLI installed. Navigate to the `supabase/` directory and start the local Supabase services:
    ```bash
    npx supabase start
    ```
    This will spin up all necessary Docker containers for Supabase (Postgres, Auth, Storage, etc.) and output connection details.

2.  **Configure Environment Variables:**
    The application needs to connect to the local Supabase instance. Update your `.env` file with the details provided by `npx supabase start`. Specifically, ensure `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_DB_STRING` are correctly set. The `SUPABASE_DB_STRING` should point to the internal Docker service name for the database, e.g., `postgresql://postgres:postgres@supabase_db_dead-simpl-backend:5432/postgres`.

3.  **Build the Application Docker Image:**
    Navigate back to the root of the `dead-simpl-backend` directory and build the application's Docker image:
    ```bash
    docker build -t dead-simpl-backend .
    ```
    

4.  **Run Database Migrations:**
    Before starting the application, ensure your database schema is up-to-date by running Alembic migrations inside a temporary container:
    ```bash
    docker run --rm --network supabase_network_dead-simpl-backend --env-file .env dead-simpl-backend alembic upgrade head
    ```

5.  **Run the Application Container:**
    Start the application, connecting it to the same Docker network as Supabase:
    ```bash
    docker run -d --name dead-simpl-backend-app -p 8000:8000 --network supabase_network_dead-simpl-backend --env-file .env dead-simpl-backend
    ```
    This will expose the application on `http://localhost:8000`.

6.  **Verify Application Status:**
    Check the application logs to ensure it started successfully and connected to the database:
    ```bash
    docker logs -f dead-simpl-backend-app
    ```

7.  **Access the API:**
    The API documentation will be available at `http://localhost:8000/docs`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
# dead-simpl-backend

Triggering CI/CD pipeline.

Triggering CI/CD pipeline again.

Triggering CI/CD pipeline one more time.

Triggering CI/CD pipeline with Artifact Registry permissions.

Triggering CI/CD pipeline again to fix the build.
