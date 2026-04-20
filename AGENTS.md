# E-Commerce Backend Project Specification

## 1. Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.115+ | Async REST API framework |
| Database | PostgreSQL | 16+ | Primary relational database |
| ORM | SQLAlchemy | 2.0+ (async) | Async database operations |
| Migrations | Alembic | 1.13+ | Database schema migrations |
| Cache | Redis | 7+ | Caching layer, sessions, pub/sub |
| Message Queue | Apache Kafka | 3.8+ | Event-driven messaging |
| Auth | JWT (PyJWT) | 2.10+ | Token-based authentication |
| Password Hash | bcrypt | 4.2+ | Secure password hashing |
| Validation | Pydantic | 2.10+ | Data validation |
| Testing | pytest + httpx | 8.x | Async tests |
| Container | Docker + Compose | Latest | Containerization |
| Code Quality | ruff + mypy | Latest | Linting, type checking |
| Email | Console (dev) / Resend (prod) | - | Email notifications |

---

## 2. Project Goals (Portfolio Focus)

Этот проект демонстрирует навыки работы с:
- **Redis**: кеширование популярных товаров, rate limiting, blacklist токенов, real-time аналитика
- **Kafka**: event-driven архитектура, producer/consumer паттерны, обработка событий заказов
- **FastAPI**: async/await, Pydantic v2, dependency injection, OpenAPI
- **PostgreSQL**: async SQLAlchemy, миграции, оптимизация запросов

---

## 3. Development Workflow

### Правило выполнения этапов:

1. **Делаешь этап четко по заданию** - реализуешь только то, что описано в текущей фазе
2. **Проверяешь работоспособность** - запускаешь приложение, проверяешь что ничего не сломалось
3. **Адаптируешь, фиксешь баги** - если что-то не работает, исправляешь и проверяешь снова
4. **Создаешь коммиты** - коммитишь измененные файлы с понятным сообщением

После каждого этапа: **спросить разрешения идти дальше**

---

## 4. Project Structure

```
online-shop/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection
│   ├── dependencies.py            # FastAPI dependencies
│   │
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # Main router aggregation
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management endpoints
│   │   │   ├── products.py     # Product endpoints
│   │   │   ├── categories.py   # Category endpoints
│   │   │   ├── cart.py       # Cart endpoints
│   │   │   └── orders.py     # Order endpoints
│   │   └── dependencies.py      # Shared dependencies
│   │
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, password hashing
│   │   ├── cache.py          # Redis caching utilities
│   │   ├── kafka.py          # Kafka producer/consumer
│   │   ├── rate_limiter.py   # Rate limiting
│   │   └── exceptions.py     # Custom exceptions
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   └── order.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── auth.py
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── cache_service.py
│   │   ├── kafka_service.py
│   │   └── notification_service.py
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── helpers.py
│
├── workers/                    # Background workers
│   ├── __init__.py
│   ├── kafka_consumer.py      # Kafka event consumer
│   └── notification_worker.py
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_orders.py
│   └── services/
│       ├── __init__.py
│       └── test_cache.py
│
├── alembic/                   # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── docker/                   # Docker files
│   └── Dockerfile
│
├── .env.example
├── docker-compose.yaml
├── pyproject.toml
├── ruff.toml
├── mypy.ini
├── pytest.ini
└── AGENTS.md
```

---

## 6. Database Schema

### 4.1. Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### 4.2. Categories Table

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

### 4.3. Products Table

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(12, 2) NOT NULL,
    old_price DECIMAL(12, 2),
    stock_quantity INTEGER DEFAULT 0,
    category_id UUID REFERENCES categories(id),
    image_url VARCHAR(500),
    images JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
```

### 4.4. Carts Table

```sql
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    price_at_add DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(cart_id, product_id)
);
```

### 4.5. Orders Table

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(12, 2) NOT NULL,
    shipping_address JSONB NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_number ON orders(order_number);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    total_price DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.6. Addresses Table

```sql
CREATE TABLE addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'Russia',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. API Endpoints

### 5.1. Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| POST | `/register` | Register new user | No | 201 |
| POST | `/login` | Login user | No | 200 |
| POST | `/logout` | Logout user | Yes | 200 |
| POST | `/refresh` | Refresh access token | Yes | 200 |
| GET | `/me` | Get current user | Yes | 200 |

