# Health Score API

A modern, secure FastAPI application for comprehensive health data management with OAuth2 authentication and rolling codes. Track, analyze, and visualize health metrics with a robust and scalable API.

> **Note:** This repository accompanies my diploma project. The commit history reflects the work completed during the project period. A dev `.env` is included for quick Docker startup.



## Features

- **Comprehensive Health Tracking**: Track over 40+ health metrics including vitals, body composition, activity, sleep, and nutrition
- **Advanced Analytics**: Built-in aggregation and trend analysis for health metrics over time
- **Secure Authentication**: OAuth2 with JWT tokens and rolling codes for enhanced security
- **RESTful API**: Clean, versioned endpoints following REST best practices
- **Asynchronous Processing**: Built with async/await for high performance
- **Type Safety**: Full type hints and Pydantic validation
- **Containerized**: Ready for Docker and Kubernetes deployments
- **Cloud-Native**: Designed for AWS with Terraform infrastructure as code
- **Structured Logging**: Integration with AWS DynamoDB for audit trails
- **Interactive Documentation**: Auto-generated OpenAPI/Swagger UI

## Project Structure

```
health_score_api/
├── app/                    # Main application code
│   ├── api/                # API endpoints
│   │   └── v1/             # Versioned API endpoints
│   ├── core/               # Core utilities and configuration
│   ├── db/                 # Database models and session management
│   ├── schemas/            # Pydantic schemas for validation
│   ├── services/           # Business logic services
│   ├── logging/            # Logging utilities
│   ├── tests/              # Automated test suite
│   └── main.py             # FastAPI application entry point
├── infrastructure/         # Deployment configurations
│   ├── Dockerfile          # Docker image definition
│   ├── docker-compose.yml  # Docker composition for local development
│   ├── terraform/          # Terraform scripts for AWS infrastructure
│   ├── aws_ec2/            # EC2 setup scripts
│   └── aws_dynamodb/       # DynamoDB logging setup
├── scripts/                # Utility scripts
└── requirements.txt        # Python dependencies
```

## Technology Stack

- **Framework**: FastAPI (Asynchronous)
- **Database**: PostgreSQL with SQLAlchemy Async
- **Authentication**: OAuth2 with JWT tokens and rolling codes
- **Deployment**: AWS EC2 (using Terraform)
- **Logging**: AWS DynamoDB
- **Containerization**: Docker

## Quick start (Docker)
   ```bash
    git clone https://github.com/Moiraines/health_score_api.git
    cd health_score_api
    docker compose up --build
   ```
API: http://localhost:8000

Swagger: http://localhost:8000/docs

PgAdmin: http://localhost:5050 (email: admin@healthscore.com, pass: admin)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 14+
- Redis (for caching and rate limiting)
- AWS CLI (for deployment)
- Terraform 1.5+ (for infrastructure)

### Local Development

1. **Clone and Setup**
   ```bash
   git clone https://github.com/Moiraines/health_score_api.git
   cd health-score-api
   
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start Services**
   ```bash
   # Start PostgreSQL, Redis, and other dependencies
   docker-compose up -d postgres redis
   
   # Install Python dependencies
   pip install -e ".[dev]"
   
   # Run database migrations
   alembic upgrade head
   ```

3. **Run the Application**
   ```bash
   # Development server with hot reload
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**
   - API: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

### Running with Docker

```bash
# Build and start all services
docker-compose up --build

# Run specific service
docker-compose up api

# View logs
docker-compose logs -f
```

### Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Reset database (DANGER: drops all data!)
scripts/reset_db.sh
```

### Seeding Test Data

```bash
# Seed database with sample data
python scripts/init_test_data.py

