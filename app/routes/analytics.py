from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Product
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/analytics/overview')
def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Get comprehensive analytics overview of the product catalog.
    """
    try:
        # Basic counts
        total_products = db.query(Product).count()
        active_products = db.query(Product).filter(Product.is_active == True).count()
        inactive_products = total_products - active_products
        
        # Price analytics
        price_stats = db.query(
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price'),
            func.avg(Product.price).label('avg_price'),
            func.sum(Product.quantity).label('total_inventory_value')
        ).filter(Product.is_active == True).first()
        
        # Inventory analytics
        inventory_stats = db.query(
            func.sum(Product.quantity).label('total_quantity'),
            func.count(Product.id).label('products_with_stock'),
            func.count(Product.id).label('out_of_stock_products')
        ).filter(Product.is_active == True).first()
        
        # Brand analytics
        brand_count = db.query(func.count(func.distinct(Product.brand))).filter(
            Product.is_active == True
        ).scalar()
        
        # Category analytics
        category_count = db.query(func.count(func.distinct(Product.category))).filter(
            and_(Product.is_active == True, Product.category.isnot(None))
        ).scalar()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_products = db.query(Product).filter(
            and_(Product.is_active == True, Product.created_at >= thirty_days_ago)
        ).count()
        
        return {
            "summary": {
                "total_products": total_products,
                "active_products": active_products,
                "inactive_products": inactive_products,
                "brand_count": brand_count,
                "category_count": category_count,
                "recent_products_30_days": recent_products
            },
            "price_analytics": {
                "min_price": price_stats.min_price,
                "max_price": price_stats.max_price,
                "avg_price": round(price_stats.avg_price, 2) if price_stats.avg_price else 0,
                "total_inventory_value": price_stats.total_inventory_value or 0
            },
            "inventory_analytics": {
                "total_quantity": inventory_stats.total_quantity or 0,
                "products_with_stock": inventory_stats.products_with_stock or 0,
                "out_of_stock_products": inventory_stats.out_of_stock_products or 0
            }
        }
    except Exception as e:
        logger.error(f"Error generating analytics overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics overview"
        )

@router.get('/analytics/brands')
def get_brand_analytics(
    limit: int = Query(10, ge=1, le=50, description="Number of brands to return"),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for brands.
    """
    try:
        brand_stats = db.query(
            Product.brand,
            func.count(Product.id).label('product_count'),
            func.avg(Product.price).label('avg_price'),
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price'),
            func.sum(Product.quantity).label('total_quantity')
        ).filter(Product.is_active == True).group_by(Product.brand).order_by(
            func.count(Product.id).desc()
        ).limit(limit).all()
        
        return {
            "brands": [
                {
                    "brand": stat.brand,
                    "product_count": stat.product_count,
                    "avg_price": round(stat.avg_price, 2),
                    "min_price": stat.min_price,
                    "max_price": stat.max_price,
                    "total_quantity": stat.total_quantity or 0
                }
                for stat in brand_stats
            ]
        }
    except Exception as e:
        logger.error(f"Error generating brand analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate brand analytics"
        )

@router.get('/analytics/categories')
def get_category_analytics(
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return"),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for categories.
    """
    try:
        category_stats = db.query(
            Product.category,
            func.count(Product.id).label('product_count'),
            func.avg(Product.price).label('avg_price'),
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price'),
            func.sum(Product.quantity).label('total_quantity')
        ).filter(
            and_(Product.is_active == True, Product.category.isnot(None))
        ).group_by(Product.category).order_by(
            func.count(Product.id).desc()
        ).limit(limit).all()
        
        return {
            "categories": [
                {
                    "category": stat.category,
                    "product_count": stat.product_count,
                    "avg_price": round(stat.avg_price, 2),
                    "min_price": stat.min_price,
                    "max_price": stat.max_price,
                    "total_quantity": stat.total_quantity or 0
                }
                for stat in category_stats
            ]
        }
    except Exception as e:
        logger.error(f"Error generating category analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate category analytics"
        )

@router.get('/analytics/price-distribution')
def get_price_distribution(
    bins: int = Query(10, ge=5, le=20, description="Number of price bins"),
    db: Session = Depends(get_db)
):
    """
    Get price distribution analysis.
    """
    try:
        # Get price range
        price_range = db.query(
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price')
        ).filter(Product.is_active == True).first()
        
        if not price_range or not price_range.min_price:
            return {"distribution": [], "price_range": {"min": 0, "max": 0}}
        
        min_price = price_range.min_price
        max_price = price_range.max_price
        bin_size = (max_price - min_price) / bins
        
        distribution = []
        for i in range(bins):
            bin_start = min_price + (i * bin_size)
            bin_end = min_price + ((i + 1) * bin_size)
            
            count = db.query(Product).filter(
                and_(
                    Product.is_active == True,
                    Product.price >= bin_start,
                    Product.price < bin_end if i < bins - 1 else Product.price <= bin_end
                )
            ).count()
            
            distribution.append({
                "bin": i + 1,
                "range": f"{bin_start:.2f} - {bin_end:.2f}",
                "count": count,
                "percentage": 0  # Will be calculated after getting total
            })
        
        # Calculate percentages
        total_active = db.query(Product).filter(Product.is_active == True).count()
        for item in distribution:
            item["percentage"] = round((item["count"] / total_active * 100), 2) if total_active > 0 else 0
        
        return {
            "distribution": distribution,
            "price_range": {
                "min": min_price,
                "max": max_price,
                "bin_size": round(bin_size, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error generating price distribution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate price distribution"
        )

@router.get('/analytics/trends')
def get_trends_analytics(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get trends analytics for the specified period.
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Products created in the period
        products_created = db.query(Product).filter(
            and_(Product.is_active == True, Product.created_at >= start_date)
        ).count()
        
        # Products updated in the period
        products_updated = db.query(Product).filter(
            and_(Product.is_active == True, Product.updated_at >= start_date)
        ).count()
        
        # Daily breakdown
        daily_stats = db.query(
            func.date(Product.created_at).label('date'),
            func.count(Product.id).label('count')
        ).filter(
            and_(Product.is_active == True, Product.created_at >= start_date)
        ).group_by(func.date(Product.created_at)).order_by('date').all()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "products_created": products_created,
                "products_updated": products_updated
            },
            "daily_breakdown": [
                {
                    "date": stat.date.isoformat(),
                    "products_created": stat.count
                }
                for stat in daily_stats
            ]
        }
    except Exception as e:
        logger.error(f"Error generating trends analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate trends analytics"
        )
