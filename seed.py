import models
from database import engine, SessionLocal

db = SessionLocal()

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db.query(models.Order).delete()
    db.query(models.Customer).delete()
    db.query(models.Product).delete()
    
    c1 = models.Customer(nama="Tifa", email="Tifa@mail.com")
    c2 = models.Customer(nama="Fira", email="Fira@mail.com")
    c3 = models.Customer(nama="Fatir", email="Fatir@mail.com")
    db.add_all([c1, c2, c3])
    db.commit()

    p1 = models.Product(nama_produk="Hp iphone 17 pro max", kategori="Elektronik", harga=25000000)
    p2 = models.Product(nama_produk="Laptop asus thinkpad", kategori="Elektronik", harga=3000000)
    p3 = models.Product(nama_produk="Baju batik ", kategori="Fashion", harga=250000)
    p4 = models.Product(nama_produk="Sepatu adidas samba", kategori="Fashion", harga=600000)
    db.add_all([p1, p2, p3, p4])
    db.commit()

    # Tifa beli hp iphone 17 pro max (Total: 25.000.000) -> kategori VIP
    o1 = models.Order(customer_id=c1.id, product_id=p1.id, jumlah=1)
    
    # Fira beli 2 batik & 1 Sepatu & 1 laptop (Total: 4.100.000) -> Regular
    o2 = models.Order(customer_id=c2.id, product_id=p3.id, jumlah=2)
    o3 = models.Order(customer_id=c2.id, product_id=p4.id, jumlah=1)
    o4 = models.Order(customer_id=c2.id, product_id=p2.id, jumlah=1)
    # Fatir beli baju batik (Total: 250.000) -> kategori Basic
    o5 = models.Order(customer_id=c3.id, product_id=p3.id, jumlah=1)
    
    db.add_all([o1, o2, o3, o4, o5])
    db.commit()

    print("Data berhasil dimasukkan ke database!")

if __name__ == "__main__":
    print("Menyuntikkan data ke database...")
    seed_data()
    db.close()