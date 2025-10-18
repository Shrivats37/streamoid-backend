from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from .database import Base

class Product(Base):
    __tablename__ = "products"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    color = Column(String(50), nullable=True, index=True)
    size = Column(String(20), nullable=True)
    mrp = Column(Float, nullable=False)
    price = Column(Float, nullable=False, index=True)
    quantity = Column(Integer, nullable=True, default=0)
    
    # Enhanced fields
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_brand_price', 'brand', 'price'),
        Index('idx_category_active', 'category', 'is_active'),
        Index('idx_price_range', 'price'),
        Index('idx_created_at', 'created_at'),
    )