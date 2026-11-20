from sqlmodel import Session, select, delete, update
from app.models import Menu, MenuProduct, Product
from app.menus.schemas import MenuProductOut, MenuOut, MenuProductItem, CreateMenuRequest, UpdateMenuRequest

def _buildMenuOut(menu:Menu, products: list[MenuProductOut]):
    return MenuOut(
        id=menu.id,
        name=menu.name,
        price_cents=menu.price_cents,
        is_available=menu.is_available,
        starting_date=menu.starting_date,
        ending_date=menu.ending_date,
        products=products
    )

def _validateAndBuildProducts(session: Session, items: list[MenuProductItem]):
    productsIds = [item.product_id for item in items]
    if len(productsIds) != len(set(productsIds)):
        raise ValueError("Duplicate product_id in menu products")

    dbProducts = session.exec(
        select(Product).where((Product.id).in_(productsIds), Product.is_deleted == False)
        ).all()

    if len(dbProducts) != len(productsIds):
        raise ValueError("One or more products do not exist or are deleted")

    productNames = {p.id: p.name for p in dbProducts}
    return[
        MenuProductOut(
            product_id=item.product_id,
            name=productNames[item.product_id],
            quantity=item.quantity
        )
        for item in items
    ]

def _getMenuProducts(session: Session, menuId: int):
    rows = session.exec(
            select(Product.id, Product.name, MenuProduct.quantity)
            .join(Product, MenuProduct.product_id == Product.id)
            .where(MenuProduct.menu_id==menuId)
            ).all()

    return [
        MenuProductOut(product_id=product_id, name= product_name, quantity=quantity)
        for product_id, product_name, quantity in rows
    ]

def getAllMenus(session: Session):
    menus = session.exec(select(Menu)).all()
    if not menus: 
        return []

    menu_ids = [menu.id for menu in menus]
    products_menus = session.exec(
        select(MenuProduct.menu_id, Product.id, Product.name, MenuProduct.quantity)
        .join(Product, MenuProduct.product_id == Product.id)
        .where(MenuProduct.menu_id.in_(menu_ids))
        ).all()

    products_by_menu: dict[int, list[MenuProductOut]] = {}
    for menu_id, product_id, product_name, quantity in products_menus:
        products_by_menu.setdefault(menu_id, []).append(
            MenuProductOut(
                product_id=product_id,
                name=product_name,
                quantity=quantity
            )
        )

    return [_buildMenuOut(menu, products_by_menu.get(menu.id, [])) for menu in menus]

def createMenu(session: Session, payload: CreateMenuRequest):
    if payload.price_cents<=0:
        raise ValueError("Price cannot be negative")
    if payload.starting_date is not None and payload.ending_date is not None and payload.starting_date>payload.ending_date:
        raise ValueError("ending_date cannot be earlier than starting_date")

    menuProductOut = _validateAndBuildProducts(session, payload.products)

    newMenu = Menu(
        name=payload.name,
        price_cents=payload.price_cents,
        is_available=payload.is_available,
        starting_date=payload.starting_date,
        ending_date=payload.ending_date
    )

    session.add(newMenu)
    session.flush()

    for item in payload.products:
        session.add(MenuProduct(menu_id=newMenu.id, product_id=item.product_id, quantity=item.quantity))

    session.commit()
    session.refresh(newMenu)

    return _buildMenuOut(newMenu, menuProductOut)

def updateMenu(session: Session, menuId: int, payload: UpdateMenuRequest):
    menu = session.get(Menu, menuId)

    if menu is None or menu.is_deleted:
        raise LookupError("Menu not found")

    if payload.name is not None:
        menu.name = payload.name

    if payload.price_cents is not None:
        if payload.price_cents <=0:
            raise ValueError("Price_cent cannot be negative or null")
        menu.price_cents = payload.price_cents

    if payload.starting_date is not None:
        menu.starting_date = payload.starting_date

    if payload.ending_date is not None:
        menu.ending_date = payload.ending_date 

    if menu.ending_date is not None and menu.starting_date is not None and menu.ending_date < menu.starting_date:
        raise ValueError("ending_date cannot be earlier than starting_date")
    
    if payload.is_available is not None:
        menu.is_available = payload.is_available

    products: list[MenuProductOut] | None = None
    if payload.products is not None:
        products = _validateAndBuildProducts(session, payload.products
                                             )
    session.add(menu)
    session.flush()

    if products is not None:
        session.exec(delete(MenuProduct).where(MenuProduct.menu_id==menuId))
        for product in products:
            session.add(MenuProduct(menu_id=menuId, product_id=product.product_id, quantity=product.quantity))
            
    session.commit()
    session.refresh(menu)

    if products is None:
        products = _getMenuProducts(session, menuId)

    return _buildMenuOut(menu, products)

def softDeleteMenu(session: Session, menuId: int):
    menu = session.get(Menu, menuId)
    if menu is None or menu.is_deleted:
        raise LookupError("Menu not found")

    menu.is_deleted = True
    menu.is_available = False
    session.add(menu)
    session.commit()

def restoreMenu(session: Session, menuId: int):
    menu = session.get(Menu, menuId)
    if menu is None :
        raise LookupError("Menu not found")

    if not menu.is_deleted:
        raise ValueError("Menu is not deleted")

    deletedProduct = session.exec(
        select(Product.id)
        .join(MenuProduct, MenuProduct.product_id == Product.id)
        .where(MenuProduct.menu_id == menuId, Product.is_deleted == True)
    ).first()

    if deletedProduct is not None: 
        raise ValueError("Cannot restore menu because one or more of its products are deleted")

    menu.is_deleted = False
    session.add(menu)
    session.commit()
    session.refresh(menu)
    return _buildMenuOut(menu, _getMenuProducts(session, menuId))

def disableMenusContainingProduct(session: Session, productId:int, available_stock: int | None = None):
    conditions = [MenuProduct.product_id == productId]

    if available_stock is not None:
        conditions.append(MenuProduct.quantity > available_stock)

    menuIdsSubquery = select(MenuProduct.menu_id).where(*conditions)

    session.exec(update(Menu)
                 .where(Menu.id.in_(menuIdsSubquery), Menu.is_available==True)
                 .values(is_available=False)
            )