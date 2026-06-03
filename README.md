# Riot Match Service


Backend-сервис для сбора и агрегации данных матчей League of Legends через Riot API.

## Возможности

Сервис умеет:

* находить игрока по Riot ID (`gameName#tagLine`)
* сохранять профиль игрока и ranked-информацию
* загружать историю матчей из Riot API
* хранить нормализованные данные и raw JSON
* отдавать последние матчи игрока
* считать агрегированную статистику по чемпионам
* обновлять данные игрока через отдельный admin endpoint

## Стек

* `Python 3.11`
* `FastAPI`
* `SQLAlchemy 2.x` async
* `PostgreSQL`
* `Alembic`
* `Pydantic v2`
* `httpx`
* `structlog`
* `Docker` / `Docker Compose`
* `Poetry`

---

# Архитектура

Проект разделён на несколько слоёв:


## API layer

FastAPI routers, схемы запросов/ответов, dependency injection, exception handlers.


## Service layer

Бизнес-логика приложения:

* синхронизация данных с Riot API
* оркестрация между репозиториями
* логика обновления матчей
* работа с агрегатами


## Repository layer

Изолированная работа с БД через SQLAlchemy Core.


## Integration layer

Клиент Riot API:

* async httpx client
* rate limiting
* retry logic
* обработка ошибок Riot API
* pydantic-схемы внешнего API


## Mappers

Преобразование Riot API моделей во внутренние DTO/data-классы.


## Model layer

* lazy='selectin' для части relationships
* PostgreSQL indexes и constraints
* JSONB для хранения raw Riot API payloads
* TimestampMixin с created_at и updated_at


## Logging

Структурированное логирование через `structlog`.

* единое форматирование логов для приложения и используемых библиотек
* ConsoleRenderer - для dev, машиночитаемый JSONRenderer - для production

---


# Запуск проекта

## 1. Клонировать проект

```bash
git clone <repo_url>
cd riot-match-service
```

## 2. Создать `.env`

Образец есть в `.env.example`.

## 3. Запустить проект

```bash
docker compose up --build
```

После запуска:

* API: `http://localhost:8000`
* Swagger docs: `http://localhost:8000/docs`

---

# Разработка

Для удобства разработки используется отдельный compose-файл:

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

Особенности dev-конфига:

* hot reload через `uvicorn --reload`
* проброс проекта volume-монтом
* postgres доступен снаружи на порту `5434` на случай имеющегося локального postgres

---

# Миграции

При старте production compose Alembic запускается автоматически.

В dev compose после запуска выполнить:

```bash
docker compose -f docker-compose.dev.yml exec api alembic upgrade head
```

Чтобы создать миграцию выполнить:

```bash
docker compose -f docker-compose.dev.yml exec api alembic revision --autogenerate
```

Файл миграции создастся по пути `alembic/versions/new_migration_file.py`, где `new_migration_file.py` - имя файла.

Рекомендуется проверить новый файл миграции перед применением. После проверки повторить команду `alembic upgrade head`.

---

# Эндпоинты

# Healthcheck

```http
GET /healthz
```

Проверяет доступность PostgreSQL.

---

## Найти игрока по `Riot ID`

```http
GET /api/players/by-riot-id
```

**Query params**:

* `platform` string
* `game_name` string
* `tag_line` string

**Ответ**:

```json
{
  "puuid": "string"
}
```

---

## Профиль игрока

```http
GET /api/players/{puuid}
```

**Path params**:

* `puuid` string

**Ответ**:

```json
{
  "puuid": "string",
  "game_name": "string",
  "tag_line": "string",
  "summoner_level": 0,
  "profile_icon_id": 0,
  "ranked_entries": [
    {
      "queue_type": "string",
      "tier": "string",
      "rank": "string",
      "league_points": 0,
      "wins": 0,
      "losses": 0
    }
  ]
}
```

---

## Последние матчи

```http
GET /api/players/{puuid}/matches
```

**Path params**:

* `puuid` string

**Query params**:

* `limit` integer (1-50)

**Ответ**:

```json
[
  {
    "match_id": "string",
    "queue_id": 0,
    "game_mode": "string",
    "game_patch": "string",
    "started_at": "2026-05-28T07:13:18.558Z",
    "game_duration": 0,
    "champion_name": "string",
    "team_position": "string",
    "kills": 0,
    "deaths": 0,
    "assists": 0,
    "win": true
  }
]
```

---

## Статистика по чемпионам

Сейчас аналитика строится только по SoloQ (`queue_id = 420`).

