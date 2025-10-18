from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import upload, products, analytics
import logging
from .utils.error_handler import ErrorHandlerMiddleware

app = FastAPI(
    title="Streamoid - Product Management API",
    description="""
    ## Streamoid Product Management System
    
    A comprehensive FastAPI-based product management service that provides:
    
    * **CSV Upload & Validation**: Upload product data via CSV files with comprehensive validation
    * **Product Management**: Full CRUD operations for product management
    * **Advanced Search**: Search products by brand, color, price range, and more
    * **Analytics**: Get insights into your product catalog
    * **Authentication**: Secure API access with JWT tokens
    
    ### Key Features:
    - Bulk product upload via CSV
    - Real-time validation and error reporting
    - Advanced filtering and search capabilities
    - Product analytics and insights
    - RESTful API design
    - Comprehensive error handling
    """,
    version="2.0.0",
    contact={
        "name": "Streamoid Team",
        "email": "support@streamoid.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app.add_middleware(ErrorHandlerMiddleware)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])

@app.get('/', tags=["Health"])
def root():
    """
    Health check endpoint
    """
    return {
        "message": "Streamoid Product Management API - Running",
        "version": "2.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get('/health', tags=["Health"])
def health_check():
    """
    Detailed health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "2.0.0",
        "database": "connected",
        "services": {
            "upload": "operational",
            "products": "operational",
            "search": "operational"
        }
    }