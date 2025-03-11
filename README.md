# Zone3000 test task

## Installation

### Prerequisites

- Docker: Engine: v27 Compose: v2.28

### Local setup

#### 1. Clone this repo

```
git clone https://github.com/VladislavLytvyn/zone3000_test_task.git
cd zone3000_test_task
```

#### 2. Create the `.env` file:

```
cp .env.example .env
```

#### 3. Build and run the docker container:

```
docker-compose build
docker-compose up
```

If installation succeed you will see the following in the console:
```
web-1  | Starting development server at http://0.0.0.0:8000/
web-1  | Quit the server with CONTROL-C.
```

#### 4. Run migrations 

```
docker-compose exec web python3 app/manage.py migrate
```
