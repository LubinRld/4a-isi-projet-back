from sqlmodel import Session, select, func
from app.models import Order, User, Product, OrderProduct, Menu, MenuProduct, OrderMenu, ClosedDay
from app.orders.schemas import ProductOrderOut, MenuOrderOut, MenuProductOut, OrderOutDetail, UserOrderOut, OrderOut, CreateOrderRequest, OrderStatus
from app.shared.schemas import PaginatedResponse
from app.users.schemas import UserStatus
from app.menus.services import disableMenusContainingProduct
from datetime import datetime

def getOrderById(session: Session, orderId: int):
    order = session.get(Order, orderId)
    if order is None:
        raise LookupError("Order not found")
    user = session.get(User, order.user_id)
    if user is None:
        raise LookupError("User not found")

    totalPriceCents = 0

    #On récupère les produits de la commande
    productRows = session.exec(select(Product.id, Product.name, Product.price_cents, OrderProduct.quantity)
                           .join(Product, OrderProduct.product_id == Product.id)
                           .where(OrderProduct.order_id == orderId)
                           ).all()

    #on construit les produits et on les ajoute au total
    productsOut: list[ProductOrderOut] = []
    for product_id, name, price_cents, quantity in productRows:
        totalPriceCents+=price_cents*quantity
        productsOut.append(
            ProductOrderOut(
            id=product_id,
            name=name,
            quantity=quantity
        )
    )

    #On récupère les menus de la commande
    menuRows = session.exec(select(Menu.id, Menu.name, Menu.price_cents, OrderMenu.quantity)
                         .join(Menu, OrderMenu.menu_id==Menu.id)
                         .where(OrderMenu.order_id == orderId)
                        ).all()

    
    menusOut: list[MenuOrderOut] = []
    if menuRows:
        menuIds = [menu_id for menu_id, _, _, _ in menuRows]

        menuProductRows = session.exec(select(MenuProduct.menu_id, Product.id, Product.name, MenuProduct.quantity)
                                       .join(Product, MenuProduct.product_id==Product.id)
                                       .where(MenuProduct.menu_id.in_(menuIds))
                                        ).all()
        
        productsByMenu: dict[int, list[MenuProductOut]] = {}
        for menuId, productId, productName, qty in menuProductRows:
            productsByMenu.setdefault(menuId, []).append(
                MenuProductOut(
                    product_id=productId,
                    name= productName,
                    quantity=qty
                )
            )

        for menuId, name, price_cents, quantity in menuRows:
            totalPriceCents+=price_cents*quantity
            menusOut.append(
                MenuOrderOut(
                    id=menuId,
                    name=name,
                    quantity=quantity,
                    products=productsByMenu.get(menuId, [])
                )
            )    

    return OrderOutDetail(
        id=order.id,
        retrieval_date=order.retrieval_date,
        created_at=order.created_at,
        status=order.status,
        total_price_cents=totalPriceCents,
        user=UserOrderOut(id=user.id, name=user.name),
        products=productsOut,
        menus=menusOut
    )

def getAllOrders(session:Session, limit:int =20, offset:int = 0):
    orderRows = session.exec(select(Order, User)
                             .join(User, Order.user_id == User.id)
                             .limit(limit)
                             .offset(offset)
                             ).all()
    
    total = session.exec(select(func.count()).select_from(Order)).one()
    ordersOut = [
        OrderOut(
            id = order.id,
            retrieval_date=order.retrieval_date,
            created_at=order.created_at,
            status = order.status,
            user = UserOrderOut(id=user.id, name=user.name)
        ) 
        for order, user in orderRows
    ]

    return PaginatedResponse[OrderOut](
        total=total,
        limit=limit,
        offset=offset,
        data=ordersOut
    )

