# Dead Simpl Backend - FastAPI with CloudSQL PostgreSQL

This is the backend API for Dead Simpl, built with FastAPI, CloudSQL PostgreSQL, SQLModel and Alembic.

## Features

- FastAPI for building APIs
- CloudSQL PostgreSQL for database
- SQLModel for ORM
- Alembic for database migrations
- Firebase Auth for authentication
- uv for dependency management

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

1. Set up your environment variables for database configuration or use an `.env` file based on the given example:
    ```bash
    cp .env.example .env
    ```

    Update the `.env` file with your DATABASE_URL for CloudSQL PostgreSQL connection.

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

## Deployment

This application is deployed to Google Kubernetes Engine (GKE) using:

- **CloudSQL PostgreSQL** for production database
- **Terraform** for infrastructure provisioning  
- **Helm** for Kubernetes deployment
- **Cloud Build** for CI/CD

The infrastructure configurations can be found in:
- `../terraform/staging/` - Staging environment
- `../terraform/production/` - Production environment
- `../helm/backend/` - Kubernetes deployment templates

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

Triggering build after granting secret access.

Triggering rebuild after fixing Firebase secret access via Terraform.

Testing unified image registry and tag configuration.

Testing fixed Cloud Build tagging strategy.

Testing branch-aware tagging: staging branch should create :staging tag.
