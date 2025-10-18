
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100, description="Unique product SKU")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    brand: str = Field(..., min_length=1, max_length=100, description="Product brand")
    color: Optional[str] = Field(None, max_length=50, description="Product color")
    size: Optional[str] = Field(None, max_length=20, description="Product size")
    mrp: float = Field(..., gt=0, description="Maximum Retail Price")
    price: float = Field(..., gt=0, description="Selling price")
    quantity: Optional[int] = Field(0, ge=0, description="Available quantity")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    
    @field_validator('price')
    @classmethod
    def price_must_be_less_than_mrp(cls, v, info):
        if 'mrp' in info.data and v > info.data['mrp']:
            raise ValueError('Price cannot be greater than MRP')
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=20)
    mrp: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class ProductOut(ProductCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProductSummary(BaseModel):
    id: int
    sku: str
    name: str
    brand: str
    price: float
    quantity: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class ProductSearchResponse(BaseModel):
    products: List[ProductOut]
    total: int
    page: int
    limit: int
    total_pages: int

class UploadResponse(BaseModel):
    stored: int
    failed: List[dict]
    total_processed: int
    success_rate: float

