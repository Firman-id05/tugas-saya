from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    nama_produk: str
    kategori: str
    harga: int = Field(gt=0, description="Harga harus lebih dari 0")

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    model_config = {"from_attributes": True}
    

# Schemas untuk SOAL 2 - 5

class CustomerTotalReport(BaseModel):
    nama: str
    total_belanja: int

class TopProductReport(BaseModel):
    kategori: str
    nama_produk: str
    total_terjual: int

class CustomerLevelReport(BaseModel):
    nama: str
    total_belanja: int
    level_customer: str