# Create admin user
python scripts/init_admin.py
```

## API Endpoints

### Authentication

- `POST /api/v1/token` - Obtain access and refresh tokens
- `POST /api/v1/refresh` - Refresh tokens using refresh token

### User Management

- `POST /api/v1/users/` - Register a new user
- `GET /api/v1/users/me/` - Get current user information
- `GET /api/v1/users/{user_id}` - Get specific user information (admin or self)

### Health Metrics

#### Core Operations
- `POST /api/v1/health/metrics` - Record a new health metric
- `GET /api/v1/health/metrics` - List health metrics with filtering
- `GET /api/v1/health/metrics/{metric_id}` - Get specific metric details
- `PUT /api/v1/health/metrics/{metric_id}` - Update a metric
- `DELETE /api/v1/health/metrics/{metric_id}` - Delete a metric

#### Analytics & Aggregations
- `GET /api/v1/health/metrics/types/{metric_type}/aggregate` - Get aggregated metrics data
  - Supports daily/weekly/monthly aggregation
  - Returns min, max, avg, and median values
- `GET /api/v1/health/metrics/trends` - Get trend analysis for specific metrics
  - Calculate percentage changes
  - Visualize historical patterns

### Health Scores (Legacy)
- `POST /api/v1/health-scores/` - Create a new health score entry
- `GET /api/v1/health-scores/` - List health scores
- `GET /api/v1/health-scores/{score_id}` - Get score details
- `PUT /api/v1/health-scores/{score_id}` - Update a score
- `DELETE /api/v1/health-scores/{score_id}` - Delete a score

## Key Features

### Health Metrics Tracking
- **40+ Metric Types**: Track everything from vitals to nutrition
- **Flexible Units**: Automatic unit conversion and validation
- **Temporal Data**: Precise timestamp tracking with timezone support
- **Source Attribution**: Track data source (device, manual entry, etc.)

### Analytics & Insights
- **Time-based Aggregations**: Daily, weekly, monthly rollups
- **Trend Analysis**: Identify patterns and changes over time
- **Statistical Summaries**: Min, max, average, and median calculations
- **Custom Date Ranges**: Flexible filtering by time periods

### Security & Compliance
- **OAuth2 with JWT**: Secure authentication with rolling codes
- **Role-Based Access Control**: Fine-grained permissions
- **Data Validation**: Pydantic models for type safety
- **Audit Logging**: Complete history of all changes
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: Protection against abuse

## 🚀 Deployment

### Docker Compose (Production)

```bash
# Build and start in production mode
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### AWS Deployment with Terraform

1. **Prerequisites**
   - AWS account with proper IAM permissions
   - Configured AWS CLI
   - Terraform 1.5+

2. **Deploy Infrastructure**
   ```bash
   cd infrastructure/terraform
   
   # Initialize Terraform
   terraform init
   
   # Review changes
   terraform plan
   
   # Apply configuration
   terraform apply
   ```

3. **Post-Deployment**
   - Access the API at the load balancer DNS
   - Run database migrations
   - Set up monitoring and alerts

### Kubernetes (Optional)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# View pods
kubectl get pods -n health-score
```

## Logging

This application integrates with AWS DynamoDB for structured logging of events, errors, and metrics. Configure your AWS credentials in the `.env` file to enable logging.

## 🧪 Testing

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest app/tests/api/v1/test_health_metrics.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Test Coverage

```bash
# Generate coverage report
coverage html
open htmlcov/index.html  # View in browser
```

### Linting & Code Quality

```bash
# Run black code formatter
black .

# Check code style
flake8
# Type checking
mypy .
# Sort imports
isort .
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Workflow

1. **Before Starting**
   - Check open issues for existing work
   - Open an issue to discuss major changes

2. **Coding Standards**
   - Follow PEP 8 and Google Python Style Guide
   - Use type hints for all functions
   - Write docstrings for all public methods
   - Include tests for new features

3. **Commit Messages**
   - Use the format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Example: `feat(api): add health metrics aggregation endpoint`

4. **Pull Requests**
   - Reference related issues
   - Update documentation
   - Ensure tests pass
   - Get code review approval

### Local Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Resources

- [API Documentation](https://api.healthscore.example.com/docs) (replace with your URL)
- [Development Guide](docs/DEVELOPMENT.md)
- [API Client Libraries](#) (coming soon)
- [Changelog](CHANGELOG.md)

## 📬 Contact

For support or questions, please contact [support@healthscore.example.com](mailto:support@healthscore.example.com) or open an issue in the repository.

---

<div align="center">
  Made with ❤️ by the Health Score Team
</div>
