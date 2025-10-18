# Streamoid Backend - Enhanced Product Management API

A comprehensive FastAPI-based product management service that provides advanced features for product catalog management, analytics, and data processing.

## 🚀 Features

### Core Functionality
- **CSV Upload & Validation**: Bulk product upload with comprehensive validation
- **Product Management**: Full CRUD operations for individual products
- **Advanced Search**: Multi-criteria search with filtering and sorting
- **Analytics Dashboard**: Comprehensive product insights and statistics
- **RESTful API**: Well-documented API with interactive documentation

### Enhanced Features
- **Soft Delete**: Products are marked as inactive instead of being permanently deleted
- **Audit Trail**: Track creation and modification timestamps
- **Advanced Filtering**: Search by brand, color, category, price range, quantity, and tags
- **Pagination**: Efficient data retrieval with configurable page sizes
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Logging**: Structured logging for monitoring and debugging
- **Health Checks**: Built-in health monitoring endpoints

### Technical Features
- **Database Optimization**: Indexed queries for better performance
- **Input Validation**: Comprehensive data validation using Pydantic
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Docker Support**: Containerized deployment with Docker Compose
- **Environment Configuration**: Flexible configuration management

## 📋 API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed health status
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### Product Management
- `GET /api/v1/products` - List products with pagination and sorting
- `GET /api/v1/products/{id}` - Get specific product
- `POST /api/v1/products` - Create new product
- `PUT /api/v1/products/{id}` - Update existing product
- `DELETE /api/v1/products/{id}` - Soft delete product

### Search & Filtering
- `GET /api/v1/products/search` - Advanced product search
- `GET /api/v1/products/summary/stats` - Product statistics

### File Upload
- `POST /api/v1/upload` - Upload CSV file with product data

### Analytics
- `GET /api/v1/analytics/overview` - Comprehensive analytics overview
- `GET /api/v1/analytics/brands` - Brand-specific analytics
- `GET /api/v1/analytics/categories` - Category-specific analytics
- `GET /api/v1/analytics/price-distribution` - Price distribution analysis
- `GET /api/v1/analytics/trends` - Trends analysis over time

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite used by default)
- Redis (optional, for caching)
- Git (for version control)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamoid-backend
   ```

2. **Quick Start (Recommended)**
   ```bash
   ./start.sh
   ```

3. **Manual Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp env.example .env
   # Edit .env with your configuration
   
   # Run the application
   uvicorn app.main:app --reload
   ```

### Git Repository Setup

1. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Enhanced Streamoid Backend v2.0.0"
   ```

2. **Add Remote Repository**
   ```bash
   git remote add origin https://github.com/yourusername/streamoid-backend.git
   git push -u origin main
   ```

3. **Auto-Update Script**
   ```bash
   # Make executable
   chmod +x auto-update.sh
   
   # Run auto-update
   ./auto-update.sh
   ```

4. **GitHub Actions CI/CD**
   - Automatic testing on push/PR
   - Docker build verification
   - Security scanning
   - Code quality checks

### Docker Development

1. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Using Docker**
   ```bash
   docker build -t streamoid-backend .
   docker run -p 8000:8000 streamoid-backend
   ```

## 📊 Usage Examples

### Upload CSV File
```bash
curl -X POST -F "file=@products.csv" http://localhost:8000/api/v1/upload
```

### List Products
```bash
curl "http://localhost:8000/api/v1/products?page=1&limit=10&sort_by=price&sort_order=asc"
```

### Search Products
```bash
curl "http://localhost:8000/api/v1/products/search?brand=StreamThreads&min_price=400&max_price=1000&q=cotton"
```

### Get Analytics
```bash
curl "http://localhost:8000/api/v1/analytics/overview"
```

### Create Product
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TSHIRT-RED-001",
    "name": "Classic Cotton T-Shirt",
    "brand": "StreamThreads",
    "color": "Red",
    "size": "M",
    "mrp": 799,
    "price": 499,
    "quantity": 20,
    "description": "Comfortable cotton t-shirt",
    "category": "Clothing",
    "tags": "cotton,comfortable,casual"
  }'
```

## 📁 Project Structure

```
streamoid-backend/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── products.py         # Product management routes
│   │   ├── upload.py           # File upload routes
│   │   └── analytics.py        # Analytics routes
│   └── utils/
│       ├── __init__.py
│       ├── csv_parser.py       # CSV parsing utilities
│       └── error_handler.py    # Error handling middleware
├── tests/
│   ├── __init__.py
│   ├── test_upload.py          # Original test cases
│   └── test_enhanced_functionality.py # Comprehensive tests
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── env.example                 # Environment configuration template
├── .gitignore                  # Git ignore rules
├── auto-update.sh              # Auto-update script
├── start.sh                    # Easy startup script
├── PROJECT_SUMMARY.md          # Detailed project summary
├── PROJECT_STATUS.json         # Project status tracking
├── GIT_SETUP.md               # Git setup instructions
├── products_enhanced.csv       # Sample data file
└── README.md                   # This file
```

## 🧪 Testing

Run the test suite:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## 📈 Performance Considerations

- **Database Indexing**: Strategic indexes on frequently queried fields
- **Pagination**: Efficient data retrieval with configurable limits
- **Connection Pooling**: Optimized database connections
- **Caching**: Redis integration for frequently accessed data
- **Query Optimization**: Efficient SQL queries with proper filtering

## 🔒 Security Features

- **Input Validation**: Comprehensive validation using Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **File Upload Security**: File type and size validation
- **Error Handling**: Secure error messages without sensitive information
- **CORS Configuration**: Configurable cross-origin policies

## 🚀 Deployment

### Production Considerations
- Use PostgreSQL for production databases
- Configure Redis for caching
- Set up proper logging and monitoring
- Use environment variables for sensitive configuration
- Implement proper backup strategies
- Configure reverse proxy (nginx)
- Set up SSL/TLS certificates

### Environment Variables
Key environment variables for production:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `DEBUG`: Set to `false` in production
- `CORS_ORIGINS`: Configure allowed origins
- `REDIS_URL`: Redis connection string

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact: support@streamoid.com

---

**Streamoid Backend v2.0.0** - Enhanced Product Management API


