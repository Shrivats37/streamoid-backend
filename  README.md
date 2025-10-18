
# File: README.md
# ----------------
# Streamoid Backend - Take Home Exercise

This project provides a small FastAPI service to upload, validate, store, list, and search product data.

## Run locally

1. Create virtualenv and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the app

```bash
uvicorn app.main:app --reload
```

3. Upload sample CSV

```bash
curl -X POST -F "file=@products.csv" http://localhost:8000/upload
```

4. List products

```bash
curl "http://localhost:8000/products?page=1&limit=10"
```

5. Search products

```bash
curl "http://localhost:8000/products/search?brand=StreamThreads&minPrice=400&maxPrice=1000"
```

## Tests

```bash
pytest -q
```


# End of scaffold