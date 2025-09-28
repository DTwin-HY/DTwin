from back.index import db
from datetime import datetime
from back.index import db
from main.models.models import Counter, Sale, History, Product, Inventory


def get_inventory_item(item_id: int) -> Inventory | None:
    """fetch a single inventory item by id"""

    return db.session.get(Inventory, item_id)


def update_inventory(quantity: int, item_id: int) -> Inventory:
    """decrease inventory quantity for an item. raise error if insufficient stock"""

    item = db.session.get(Inventory, item_id)
    if not item:
        raise ValueError(f"Inventory item {item_id} not found")

    if item.amount - quantity < 0:
        raise ValueError(f"Not enough stock for item {item_id}")

    item.amount -= quantity
    db.session.commit()
    return item


def add_inventory(product_id: int, amount: int) -> Inventory:
    """add a new inventory record for a product"""

    item = Inventory(product_id=product_id, amount=amount)
    db.session.add(item)
    db.session.commit()
    return item


def get_product(product_id: int) -> Product | None:
    """fetch a product by id"""

    return db.session.get(Product, product_id)


def add_product(name: str, price: float) -> Product:
    """add a new product with name and price"""

    product = Product(name=name, price=price)
    db.session.add(product)
    db.session.commit()
    return product


def update_product_price(product_id: int, new_price: float) -> Product:
    """update the price of an existing product"""

    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")
    product.price = new_price
    db.session.commit()
    return product


def add_sale(transaction_id: str, item_id: int, quantity: int, amount: float, timestamp: datetime | None = None) -> Sale:
    """create a new sale record"""

    sale = Sale(
        transaction_id=transaction_id,
        item_id=item_id,
        quantity=quantity,
        amount=amount,
        timestamp=timestamp or datetime.now()
    )
    db.session.add(sale)
    db.session.commit()
    return sale


def get_sales_for_day(day: datetime) -> list[Sale]:
    """fetch all sales for a specific day"""

    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return Sale.query.filter(Sale.timestamp >= start, Sale.timestamp <= end).all()


def add_history_event(product_id: int, event_type: str, amount: int, time: datetime | None = None) -> History:
    """add a history event (stock change or sale)"""

    history = History(
        time=time or datetime.now(),
        product_id=product_id,
        event_type=event_type,
        amount=amount
    )
    db.session.add(history)
    db.session.commit()
    return history


def get_counter() -> Counter:
    """fetch the counter record, creating it if it doesnt exist"""

    counter = Counter.query.first()
    if not counter:
        counter = Counter(balance=0)
        db.session.add(counter)
        db.session.commit()
    return counter


def update_counter_balance(change: float) -> Counter:
    """update counter balance. prevent negative balance"""

    counter = get_counter()
    new_balance = counter.balance + change
    if new_balance < 0:
        raise ValueError("Counter balance cannot be negative")
    counter.balance = new_balance
    db.session.commit()
    return counter
