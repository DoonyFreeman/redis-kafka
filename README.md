# 🛒 Online Shop API

Full-stack e-commerce backend с современным API и real-time событийной архитектурой.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-005791?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?style=flat&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=flat&logo=redis)
![Kafka](https://img.shields.io/badge/Kafka-3.8+-231F20?style=flat&logo=apache-kafka)
![TypeScript](https://img.shields.io/badge/TypeScript-Next.js_14-3178C6?style=flat&logo=typescript)

## 📌 О проекте

Production-ready e-commerce API с демонстрацией навыков работы с:
- **Redis** — кеширование, rate limiting, токен blacklist, trending products
- **Kafka** — event-driven архитектура, producer/consumer паттерны
- **FastAPI** — async/await, Pydantic v2, dependency injection
- **PostgreSQL** — async SQLAlchemy, миграции Alembic

## 🛠 Tech Stack

### Backend
| Технология | Версия | Назначение |
|------------|--------|-------------|
| FastAPI | 0.115+ | Async REST API framework |
| SQLAlchemy | 2.0+ | Async ORM |
| Alembic | 1.13+ | Database migrations |
| PostgreSQL | 16+ | Primary database |
| Redis | 7+ | Caching, sessions, pub/sub |
| Kafka | 3.8+ | Event-driven messaging |
| PyJWT | 2.10+ | Token authentication |
| bcrypt | 4.2+ | Password hashing |
| Pydantic | 2.10+ | Data validation |

### Frontend
| Технология | Версия | Назначение |
|------------|--------|-------------|
| Next.js | 14+ | React framework |
| TypeScript | 5+ | Type safety |
| shadcn/ui | latest | UI components |
| Zustand | 4+ | State management |
| TanStack Query | 5+ | Server state |
| Axios | 1+ | HTTP client |

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Node.js 18+
- Python 3.11+

### Запуск через Docker

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/online-shop.git
cd online-shop

# Запустить все сервисы
docker-compose up -d

# API доступен по адресу
http://localhost:8000

# Swagger документация
http://localhost:8000/docs
```

### Запуск frontend

```bash
cd frontend
npm install
npm run dev
# Открыть http://localhost:3000
```

### Тестовые данные

```
Email:    123@gamil.com
Password: 123@gamil.com
```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |
| POST | `/api/v1/auth/logout` | Logout user |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Get current user |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products |
| GET | `/api/v1/products/{slug}` | Get product |
| GET | `/api/v1/products/trending` | Trending products |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart` | Get cart |
| POST | `/api/v1/cart/items` | Add item |
| PATCH | `/api/v1/cart/items/{id}` | Update quantity |
| DELETE | `/api/v1/cart/items/{id}` | Remove item |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders` | List orders |
| GET | `/api/v1/orders/{order_number}` | Get order |
| POST | `/api/v1/orders` | Create order |
| POST | `/api/v1/orders/{order_number}/pay` | Process payment |

Полная документация: http://localhost:8000/docs

## 🗂 Project Structure

```
online-shop/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── dependencies.py      # FastAPI dependencies
│   │
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── categories.py
│   │   ├── cart.py
│   │   └── orders.py
│   │
│   ├── core/                # Core functionality
│   │   ├── security.py      # JWT, password hashing
│   │   ├── cache.py       # Redis caching
│   │   ├── kafka.py       # Kafka producer
│   │   └── rate_limiter.py # Rate limiting
│   │
│   ├── models/              # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   │   ├── cache_service.py
│   │   └── kafka_service.py
│   │
│   └── utils/              # Utilities
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # UI components
│   │   ├── lib/          # API client
│   │   └── store/        # Zustand store
│   └── public/
│
├── workers/               # Background workers
│   └── kafka_consumer.py
│
├── tests/                 # Test suite
│   ├── api/              # API tests
│   └── services/         # Service tests
│
├── alembic/               # Database migrations
├── docker/                # Docker files
├── docker-compose.yaml
└── pyproject.toml
```

## 🧪 Testing

```bash
# Запустить все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Только интеграционные
docker-compose -f docker-compose.test.yaml up -d
pytest tests/api/
```

## 🔑 Ключевые фичи

### Redis
- **Кеширование** — популярные товары кешируются на 5 минут
- **Rate limiting** — 60 запросов в минуту на пользователя
- **Token blacklist** — при logout токен добавляется в blacklist
- **Trending products** — real-time обновление по просмотрам

### Kafka
- **order.created** — при создании заказа
- **order.paid** — при оплате
- **product.viewed** — при просмотре товара

### Background Worker
- Потребляет события из Kafka
- Обновляет trending products в Redis
- Логирует уведомления

## 📊 Схема БД

```
users
├── id (UUID)
├── email (UNIQUE)
├── username (UNIQUE)
├── hashed_password
├── is_superuser
└── created_at

categories
├── id (UUID)
├── name
├── slug (UNIQUE)
├── parent_id (FOREIGN KEY)
└── is_active

products
├── id (UUID)
├── name
├── slug (UNIQUE)
├── price
├── stock_quantity
├── category_id (FOREIGN KEY)
└── is_active

carts → cart_items
orders → order_items
addresses
```

## 🔐 Безопасность

- JWT токены с access/refresh
- Пароли хешируются через bcrypt
- Rate limiting на основе IP + user ID
- Pydantic validation на всех вход��ых ��анных

## 📈 CI/CD

GitHub Actions:
- ruff lint check
- mypy type check
- pytest с покрытием

## 👤 Author

**Artem Rebrikov**

- Telegram: @artemrebrikov
- GitHub: github.com/artemrebrikov

## 📄 License

MIT License