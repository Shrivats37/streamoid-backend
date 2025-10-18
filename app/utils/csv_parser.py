
import csv
import io
from typing import List, Tuple, Dict
from ..schemas import ProductCreate

REQUIRED_FIELDS = ["sku", "name", "brand", "mrp", "price"]
OPTIONAL_FIELDS = ["color", "size", "quantity", "description", "category", "tags"]

def parse_and_validate_csv(file_bytes: bytes) -> Tuple[List[ProductCreate], List[Dict]]:
    """
    Parse CSV bytes and validate rows.
    Returns (valid_products, failed_rows)
    failed_rows: list of dicts with row and reason
    """
    text = file_bytes.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    
    # Validate CSV headers
    if not reader.fieldnames:
        return [], [{"row": 1, "reason": "Empty CSV file"}]
    
    # Normalize headers
    normalized_headers = {h.strip().lower(): h for h in reader.fieldnames}
    
    # Check for required headers
    missing_headers = []
    for field in REQUIRED_FIELDS:
        if field not in normalized_headers:
            missing_headers.append(field)
    
    if missing_headers:
        return [], [{"row": 1, "reason": f"Missing required headers: {missing_headers}"}]
    
    valid = []
    failed = []

    for idx, row in enumerate(reader, start=2):  # start=2 to account for header line
        # normalize keys
        row = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items()}
        
        # Map to normalized field names
        normalized_row = {}
        for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
            if field in normalized_headers:
                original_header = normalized_headers[field]
                normalized_row[field] = row.get(original_header, "")
        
        # Check required fields
        missing = [f for f in REQUIRED_FIELDS if not normalized_row.get(f)]
        if missing:
            failed.append({"row": idx, "sku": normalized_row.get('sku'), "reason": f"missing fields: {missing}"})
            continue
        
        # Convert numeric fields
        try:
            mrp = float(normalized_row.get('mrp'))
            price = float(normalized_row.get('price'))
        except ValueError:
            failed.append({"row": idx, "sku": normalized_row.get('sku'), "reason": "mrp/price must be numeric"})
            continue
        
        # Handle quantity
        quantity = 0
        if normalized_row.get('quantity') != "":
            try:
                quantity = int(float(normalized_row.get('quantity')))
            except ValueError:
                failed.append({"row": idx, "sku": normalized_row.get('sku'), "reason": "quantity must be integer"})
                continue
        
        # Validation rules
        if price > mrp:
            failed.append({"row": idx, "sku": normalized_row.get('sku'), "reason": "price cannot be greater than mrp"})
            continue
        
        if quantity < 0:
            failed.append({"row": idx, "sku": normalized_row.get('sku'), "reason": "quantity must be >= 0"})
            continue
        
        # Validate SKU format (basic validation)
        sku = normalized_row.get('sku')
        if len(sku) > 100:
            failed.append({"row": idx, "sku": sku, "reason": "SKU too long (max 100 characters)"})
            continue
        
        # Validate name length
        name = normalized_row.get('name')
        if len(name) > 255:
            failed.append({"row": idx, "sku": sku, "reason": "Product name too long (max 255 characters)"})
            continue
        
        # Create product object
        try:
            prod = ProductCreate(
                sku=sku,
                name=name,
                brand=normalized_row.get('brand'),
                color=normalized_row.get('color') or None,
                size=normalized_row.get('size') or None,
                mrp=mrp,
                price=price,
                quantity=quantity,
                description=normalized_row.get('description') or None,
                category=normalized_row.get('category') or None,
                tags=normalized_row.get('tags') or None,
            )
            valid.append(prod)
        except Exception as e:
            failed.append({"row": idx, "sku": sku, "reason": f"Validation error: {str(e)}"})

    return valid, failed
