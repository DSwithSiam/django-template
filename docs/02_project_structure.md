# Project Structure

This project follows a clean, scalable layout that separates project
configuration, applications, shared utilities, and third-party integrations.

```
myproject/
│
├── config/                     # Project configuration (not an app)
│   ├── __init__.py             # Loads the Celery app
│   ├── settings.py
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py
│   ├── asgi.py
│   ├── celery.py               # Celery application
│   └── env.py                  # Environment variable parsing
│
├── apps/                       # All Django apps live here
│   ├── users/
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_services.py
│   │   ├── services/           # Write/business logic
│   │   │   ├── __init__.py
│   │   │   └── feature.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── selectors.py        # Read/query logic
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── contact/
│       └── ...
│
├── common/                     # Shared utilities, base classes, mixins
│   ├── __init__.py
│   ├── backends.py             # Auth backends
│   ├── enums.py
│   ├── exceptions.py
│   ├── mixins.py
│   ├── models.py               # BaseModel
│   ├── pagination.py
│   ├── permissions.py
│   └── serializers.py
│
├── helpers/                    # Low-level reusable helpers (response, cache, env, ...)
│
├── infrastructure/             # Third-party integrations
│   ├── email/
│   ├── storage/
│   └── payment/
│
├── templates/                  # Global templates (if server-rendered)
├── static/                     # Static assets
├── media/                      # User-uploaded content (local dev only)
│
├── requirements.txt
│
├── scripts/                    # Management scripts, data migrations
├── docs/                       # Project documentation
│
├── .env.example                # Template for local environment variables
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── manage.py
└── pyproject.toml
```

## Conventions

- **`config/`** holds project-wide configuration only. It is not a Django app.
- **`apps/`** is a namespace package; every app is referenced as `apps.<name>`
  in `INSTALLED_APPS`, but keeps its short label (e.g. `users`).
- **`services/`** contains write/business logic; **`selectors.py`** contains
  read/query logic. Keep views and serializers thin.
- **`common/`** holds cross-app base classes and mixins; **`helpers/`** holds
  lower-level utilities (standard API responses, caching, env parsing).
- **`infrastructure/`** isolates external providers (email, storage, payment)
  behind small boundaries so they can be swapped without touching apps.
