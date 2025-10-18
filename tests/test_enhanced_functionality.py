import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import Product

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_product_data():
    return {
        "sku": "TEST-SKU-001",
        "name": "Test Product",
        "brand": "TestBrand",
        "color": "Blue",
        "size": "M",
        "mrp": 1000.0,
        "price": 800.0,
        "quantity": 10,
        "description": "A test product",
        "category": "TestCategory",
        "tags": "test,product,sample"
    }

def test_health_endpoints():
    """Test health check endpoints"""
    response = client.get("/")
    assert response.status_code == 200
    assert "healthy" in response.json()["status"]
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_product(setup_database, sample_product_data):
    """Test product creation"""
    response = client.post("/api/v1/products", json=sample_product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == sample_product_data["sku"]
    assert data["name"] == sample_product_data["name"]
    assert data["id"] is not None

def test_get_product(setup_database, sample_product_data):
    """Test getting a specific product"""
    # First create a product
    create_response = client.post("/api/v1/products", json=sample_product_data)
    product_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["sku"] == sample_product_data["sku"]

def test_update_product(setup_database, sample_product_data):
    """Test product update"""
    # First create a product
    create_response = client.post("/api/v1/products", json=sample_product_data)
    product_id = create_response.json()["id"]
    
    # Update it
    update_data = {"name": "Updated Test Product", "price": 900.0}
    response = client.put(f"/api/v1/products/{product_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Product"
    assert response.json()["price"] == 900.0

def test_delete_product(setup_database, sample_product_data):
    """Test product soft delete"""
    # First create a product
    create_response = client.post("/api/v1/products", json=sample_product_data)
    product_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204
    
    # Verify it's soft deleted (should not appear in active products)
    response = client.get("/api/v1/products")
    products = response.json()["products"]
    assert not any(p["id"] == product_id for p in products)

def test_list_products_pagination(setup_database):
    """Test product listing with pagination"""
    # Create multiple products
    for i in range(15):
        product_data = {
            "sku": f"TEST-SKU-{i:03d}",
            "name": f"Test Product {i}",
            "brand": "TestBrand",
            "mrp": 1000.0,
            "price": 800.0,
            "quantity": 10
        }
        client.post("/api/v1/products", json=product_data)
    
    # Test pagination
    response = client.get("/api/v1/products?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) == 10
    assert data["total"] >= 15
    assert data["page"] == 1
    assert data["limit"] == 10

def test_search_products(setup_database, sample_product_data):
    """Test product search functionality"""
    # Create a product
    client.post("/api/v1/products", json=sample_product_data)
    
    # Search by brand
    response = client.get("/api/v1/products/search?brand=TestBrand")
    assert response.status_code == 200
    assert len(response.json()["products"]) >= 1
    
    # Search by price range
    response = client.get("/api/v1/products/search?min_price=700&max_price=900")
    assert response.status_code == 200
    assert len(response.json()["products"]) >= 1
    
    # Text search
    response = client.get("/api/v1/products/search?q=Test")
    assert response.status_code == 200
    assert len(response.json()["products"]) >= 1

def test_analytics_endpoints(setup_database, sample_product_data):
    """Test analytics endpoints"""
    # Create a product first
    client.post("/api/v1/products", json=sample_product_data)
    
    # Test analytics overview
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "price_analytics" in data
    assert "inventory_analytics" in data
    
    # Test brand analytics
    response = client.get("/api/v1/analytics/brands")
    assert response.status_code == 200
    assert "brands" in response.json()
    
    # Test category analytics
    response = client.get("/api/v1/analytics/categories")
    assert response.status_code == 200
    assert "categories" in response.json()

def test_csv_upload(setup_database):
    """Test CSV file upload"""
    csv_content = """sku,name,brand,color,size,mrp,price,quantity,description,category,tags
TEST-CSV-001,CSV Test Product,TestBrand,Red,M,1000,800,5,Test description,TestCategory,test,csv
TEST-CSV-002,Another CSV Product,TestBrand,Blue,L,1200,900,3,Another description,TestCategory,test,csv"""
    
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["stored"] >= 2
    assert data["success_rate"] > 0

def test_validation_errors():
    """Test input validation"""
    # Test invalid product data
    invalid_data = {
        "sku": "",  # Empty SKU
        "name": "Test Product",
        "brand": "TestBrand",
        "mrp": 1000.0,
        "price": 1200.0,  # Price > MRP
        "quantity": -5  # Negative quantity
    }
    
    response = client.post("/api/v1/products", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_error_handling():
    """Test error handling"""
    # Test getting non-existent product
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404
    
    # Test updating non-existent product
    response = client.put("/api/v1/products/99999", json={"name": "Updated"})
    assert response.status_code == 404
    
    # Test deleting non-existent product
    response = client.delete("/api/v1/products/99999")
    assert response.status_code == 404

def test_duplicate_sku_error(setup_database, sample_product_data):
    """Test duplicate SKU handling"""
    # Create first product
    response = client.post("/api/v1/products", json=sample_product_data)
    assert response.status_code == 201
    
    # Try to create another product with same SKU
    response = client.post("/api/v1/products", json=sample_product_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

