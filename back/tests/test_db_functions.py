from datetime import datetime
from decimal import Decimal

import pytest
from back.index import app, db
from main.models.models import Counter, History, Inventory, Product, Sale

from main.services.db_functions import (
    add_product,
    get_product,
    update_product_price,
    add_inventory,
    get_inventory_item,
    update_inventory,
    add_sale,
    get_sales_for_day,
)


@pytest.fixture
def test_app():
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app, db
        db.drop_all()


@pytest.fixture
def sample_product_data():
    return {"name": "testproduct", "price": Decimal("0.99")}


@pytest.fixture
def created_product(test_app, sample_product_data):
    app, _ = test_app
    """Create a product"""
    with app.app_context():
        product = add_product(**sample_product_data)
        yield product


@pytest.fixture
def product_with_inventory(created_product, test_app):
    """Create a product and an inventory referencing it."""
    app, _ = test_app
    with app.app_context():
        product = created_product
        inventory = add_inventory(product_id=product.id, amount=2)
        yield product, inventory


@pytest.fixture
def created_sale(test_app, product_with_inventory):
    app, _ = test_app
    with app.app_context():
        product, inventory = product_with_inventory
        sale = add_sale(
            transaction_id="abc",
            item_id=inventory.id,
            quantity=1,
            amount=product.price,
            timestamp=datetime(2000, 1, 1),
        )

        yield sale


class TestProductFunctions:
    def test_add_product(self, test_app, sample_product_data):
        app, _ = test_app
        with app.app_context():
            # Do it with kwargs so that we can update the data later
            product = add_product(**sample_product_data)

            assert product.id is not None
            assert product.name == sample_product_data["name"]
            assert product.price == sample_product_data["price"]

            saved_product = Product.query.first()
            assert saved_product.name == sample_product_data["name"]

    def test_get_product(self, test_app, created_product):
        app, _ = test_app
        with app.app_context():
            retrieved_product = get_product(created_product.id)

            assert retrieved_product is not None
            assert retrieved_product.name == created_product.name
            assert retrieved_product.price == created_product.price

    def test_update_product_price(self, test_app, created_product):
        app, test_db = test_app
        with app.app_context():
            new_price = Decimal("1.99")

            # This works without float casting, but shows error with pylance
            updated_product = update_product_price(created_product.id, float(new_price))

            db_product = test_db.session.get(Product, created_product.id)

            assert created_product.id == updated_product.id
            assert created_product.price != new_price
            assert db_product.price == new_price

    def test_update_product_price_invalid_id_raises_value_error(self, test_app):
        app, _ = test_app
        with app.app_context():
            with pytest.raises(ValueError):
                update_product_price(2, 4.99)


class TestInventoryFunctions:
    def test_add_inventory(self, test_app, sample_product_data):
        app, _ = test_app
        with app.app_context():
            product = add_product(**sample_product_data)
            inventory = add_inventory(product_id=product.id, amount=1)

            saved_inventory = Inventory.query.first()
            assert saved_inventory is not None
            assert saved_inventory.product_id == product.id
            assert saved_inventory.id == inventory.id
            assert saved_inventory.amount == 1

    def test_get_inventory_item(self, test_app, product_with_inventory):
        app, _ = test_app
        with app.app_context():
            _, inventory = product_with_inventory

            retrieved_inventory = get_inventory_item(inventory.id)

            assert retrieved_inventory is not None
            assert retrieved_inventory.id == inventory.id
            assert retrieved_inventory.amount == 2

    def test_update_inventory(self, test_app, product_with_inventory):
        app, test_db = test_app
        with app.app_context():
            _, inventory = product_with_inventory

            new_amount = inventory.amount - 1
            updated_inventory = update_inventory(1, inventory.id)

            db_inventory = test_db.session.get(Inventory, inventory.id)

            assert updated_inventory.id == inventory.id
            assert db_inventory.amount == new_amount

    def test_update_inventory_invalid_id_raises_error(self, test_app):
        app, _ = test_app
        with app.app_context():
            with pytest.raises(ValueError):
                update_inventory(1, 1)

    def test_update_inventory_invalid_quantity_raises_error(
        self, test_app, product_with_inventory
    ):
        app, _ = test_app
        with app.app_context():
            _, inventory = product_with_inventory
            inventory_amount = inventory.amount

            with pytest.raises(ValueError):
                update_inventory(inventory_amount + 1, inventory.id)


class TestSaleFunctions:
    def test_add_sale(self, test_app, product_with_inventory):
        app, _ = test_app
        with app.app_context():
            product, inventory = product_with_inventory
            add_sale("abc", inventory.id, 1, product.price, datetime(2000, 1, 1))
            added_sale = Sale.query.first()

            assert added_sale is not None
            assert added_sale.amount == product.price
            assert int(added_sale.item_id) == inventory.id

    def test_get_sales_for_day(self, test_app, created_sale):
        app, _ = test_app
        with app.app_context():
            day = datetime(2000, 1, 1)
            sales_list = get_sales_for_day(day)

            retrieved_sale = sales_list[0]

            assert len(sales_list) == 1
            assert retrieved_sale.id == created_sale.id

    def test_get_sales_for_empty_day_returns_empty_list(self, test_app):
        app, _ = test_app
        with app.app_context():
            day = datetime(2000, 2, 2)
            sales_list = get_sales_for_day(day)

            assert len(sales_list) == 0
