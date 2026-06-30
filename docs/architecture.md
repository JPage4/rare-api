# Rare System Architecture

```mermaid
graph TD
    Browser["Browser\nlocalhost:3000"]

    subgraph Client["React Client (rare-client)"]
        Components["Components\nUI forms and views"]
        Managers["Managers\nAPI call functions"]
        LocalStorage["localStorage\nauth_token, current_user_id"]
    end

    subgraph API["Django REST Framework API (rare-api)\nlocalhost:8000"]
        URLs["urls.py\nRoute matching"]
        Views["Views\nBusiness logic, auth checks"]
        Serializers["Serializers\nResponse shaping"]
        ORM["Django ORM\nDatabase queries"]
        MediaFiles["Media files\nmedia/post_images/"]
    end

    subgraph Docker["Docker"]
        Postgres["PostgreSQL 16\nlocalhost:5432\nDatabase: rare"]
        Volume["Volume: rare_db_data\nPersistent storage"]
    end

    Browser --> Components
    Components --> Managers
    Managers -->|"HTTP POST/GET/PUT/DELETE\nAuthorization: Token <token>"| URLs
    Managers -->|"Read/write token"| LocalStorage
    URLs --> Views
    Views --> Serializers
    Views --> ORM
    Views -->|"Save uploaded images"| MediaFiles
    Serializers -->|"JSON response"| Managers
    ORM -->|"psycopg2\nSQL queries"| Postgres
    Postgres --- Volume
```

## Components

| Component | Technology | Responsibility |
|---|---|---|
| React Client | Create React App, Bulma, react-router-dom | UI, routing, token storage |
| Managers | Plain JS fetch functions | One file per resource — abstracts all API calls from components |
| Django API | Django 4.2 + Django REST Framework | Auth, business logic, moderation rules |
| Views | DRF function-based views | Handle HTTP methods, enforce permissions, read `request.data` |
| Serializers | DRF ModelSerializers | Shape ORM objects into JSON responses |
| PostgreSQL | Postgres 16 in Docker | Persistent relational storage |
| Media files | Local filesystem | Uploaded post and profile images stored under `media/` |

## Communication

- **Client → API**: JSON over HTTP. Every authenticated request includes `Authorization: Token <token>` in the header. CORS is restricted to `localhost:3000`.
- **API → Database**: Django ORM via the psycopg2 driver. No raw SQL.
- **Auth flow**: Client POSTs credentials to `/login` or `/register`, receives a token, stores it in `localStorage`, and attaches it to all subsequent requests. DRF's `TokenAuthentication` middleware validates the token on every request.
