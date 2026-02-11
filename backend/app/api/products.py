from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.session import SessionLocal
from backend.app.models.product import Product
from backend.app.schemas.product import ProductCreate
from backend.app.schemas.product import ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(
        title=product.title,
        model=product.model,
        price=product.price
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return {
        "id": db_product.id,
        "title": db_product.title,
        "model": db_product.model,
        "price": db_product.price
    }

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "model": p.model,
            "price": p.price
        }
        for p in products
    ]

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


@router.patch("/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.title is not None:
        db_product.title = product.title
    if product.model is not None:
        db_product.model = product.model
    if product.price is not None:
        db_product.price = product.price

    db.commit()
    db.refresh(db_product)

    return {
        "id": db_product.id,
        "title": db_product.title,
        "model": db_product.model,
        "price": db_product.price
    }