# Backend - Authentication & User Isolation API

FastAPI backend providing JWT-based authentication and user isolation.

## Features

- User signup with email and password
- User signin with JWT token generation
- Password hashing with bcrypt (12 rounds)
- JWT token verification
- Protected API endpoints
- User isolation enforcement
- PostgreSQL database with SQLModel ORM
- Alembic migrations

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database (Neon or local)
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL and secret key
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Authentication

- `POST /auth/signup` - Create new user account
- `POST /auth/signin` - Authenticate existing user
- `GET /auth/me` - Get current user information (requires auth)

### User

- `GET /api/{user_id}/profile` - Get user profile (requires auth, enforces user isolation)

## Testing

Run tests with pytest:
```bash
pytest
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Secret key for JWT signing (32+ characters) - preferred; also supports `BETTER_AUTH_SECRET` as fallback
- `JWT_EXPIRATION_HOURS` - Token expiration time (default: 1)

## Security Features

- Password strength validation (min 8 chars, uppercase, lowercase, number)
- Bcrypt password hashing with 12 rounds
- JWT token expiration (1 hour)
- Constant-time password comparison (timing attack prevention)
- Generic error messages (user enumeration prevention)
- User isolation at query level
- CORS configuration for frontend