def createOrder(session: Session, payload: CreateOrderRequest):

    user = session.get(User, payload.user_id)
    if user is None:
        raise LookupError("User not found")
    if user.status != UserStatus.ACTIVE:
        raise ValueError("User account is blocked")

    retrievalDate = payload.retrieval_date.replace(tzinfo=None)
    if retrievalDate < datetime.now():
        raise ValueError("Retrieval date cannot be earlier than now")

    closedDay = session.exec(select(ClosedDay).where(ClosedDay.day == retrievalDate.date())).first()
    if closedDay is not None:
        raise ValueError("Cafeteria is closed on this date")

    productIds = [item.product_id for item in payload.products]
    if len(productIds) != len(set(productIds)):
        raise ValueError("Duplicate product_id in order")

    menuIds = [item.menu_id for item in payload.menus]
    if len(menuIds) != len(set(menuIds)):
        raise ValueError("Duplicate menu_id in order") 

    #requiredStock contient tous les produits de la commande
    requiredStock: dict[int, int] = {}
    #on ajoute les produits seuls
    for item in payload.products:
        requiredStock[item.product_id] = requiredStock.get(item.product_id, 0)+item.quantity
    #puis les produits venant des menus
    if menuIds:
        menus = session.exec(select(Menu).where(Menu.id.in_(menuIds))).all()
        if len(menus) != len(menuIds):
            raise LookupError("One or more menus were not found")

        for menu in menus:
            if menu.is_deleted:
                raise ValueError(f"Menu '{menu.name}' is deleted")
            if not menu.is_available:
                raise ValueError(f"Menu '{menu.name}' is currently unavailable")
            if menu.starting_date and retrievalDate < menu.starting_date:
                raise ValueError(f"Menu '{menu.name}' is not available yet for this retrieval date")
            if menu.ending_date and retrievalDate>menu.ending_date:
                raise ValueError(f"Menu '{menu.name}' is no longer available for this retrieval date")

        menuQuantities = {item.menu_id: item.quantity for item in payload.menus}
        menuProducts = session.exec(select(MenuProduct)
                                    .where(MenuProduct.menu_id.in_(menuIds))
                                    ).all()
        for menuProduct in menuProducts:
            totalQuantityForMenu = menuProduct.quantity * menuQuantities[menuProduct.menu_id]
            requiredStock[menuProduct.product_id] = requiredStock.get(menuProduct.product_id,0)+ totalQuantityForMenu

    #je met tous les produits dont j'ai besoin pour ma commande dans mon dictionnaire
    productsByIds: dict[int, Product] = {}
    if requiredStock:
        products = session.exec(select(Product)
                                .where(Product.id.in_(requiredStock.keys()))
                                ).all()
        if len(products) != len(requiredStock):
            raise LookupError("One or more products were not found")

        for product in products:
            if product.is_deleted:
                raise ValueError(f"Product '{product.name}' is deleted")
            if product.stock < requiredStock[product.id]:
                raise ValueError(f"Insufficient stock for product '{product.name}'")
            productsByIds[product.id]=product

    newOrder = Order(
        user_id=payload.user_id,
        retrieval_date=retrievalDate
    )

    session.add(newOrder)
    session.flush()

    for item in payload.products:
        session.add(
            OrderProduct(
                order_id=newOrder.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
        )

    for item in payload.menus:
        session.add(
            OrderMenu(
                order_id=newOrder.id,
                menu_id=item.menu_id,
                quantity=item.quantity
            )
        )

    #Pour chaque produit, j'enlève ce dont j'ai eu besoin pour la commande
    for product_id, quantityUsed in requiredStock.items():
        product = productsByIds[product_id]
        product.stock -= quantityUsed
        session.add(product)
        disableMenusContainingProduct(session, product_id, product.stock)

    session.commit()
    return getOrderById(session, newOrder.id)

ALLOWED_STATUS_TRAINSITION: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.READY, OrderStatus.DONE, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.DONE, OrderStatus.CANCELLED},
    OrderStatus.DONE: set(),
    OrderStatus.CANCELLED: set()
}

def updateOrderStatus(session: Session, orderId:int, status: OrderStatus):
    order = session.get(Order, orderId)
    if order is None:
        raise LookupError("Order not found")

    currentStatus = OrderStatus(order.status)

    if currentStatus == status:
        raise ValueError(f"Order is already '{status.value}'")

    if status not in ALLOWED_STATUS_TRAINSITION[currentStatus]:
        raise ValueError(f"Cannot transition order status from '{currentStatus.value}' to '{status.value}'")

    if status == OrderStatus.CANCELLED:
        stockToRestore: dict[int, int] = {}

        orderProducts = session.exec(select(OrderProduct)
                                     .where(OrderProduct.order_id == orderId)
                                     ).all()
        for orderProduct in orderProducts:
            stockToRestore[orderProduct.product_id] = stockToRestore.get(orderProduct.product_id, 0) + orderProduct.quantity

        orderMenus = session.exec(select(OrderMenu)
                                  .where(OrderMenu.order_id == orderId)
                                  ).all()
        if orderMenus:
            menuQuantities = {ordermenu.menu_id: ordermenu.quantity for ordermenu in orderMenus}
            menuProducts = session.exec(select(MenuProduct)
                                        .where(MenuProduct.menu_id.in_(menuQuantities.keys()))
                                        ).all()
            for menuProduct in menuProducts:
                totalQuantity = menuProduct.quantity * menuQuantities[menuProduct.menu_id]
                stockToRestore[menuProduct.product_id]= stockToRestore.get(menuProduct.product_id, 0) + totalQuantity

        if stockToRestore:
            products = session.exec(
                select(Product)
                .where(Product.id.in_(stockToRestore.keys()))
            ).all()
            for product in products:
                product.stock += stockToRestore[product.id]
                session.add(product)

    order.status = status.value
    session.add(order)
    session.commit()

    return getOrderById(session, orderId)