### 5.2. Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List users | Admin | 200 |
| GET | `/{id}` | Get user by ID | Yes | 200 |
| PATCH | `/{id}` | Update user | Yes | 200 |
| DELETE | `/{id}` | Delete user | Admin | 204 |

### 5.3. Categories (`/api/v1/categories`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List categories | No | 200 |
| GET | `/{slug}` | Get category | No | 200 |
| POST | `/` | Create category | Admin | 201 |
| PATCH | `/{slug}` | Update category | Admin | 200 |
| DELETE | `/{slug}` | Delete category | Admin | 204 |

### 5.4. Products (`/api/v1/products`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List products | No | 200 |
| GET | `/{slug}` | Get product | No | 200 |
| GET | `/trending` | Get trending products | No | 200 |
| POST | `/` | Create product | Admin | 201 |
| PATCH | `/{slug}` | Update product | Admin | 200 |
| DELETE | `/{slug}` | Delete product | Admin | 204 |

### 5.5. Cart (`/api/v1/cart`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | Get cart | Yes | 200 |
| POST | `/items` | Add item | Yes | 201 |
| PATCH | `/items/{id}` | Update quantity | Yes | 200 |
| DELETE | `/items/{id}` | Remove item | Yes | 204 |
| DELETE | `/` | Clear cart | Yes | 204 |

### 5.6. Orders (`/api/v1/orders`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List orders | Yes | 200 |
| GET | `/{order_number}` | Get order | Yes | 200 |
| POST | `/` | Create order | Yes | 201 |
| PATCH | `/{order_number}/cancel` | Cancel order | Yes | 200 |
| POST | `/{order_number}/pay` | Process payment (mock) | Yes | 200 |

### 5.7. Addresses (`/api/v1/addresses`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List addresses | Yes | 200 |
| POST | `/` | Create address | Yes | 201 |
| PATCH | `/{id}` | Update address | Yes | 200 |
| DELETE | `/{id}` | Delete address | Yes | 204 |

---

## 8. Implementation Plan

### Phase 1: Foundation
- [ ] Создать структуру проекта и конфигурационные файлы
- [ ] Настроить Docker Compose (PostgreSQL, Redis, Kafka, Kafka UI)
- [ ] Настроить Alembic и создать initial миграцию
- [ ] Подключить async SQLAlchemy
- [ ] Настроить Redis client (async)
- [ ] Настроить Kafka producer
- [ ] Настроить логирование и error handling

### Phase 2: Auth & Users
- [ ] Модель User + Pydantic схемы
- [ ] Регистрация пользователя
- [ ] Логин (jwt access + refresh токены)
- [ ] Logout (blacklist токена в Redis)
- [ ] Refresh токена
- [ ] GET /me - текущий пользователь
- [ ] CRUD пользователей (admin only)

### Phase 3: Products & Categories
- [ ] Модели Category, Product
- [ ] CRUD категорий
- [ ] CRUD товаров
- [ ] Пагинация и фильтрация товаров
- [ ] [Redis] Кеширование популярных товаров
- [ ] [Redis] Инвалидация кеша при обновлении

### Phase 4: Cart & Orders
- [ ] Модели Cart, CartItem
- [ ] Добавление/удаление товаров из корзины
- [ ] Модели Order, OrderItem
- [ ] Создание заказа из корзины
- [ ] Статусная машина заказа (pending → paid → shipped → delivered)
- [ ] [Mock] Оплата заказа

### Phase 5: Redis Features
- [ ] [Redis] Rate limiting (на основе IP + user)
- [ ] [Redis] Trending products (сортировка по просмотрам)
- [ ] [Redis] Кеширование категорий
- [ ] [Redis] Счетчики просмотров товаров

### Phase 6: Kafka & Events
- [ ] [Kafka] Producer - отправка событий при создании заказа
- [ ] [Kafka] Producer - события регистрации пользователя
- [ ] [Kafka] Consumer worker - обработка событий
- [ ] [Redis] Real-time аналитика (trending products)
- [ ] [Worker] Notification service (логирование уведомлений)
- [ ] [Worker] Аналитика - обновление trending в Redis

### Phase 7: Addresses
- [ ] CRUD адресов пользователя
- [ ] Выбор адреса при оформлении заказа

### Phase 8: Testing
- [x] Unit тесты для key services (58 tests)
- [x] Интеграционные тесты для API endpoints (53 tests, requires Docker)

