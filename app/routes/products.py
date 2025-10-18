from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from ..database import get_db
from ..models import Product
from ..schemas import ProductOut, ProductCreate, ProductUpdate, ProductSearchResponse, ProductSummary
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/products', response_model=ProductSearchResponse)
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of products per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    active_only: bool = Query(True, description="Show only active products"),
    db: Session = Depends(get_db)
):
    """
    List products with pagination and sorting.
    
    Supports sorting by: id, name, brand, price, created_at, updated_at
    """
    # Validate sort field
    valid_sort_fields = ["id", "name", "brand", "price", "created_at", "updated_at"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Must be one of: {valid_sort_fields}"
        )
    
    # Build query
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    # Apply sorting
    sort_column = getattr(Product, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    return ProductSearchResponse(
        products=products,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get('/products/search', response_model=ProductSearchResponse)
def search_products(
    q: Optional[str] = Query(None, description="Search query for name, brand, or description"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    color: Optional[str] = Query(None, description="Filter by color"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_quantity: Optional[int] = Query(None, ge=0, description="Minimum quantity"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    active_only: bool = Query(True, description="Show only active products"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Number of products per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """
    Advanced product search with multiple filters and text search.
    """
    # Validate sort field
    valid_sort_fields = ["id", "name", "brand", "price", "created_at", "updated_at"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field. Must be one of: {valid_sort_fields}"
        )
    
    # Build query
    query = db.query(Product)
    
    # Apply filters
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    
    if color:
        query = query.filter(Product.color.ilike(f"%{color}%"))
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if min_quantity is not None:
        query = query.filter(Product.quantity >= min_quantity)
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(Product.tags.ilike(f"%{tag}%"))
    
    # Text search
    if q:
        search_filter = or_(
            Product.name.ilike(f"%{q}%"),
            Product.brand.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%"),
            Product.sku.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    sort_column = getattr(Product, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    return ProductSearchResponse(
        products=products,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get('/products/{product_id}', response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post('/products', response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    """
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    logger.info(f"Created new product: {db_product.sku}")
    return db_product

@router.put('/products/{product_id}', response_model=ProductOut)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    logger.info(f"Updated product: {db_product.sku}")
    return db_product

@router.delete('/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product (soft delete by setting is_active to False).
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_product.is_active = False
    db.commit()
    
    logger.info(f"Soft deleted product: {db_product.sku}")

@router.get('/products/summary/stats')
def get_product_stats(db: Session = Depends(get_db)):
    """
    Get product statistics and analytics.
    """
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Brand distribution
    brand_stats = db.query(
        Product.brand, 
        func.count(Product.id).label('count'),
        func.avg(Product.price).label('avg_price')
    ).filter(Product.is_active == True).group_by(Product.brand).all()
    
    # Price statistics
    price_stats = db.query(
        func.min(Product.price).label('min_price'),
        func.max(Product.price).label('max_price'),
        func.avg(Product.price).label('avg_price'),
        func.sum(Product.quantity).label('total_quantity')
    ).filter(Product.is_active == True).first()
    
    # Category distribution
    category_stats = db.query(
        Product.category,
        func.count(Product.id).label('count')
    ).filter(
        Product.is_active == True,
        Product.category.isnot(None)
    ).group_by(Product.category).all()
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": total_products - active_products,
        "brand_distribution": [
            {"brand": stat.brand, "count": stat.count, "avg_price": round(stat.avg_price, 2)}
            for stat in brand_stats
        ],
        "price_statistics": {
            "min_price": price_stats.min_price,
            "max_price": price_stats.max_price,
            "avg_price": round(price_stats.avg_price, 2),
            "total_quantity": price_stats.total_quantity
        },
        "category_distribution": [
            {"category": stat.category, "count": stat.count}
            for stat in category_stats
        ]
    }