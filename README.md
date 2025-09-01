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

## Environment Setup

This project supports three environments: **local development**, **staging**, and **production**.

### Quick Start (Local Development)

1. **Install dependencies:**
   ```bash
   make install
   # or: uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your Supabase credentials
   ```

3. **Start development environment:**
   ```bash
   make dev
   ```
   This will:
   - Start a local PostgreSQL database in Docker
   - Run database migrations automatically
   - Start the FastAPI server with hot reload

4. **Access the API documentation at `http://127.0.0.1:8000/docs`**

### Environment Configuration

#### Local Development
- Uses local PostgreSQL database (Docker)
- Hot reload enabled
- Debug logging
- Supabase used only for authentication

#### Staging
- Uses separate Supabase staging database
- Production-like settings
- Reduced logging

#### Production
- Uses Supabase production database
- Optimized for performance
- Multiple workers

### Available Commands

```bash
make help           # Show all available commands
make dev            # Start local development
make staging        # Start staging environment
make prod           # Start production environment
make docker-dev     # Start only PostgreSQL for development
make docker-full    # Start full stack in Docker
make migrate        # Run database migrations
make migrate-create # Create new migration
make test           # Run tests
make clean          # Clean up Docker containers
make reset-db       # Reset local database (⚠️ deletes data!)
```

### Manual Setup

If you prefer manual setup:

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **For local development with Docker:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d postgres
   ```

3. **Run migrations:**
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the server:**
   ```bash
   # Development (with hot reload)
   uv run uvicorn app.main:app --reload --reload-dir app
   
   # Production
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Database Schema Changes

When you modify `models.py`:

```bash
make migrate-create MESSAGE="your change description"
make migrate
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
# dead-simpl-backend

Triggering CI/CD pipeline.

Triggering CI/CD pipeline again.

Triggering CI/CD pipeline one more time.

Triggering CI/CD pipeline with Artifact Registry permissions.