#### Phase 8.2: Integration Tests (Done)
- [x] API тесты для auth endpoints (/register, /login, /logout, /refresh)
- [x] API тесты для products (/, /{slug}, /trending)
- [x] API тесты для cart (/items, /items/{id})
- [x] API тесты для orders (/, /{order_number}, /{order_number}/pay)
- [x] Fixtures для test client (httpx async)
- [x] Database fixtures для тестов (PostgreSQL in Docker)
- [x] Authentication fixtures (JWT tokens)
- [x] docker-compose.test.yaml

### Phase 9: CI/CD Pipeline (Done)
- [x] GitHub Actions workflow (.github/workflows/ci.yml)
- [x] Ruff lint check
- [x] MyPy type check
- [x] PostgreSQL service container (в workflow)
- [x] Redis service container (в workflow)
- [ ] Kafka service container (тесты не используют)
- [x] pytest с coverage
- [ ] Codecov integration (требует CODECOV_TOKEN)

---

## 9. Redis Usage (Key Feature)

### 7.1. Caching Strategy

```
Кеширование ТОЛЬКО для популярных товаров:
- key: "trending:products:v1"
- TTL: 300 seconds (5 min)
- Обновляется через Kafka consumer
```

```
Кеширование категорий:
- key: "category:{slug}:v1"  
- TTL: 600 seconds (10 min)
- Инвалидация при update/delete
```

### 7.2. Rate Limiting

```
key: "rate_limit:{ip}:{user_id}"
- Проверка на каждый запрос
- Лимит: 60 запросов в минуту
- TTL: 60 seconds
```

### 7.3. Token Blacklist

```
key: "blacklist:{token_id}"
- При logout токен добавляется в blacklist
- TTL: until token expiration
- Проверка при каждом запросе
```

### 7.4. Real-time Analytics

```
key: "analytics:product_views:{product_id}"
- Инкремент при каждом просмотре товара

key: "trending:products:v1"
- Топ-N товаров по просмотрам
- Обновляется фоновым worker-ом
```

---

## 10. Kafka Topics

| Topic | Producer | Consumer | Description |
|-------|----------|----------|-------------|
| `user.registered` | auth | notifications | New user registration |
| `order.created` | orders | notifications, analytics | New order placed |
| `order.paid` | orders | notifications | Payment confirmed |
| `order.cancelled` | orders | notifications | Order cancelled |
| `product.viewed` | products | analytics | Product view event |

---

## 11. Environment Variables

```bash
# Application
APP_NAME=online-shop
APP_VERSION=1.0.0
DEBUG=true
SECRET_KEY=<generate-random-key>

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/online_shop
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# JWT
JWT_SECRET_KEY=<generate-random-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Email (dev = console, prod = resend)
EMAIL_MODE=console
```

---

## 12. Docker Compose Services

```yaml
version: '3.8'

services:
  app:
    build: ./docker
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - kafka
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: online_shop

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  kafka:
    image: apache/kafka:3.8.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESSOR_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    depends_on:
      - kafka

volumes:
  postgres_data:
  redis_data:
```

---

## 13. Acceptance Criteria

### Functional Requirements

- [ ] Users can register, login, logout
- [ ] Users can browse products and categories
- [ ] Users can add products to cart
- [ ] Users can place orders with mock payment
- [ ] Users can view order history
- [ ] Admins can manage products and categories
- [ ] JWT tokens refresh automatically

### Redis Requirements (Portfolio Focus)

- [ ] Popular products cached in Redis
- [ ] Rate limiting works correctly
- [ ] Token blacklist prevents reuse
- [ ] Trending products updated in real-time

### Kafka Requirements (Portfolio Focus)

- [ ] Order events published to Kafka
- [ ] Consumer processes order.created events
- [ ] Notifications logged asynchronously
- [ ] Analytics updated via Kafka consumer

### Non-Functional Requirements

- [ ] OpenAPI documentation at `/docs`
- [ ] All endpoints have unit tests
- [ ] Clean code with proper type hints

---

## 14. Payment Implementation

**Mock Payment Mode** (для портфолио):
- При вызове `/orders/{order_number}/pay` всегда возвращается success
- Статус заказа меняется на `paid`
- В реальном проекте можно легко заменить на Stripe/Resad

```python
# Пример реализации mock платежа
async def process_payment(order_id: UUID) -> bool:
    # Имитация проверки платежа
    await asyncio.sleep(0.5)  # simulate API call
    return True  # всегда успешно
```