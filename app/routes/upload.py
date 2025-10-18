from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.csv_parser import parse_and_validate_csv
from ..models import Product
from ..schemas import UploadResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post('/upload', response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file containing product data"),
    db: Session = Depends(get_db)
):
    """
    Upload and process a CSV file containing product data.
    
    The CSV file should contain the following columns:
    - sku: Unique product identifier (required)
    - name: Product name (required)
    - brand: Product brand (required)
    - color: Product color (optional)
    - size: Product size (optional)
    - mrp: Maximum Retail Price (required)
    - price: Selling price (required)
    - quantity: Available quantity (optional, defaults to 0)
    - description: Product description (optional)
    - category: Product category (optional)
    - tags: Comma-separated tags (optional)
    
    Returns detailed information about successful uploads and any validation errors.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Check file size (limit to 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        contents = await file.read()
        valid_products, failed = parse_and_validate_csv(contents)
        
        stored = 0
        total_processed = len(valid_products) + len(failed)
        
        # Process valid products
        for p in valid_products:
            try:
                prod = Product(
                    sku=p.sku,
                    name=p.name,
                    brand=p.brand,
                    color=p.color,
                    size=p.size,
                    mrp=p.mrp,
                    price=p.price,
                    quantity=p.quantity,
                    description=getattr(p, 'description', None),
                    category=getattr(p, 'category', None),
                    tags=getattr(p, 'tags', None)
                )
                db.add(prod)
                db.commit()
                stored += 1
                logger.info(f"Successfully stored product: {p.sku}")
                
            except IntegrityError as e:
                db.rollback()
                failed.append({
                    "sku": p.sku, 
                    "reason": f"Duplicate SKU or database constraint violation: {str(e)}"
                })
                logger.warning(f"Failed to store product {p.sku}: {str(e)}")
        
        # Calculate success rate
        success_rate = (stored / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(f"Upload completed: {stored}/{total_processed} products stored successfully")
        
        return UploadResponse(
            stored=stored,
            failed=failed,
            total_processed=total_processed,
            success_rate=round(success_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )
