# Zone3000 test task

## Installation

### Prerequisites

- Docker: Engine: v27 Compose: v2.28

### Local setup

#### 1. Create the `.env` file:

```
cp .env.example .env
```

#### 2. Build and run the docker container:

```
docker compose build
docker compose up
```

If installation succeed you will see the following in the console:
```
web-1  | Starting development server at http://0.0.0.0:8000/
web-1  | Quit the server with CONTROL-C.
```

#### 3. Run migrations 

```
docker compose exec web python3 app/manage.py migrate
```
