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

---

## 2. Project Structure

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
│   ���── conftest.py
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
│   ├── Dockerfile
│   └── nginx.conf
│
├── scripts/                  # Utility scripts
│   └── init_db.py
│
├── .env.example
├── .env.docker
├── docker-compose.yaml
├── pyproject.toml
├── ruff.toml
├── mypy.ini
├── pytest.ini
└── AGENTS.md
```

---

## 3. Database Schema

### 3.1. Users Table

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

### 3.2. Categories Table

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

### 3.3. Products Table

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

### 3.4. Carts Table

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

### 3.5. Orders Table

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

### 3.6. Addresses Table

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

## 4. API Endpoints

### 4.1. Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| POST | `/register` | Register new user | No | 201 |
| POST | `/login` | Login user | No | 200 |
| POST | `/logout` | Logout user | Yes | 200 |
| POST | `/refresh` | Refresh access token | Yes | 200 |
| GET | `/me` | Get current user | Yes | 200 |

### 4.2. Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List users | Admin | 200 |
| GET | `/{id}` | Get user by ID | Yes | 200 |
| PATCH | `/{id}` | Update user | Yes | 200 |
| DELETE | `/{id}` | Delete user | Admin | 204 |

### 4.3. Categories (`/api/v1/categories`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List categories | No | 200 |
| GET | `/{slug}` | Get category | No | 200 |
| POST | `/` | Create category | Admin | 201 |
| PATCH | `/{slug}` | Update category | Admin | 200 |
| DELETE | `/{slug}` | Delete category | Admin | 204 |

### 4.4. Products (`/api/v1/products`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List products | No | 200 |
| GET | `/{slug}` | Get product | No | 200 |
| GET | `/{slug}/related` | Related products | No | 200 |
| POST | `/` | Create product | Admin | 201 |
| PATCH | `/{slug}` | Update product | Admin | 200 |
| DELETE | `/{slug}` | Delete product | Admin | 204 |

### 4.5. Cart (`/api/v1/cart`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | Get cart | Yes | 200 |
| POST | `/items` | Add item | Yes | 201 |
| PATCH | `/items/{id}` | Update quantity | Yes | 200 |
| DELETE | `/items/{id}` | Remove item | Yes | 204 |
| DELETE | `/` | Clear cart | Yes | 204 |

### 4.6. Orders (`/api/v1/orders`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List orders | Yes | 200 |
| GET | `/{order_number}` | Get order | Yes | 200 |
| POST | `/` | Create order | Yes | 201 |
| PATCH | `/{order_number}/cancel` | Cancel order | Yes | 200 |
| POST | `/{order_number}/pay` | Process payment | Yes | 200 |

### 4.7. Addresses (`/api/v1/addresses`)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-----------|------|--------|
| GET | `/` | List addresses | Yes | 200 |
| POST | `/` | Create address | Yes | 201 |
| PATCH | `/{id}` | Update address | Yes | 200 |
| DELETE | `/{id}` | Delete address | Yes | 204 |

---

## 5. Implementation Plan

### Phase 1: Foundation (Week 1)

- [ ] Initialize project with FastAPI structure
- [ ] Configure Docker Compose with PostgreSQL, Redis, Kafka
- [ ] Set up Alembic migrations
- [ ] Implement database connection and base models
- [ ] Configure logging and error handling

### Phase 2: Core Entities (Week 2)

- [ ] Implement User model and authentication
- [ ] Implement Category model and CRUD
- [ ] Implement Product model and CRUD
- [ ] Add Pydantic schemas for all entities
- [ ] Write basic unit tests for models

### Phase 3: Business Logic (Week 3)

- [ ] Implement Cart service with Redis storage
- [ ] Implement Order service with status machine
- [ ] Add address management
- [ ] Implement JWT refresh token rotation
- [ ] Add RBAC (role-based access control)

### Phase 4: Caching & Performance (Week 4)

- [ ] Implement Redis caching layer for products
- [ ] Add cache invalidation strategies
- [ ] Implement query optimization with indexes
- [ ] Add rate limiting
- [ ] Performance testing and profiling

### Phase 5: Event-Driven Architecture (Week 5)

- [ ] Set up Kafka producer for events
- [ ] Implement Kafka consumer worker
- [ ] Add notification service
- [ ] Implement real-time analytics with Redis
- [ ] Add event retry logic and dead letter queue

### Phase 6: Testing & Optimization (Week 6)

- [ ] Write integration tests
- [ ] Write E2E tests with Playwright
- [ ] Security audit and fixes
- [ ] Load testing with k6
- [ ] Documentation and OpenAPI specs

---

## 6. Kafka Topics

| Topic | Event Type | Description |
|-------|-----------|-------------|
| `user.registered` | UserCreated | New user registration |
| `user.updated` | UserUpdated | User profile update |
| `product.created` | ProductCreated | New product added |
| `product.updated` | ProductUpdated | Product updated |
| `product.out_of_stock` | ProductOutOfStock | Product stock depleted |
| `order.created` | OrderCreated | New order placed |
| `order.paid` | OrderPaid | Payment confirmed |
| `order.shipped` | OrderShipped | Order shipped |
| `order.cancelled` | OrderCancelled | Order cancelled |

---

## 7. Redis Keys Schema

| Key Pattern | Type | TTL | Description |
|------------|-----|-----|-------|
| `product:{id}:v1` | JSON | 300s | Product details |
| `products:list:{filter_hash}:v1` | JSON | 60s | Product list cache |
| `category:{id}:v1` | JSON | 600s | Category details |
| `trending:products:v1` | JSON | 300s | Popular products |
| `cart:{user_id}:v1` | JSON | 7d | User cart |
| `blacklist:{token_id}` | string | token_ttl | JWT blacklist |
| `rate_limit:{identifier}` | int | 60s | Rate limit counter |

---

## 8. Environment Variables

```bash
# Application
APP_NAME=online-shop
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=<generate-random-key>

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/online_shop
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
```

---

## 9. Docker Compose Services

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

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      REDIS_HOSTS: local:redis:6379

volumes:
  postgres_data:
  redis_data:
```

---

## 10. Acceptance Criteria

### Functional Requirements

- [ ] Users can register, login, logout
- [ ] Users can browse products and categories
- [ ] Users can add products to cart
- [ ] Users can place orders
- [ ] Users can view order history
- [ ] Admins can manage products and categories
- [ ] JWT tokens refresh automatically

### Non-Functional Requirements

- [ ] API response time < 200ms for cached requests
- [ ] Support 1000+ concurrent users
- [ ] 99.9% uptime
- [ ] All endpoints have tests
- [ ] OpenAPI documentation at `/docs`

### Caching Requirements

- [ ] Products cached in Redis with 5-minute TTL
- [ ] Cache invalidation on product update
- [ ] Rate limiting per user/IP

### Event-Driven Requirements

- [ ] Order events published to Kafka
- [ ] Background workers process events
- [ ] Notifications sent async