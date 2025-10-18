
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

CSV_CONTENT = """
sku,name,brand,color,size,mrp,price,quantity
TSHIRT-RED-001,Classic Cotton T-Shirt,StreamThreads,Red,M,799,499,20
BAD-PRICE,Faulty Item,BrandX,Black,L,500,600,5
"""

def test_upload_and_response():
    files = {"file": ("products.csv", CSV_CONTENT, "text/csv")}
    resp = client.post('/api/v1/upload', files=files)
    assert resp.status_code == 201
    data = resp.json()
    assert data['stored'] >= 1
    assert any('BAD-PRICE' in str(f) or 'price cannot be greater than mrp' in str(f) for f in data['failed'])