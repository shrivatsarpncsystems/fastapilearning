from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Product
import database_models

app = FastAPI()



database_models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

@app.get("/")
def greet():
    return "welcome shri"


products = [
    Product(id=1, name="Laptop", price=1000, quantity=10, description="A high performance laptop"),
    Product(id=2, name="Mouse", price=10, quantity=100, description="A wireless mouse"),
    Product(id=3, name="Keyboard", price=50, quantity=50, description="A mechanical keyboard"),
    Product(id=4, name="Monitor", price=200, quantity=20, description="A 24 inch monitor"),
    Product(id=5, name="Headphones", price=100, quantity=80, description="A noise cancelling headphones"),
]



def init_db():
    db = SessionLocal()
    if db.query(database_models.Product).count() == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
    db.close()

init_db()

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return db_products

@app.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product is None:
        return {"message": "Product not found"}    
    return db_product


@app.post("/products")
def create_product(product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == product.id).first()
    if db_product is not None:
        return {"message": "Product already exists"}    
    new_product = database_models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product is None:
        return {"message": "Product not found"}    
    db_product.name = product.name
    db_product.price = product.price
    db_product.quantity = product.quantity
    db_product.description = product.description
    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product is None:
        return {"message": "Product not found"}    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}


