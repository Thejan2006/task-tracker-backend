# Task & Resource Tracker Backend

FastAPI/PostgreSQL backend for the task tracker. Protected resources are scoped
to the authenticated user; task state and Kanban ordering are persisted in the
database.

## Endpoints

- `POST /users/` registers a user; `POST /login` returns a JWT.
- `GET/POST /tasks/`, `PUT/DELETE /tasks/{id}` manage owned tasks. Tasks expose
  `status` (`todo`, `in_progress`, `review`, `done`), contiguous `position`,
  `priority`, timestamps, and `is_completed`.
- `GET/POST /categories/` manages owned categories.
- `GET /users/me` and multipart `PUT /users/me` manage profile fields and avatars.
- Admin-only `GET /users/admin/users`, `PATCH /users/admin/users/{id}`, and
  `DELETE /users/admin/users/{id}` manage accounts. Use `?search=` and
  `?status=all|active|disabled`.
- `GET /dashboard/stats` returns current-user task counts, status groups, recent
  activity, overdue tasks, and a 30-day completion trend.

All protected endpoints require `Authorization: Bearer <token>`. Disabled users
are rejected even when they hold an unexpired token. Users cannot change their
own role, and the last active admin cannot be disabled or deleted.

## Database and configuration

Run `alembic upgrade head` against an existing database before starting the API.
This applies the `users` schema alignment, including `is_verified`, `otp`, and
`otp_code`, as well as task workflow fields, profile fields, and the
`activities` table without deleting records. Legacy completed tasks become
`done` and positions are generated per owner/status column. Docker Compose waits
for PostgreSQL to become ready and runs this migration automatically before
starting the API.

Set `SQLALCHEMY_DATABASE_URL` or `DATABASE_USERNAME`, `DATABASE_PASSWORD`,
`DATABASE_HOSTNAME`, `DATABASE_PORT`, and `DATABASE_NAME`. Set `SECRET_KEY`,
`ALGORITHM`, `FRONTEND_ORIGIN`, and optionally `ACCESS_TOKEN_EXPIRE_MINUTES`.
The development fallback secret must not be used in production.

Avatar uploads are validated to JPEG, PNG, GIF, or WebP and limited to 5 MB.
They are stored under `uploads/avatars` and served at `/uploads/...`; mount that
directory as persistent storage in production. Restrict `allow_origins` in
`app/main.py` to the frontend origin when deploying outside local development.

## Tests

Run `python -m pytest -q`. The repository tests use an in-memory SQLite override;
production uses PostgreSQL through `SQLALCHEMY_DATABASE_URL`.

The API intentionally does not implement external object-storage uploads or
email/password reset flows. Local avatar storage is the supported backend
implementation.
