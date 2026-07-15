from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Toko Online ORM API")

# SOAL 1: CRUD PRODUCTS

@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):

    db_product = models.Product(
        nama_produk=product.nama_produk,
        kategori=product.kategori,
        harga=product.harga
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=list[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return product

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    product.nama_produk = product_data.nama_produk
    product.kategori = product_data.kategori
    product.harga = product_data.harga
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    
    db.delete(product)
    db.commit()
    return {"pesan": f"Produk dengan ID {product_id} berhasil dihapus"}

# SOAL 2: ENDPOINT TOTAL BELANJA CUSTOMER
@app.get("/reports/customer-total", response_model=list[schemas.CustomerTotalReport])
def get_customer_total(db: Session = Depends(get_db)):
    results = db.query(
        models.Customer.nama,
        func.sum(models.Order.jumlah * models.Product.harga).label("total_belanja")
    ).join(models.Order, models.Customer.id == models.Order.customer_id) \
     .join(models.Product, models.Order.product_id == models.Product.id) \
     .group_by(models.Customer.id, models.Customer.nama) \
     .order_by(func.sum(models.Order.jumlah * models.Product.harga).desc()) \
     .all()
    
    return results


# SOAL 3: ENDPOINT CUSTOMER DI ATAS RATA-RATA
@app.get("/reports/customer-above-average", response_model=list[schemas.CustomerTotalReport])
def get_customer_above_average(db: Session = Depends(get_db)):

    subq_total = db.query(
        models.Order.customer_id,
        func.sum(models.Order.jumlah * models.Product.harga).label("total")
    ).join(models.Product, models.Order.product_id == models.Product.id) \
     .group_by(models.Order.customer_id).subquery()

    subq_avg = db.query(func.avg(subq_total.c.total)).scalar_subquery()

    results = db.query(
        models.Customer.nama,
        func.sum(models.Order.jumlah * models.Product.harga).label("total_belanja")
    ).join(models.Order, models.Customer.id == models.Order.customer_id) \
     .join(models.Product, models.Order.product_id == models.Product.id) \
     .group_by(models.Customer.id, models.Customer.nama) \
     .having(func.sum(models.Order.jumlah * models.Product.harga) > subq_avg) \
     .all()

    return results


# SOAL 4: ENDPOINT PRODUK TERLARIS PER KATEGORI
@app.get("/reports/top-product-by-category", response_model=list[schemas.TopProductReport])
def get_top_product_by_category(db: Session = Depends(get_db)):
    
    cte_sales = db.query(
        models.Product.kategori,
        models.Product.nama_produk,
        func.sum(models.Order.jumlah).label("total_terjual")
    ).join(models.Order, models.Product.id == models.Order.product_id) \
     .group_by(models.Product.id, models.Product.kategori, models.Product.nama_produk) \
     .cte("product_sales")

    subq_max = db.query(
        cte_sales.c.kategori,
        func.max(cte_sales.c.total_terjual).label("max_terjual")
    ).group_by(cte_sales.c.kategori).subquery()

    results = db.query(
        cte_sales.c.kategori,
        cte_sales.c.nama_produk,
        cte_sales.c.total_terjual
    ).join(subq_max, (cte_sales.c.kategori == subq_max.c.kategori) & 
                     (cte_sales.c.total_terjual == subq_max.c.max_terjual)) \
     .all()

    return results


# SOAL 5: ENDPOINT KLASIFIKASI CUSTOMER
@app.get("/reports/customer-level", response_model=list[schemas.CustomerLevelReport])
def get_customer_level(db: Session = Depends(get_db)):
    
    cte_total = db.query(
        models.Customer.nama,
        func.sum(models.Order.jumlah * models.Product.harga).label("total_belanja")
    ).join(models.Order, models.Customer.id == models.Order.customer_id) \
     .join(models.Product, models.Order.product_id == models.Product.id) \
     .group_by(models.Customer.id, models.Customer.nama) \
     .cte("customer_totals")

    level_case = case(
        (cte_total.c.total_belanja > 5000000, "VIP"),
        (cte_total.c.total_belanja >= 1000000, "Regular"),
        else_="Basic"
    ).label("level_customer")

    results = db.query(
        cte_total.c.nama,
        cte_total.c.total_belanja,
        level_case
    ).all()

    return results