```http
GET /api/players/{puuid}/champions
```

**Path params**:

* `puuid` string

**Query params**:

* `recent_matches` integer (1-50)

**Ответ**:

```json
[
  {
    "champion_name": "string",
    "games": 0,
    "wins": 0,
    "losses": 0,
    "win_rate": 0,
    "average_kills": 0,
    "average_deaths": 0,
    "average_assists": 0,
    "average_kda": 0,
    "average_cs": 0
  }
]
```

---

## Запуск синхронизации

```http
POST /api/admin/players/sync
```

**Body**:

```json
{
  "platform": "string",
  "game_name": "string",
  "tag_line": "string"
}
```

**Ответ**:

```json
{
  "status": "sync_started"
}
```

Синхронизация запускается в фоновом режиме и не блокирует HTTP-запрос.

---

# Работа с Riot API

## Routing

Используются оба типа Riot routing:

### Platform routing

Для:

* summoner-v4
* league-v4

Пример:

```text
https://euw1.api.riotgames.com
```

### Regional routing

Для:

* account-v1
* match-v5

Пример:

```text
https://europe.api.riotgames.com
```

Маппинг platform -> region вынесен в отдельный mapper.

---

# Стратегия хранения данных

## Player

Таблица `players` хранит:

* tracked игроков (`is_tracked=True`)
* untracked игроков из матчей (`is_tracked=False`)

Это позволяет:

* сохранять связи участников матчей
* не загружать лишние профили из Riot API

Идентичность игрока строится только на `PUUID`.

Riot ID не используется как primary key, потому что может меняться.

---

## Raw JSON

Сырые ответы Riot API сохраняются:

* `Match.raw_data`
* `RankedEntry.raw_data`

Для `Player` raw JSON не хранится, потому что все поля уже нормализованы.

Для `MatchParticipant` raw JSON не хранится, так как данные участников уже содержатся внутри `Match.raw_data`.

---

# Стратегия синхронизации матчей

Сервис не перекачивает уже сохранённые матчи.

## Как работает обновление

При синхронизации:

1. Находим последний сохранённый матч игрока
2. Берём время конца матча `ended_at` (оригинальный `gameEndTimestamp`)
3. Передаём его в Riot API как `startTime`
4. Получаем данные только новых матчей

Используется:

```python
startTime = latest_match_end + 2 seconds
```

Небольшое смещение нужно, чтобы Riot API гарантированно не вернул последний уже сохранённый матч повторно.

---

## Ограничение глубины истории

Если игрок синхронизируется впервые или давно не обновлялся, сервис ограничивает глубину загрузки 30 днями.

Это предотвращает:

* слишком долгие синхронизации
* избыточные запросы к Riot API
* проблемы с rate limits

---

# Обработка незавершённых матчей

Riot API иногда возвращает незавершённые матчи - без `gameEndTimestamp`.

Такие матчи не сохраняются в БД.

---

# Rate limiting и retry policy

В Riot API client реализованы:

### Rate limiters

На каждый host создаются два limiter-а:

* 20 req/sec
* 100 req / 2 min

Используется `aiolimiter`.

---

### Retry policy

### Retry выполняется для:

* ошибки сети - exponential backoff
* `429` - `Retry-After`
* `5xx` - exponential backoff

### Не ретраятся:

* `403`
* `404`

---

# Асинхронная архитектура

## Один AsyncClient на процесс

`httpx.AsyncClient` создаётся один раз в lifespan приложения и переиспользуется.

Это позволяет:

* переиспользовать connection pool
* избежать лишних TCP connections
* корректно работать rate limiter-ам

---

## Background tasks

Синхронизация запускается через `asyncio.create_task`.

Активные задачи сохраняются в:

```python
app.state.background_tasks
```

При shutdown приложения все background tasks корректно отменяются.

---

# Pydantic и Riot API

Все Riot API схемы используют:

```python
extra='ignore'
```

Это защищает сервис от падений при появлении новых полей в Riot API.

---

# Логирование

Используется `structlog` поверх стандартного `logging`.

При `DEBUG=True` используется `ConsoleRenderer` - логи выводятся в удобном для чтения человеком формате.

При `DEBUG=False` используется `JSONRenderer` - логи выводятся в виде JSON-событий, пригодных для агрегации и парсинга системами мониторинга.

---

# Code quality

Используются:

* flake8
* isort
* mypy
* pre-commit

Проверки запускаются через:

```bash
pre-commit run 
```
