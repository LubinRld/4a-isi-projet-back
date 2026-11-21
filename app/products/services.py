from sqlmodel import Session, select, func
from app.menus.services import disableMenusContainingProduct
from app.models import Product

def getAllProducts(session: Session,limit: int = 20, offset: int = 0):
    getAllProductStatement = select(Product).limit(limit).offset(offset)
    products = session.exec(getAllProductStatement).all()
    getTotalProductStatement = select(func.count()).select_from(Product)
    total = session.exec(getTotalProductStatement).one()

    return{
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": products
    }

def createProduct(session: Session, name: str, price_cents: int, stock: int = 0):
    existing = session.exec(select(Product).where(Product.name == name)).first()
    if existing :
        raise ValueError("This product is already created")
    if price_cents <0:
        raise ValueError("Price cannot be negative")
    if stock <0:
        raise ValueError("Stock cannot be negative")
    
    newProduct = Product(name=name, price_cents=price_cents, stock=stock)
    session.add(newProduct)
    session.commit()
    session.refresh(newProduct)
    return newProduct

def patchProduct(session: Session, productId: int, name: str | None = None, price_cents: int | None = None, stock_change: int |None = None):
    if name is None and price_cents is None and stock_change is None:
        raise ValueError("No fields provided to update")
    product = session.get(Product, productId)
    if product is None:
        raise LookupError("Product not found")
    
    if product.is_deleted:
        raise ValueError("Cannot modify a deleted product")
    
    if name is not None:
        existing = session.exec(select(Product).where(Product.name == name)).first()
        if existing is not None:
            raise ValueError("This name is already taken")
        product.name = name

    if price_cents is not None:
        if price_cents < 0:
            raise ValueError("Price cannot be negative")
        product.price_cents = price_cents

    if stock_change is not None:
        if stock_change == 0:
            raise ValueError("Stock change cannot be null")
        if product.stock+stock_change <0:
            raise ValueError("Insufficient stock")
        product.stock += stock_change
        disableMenusContainingProduct(session, productId, product.stock)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product

def softDeleteProduct(session: Session, productId: int):
    product = session.get(Product, productId)
    if product is None or product.is_deleted == True:
        raise LookupError("Product not found")

    product.is_deleted = True
    disableMenusContainingProduct(session, productId)
    session.add(product)
    session.commit()

def restoreProduct(session: Session, productId: int):
    product = session.get(Product, productId)
    if product is None:
        raise LookupError("Product not found")
    if not product.is_deleted:
        raise ValueError("Product is not deleted")
    product.is_deleted = False
    session.add(product)
    session.commit()
    session.refresh(product)
    return product