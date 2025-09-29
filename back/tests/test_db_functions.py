from decimal import Decimal

import pytest
from back.index import app, db
from main.models.models import Log, User, Counter, History, Inventory, Product, Sale

from main.services.db_functions import (
    add_product,
    get_product,
    add_inventory,
    get_inventory_item,
    update_inventory
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
        yield app
        db.drop_all()


@pytest.fixture
def sample_product_data(test_app):
    return {"name": "testproduct", "price": Decimal("0.99")}


class TestProductFunctions:
    def test_add_product(self, test_app, sample_product_data):
        with test_app.app_context():
            #Do it with kwargs so that we can update the data later
            product = add_product(**sample_product_data)

            assert product.id is not None
            assert product.name == sample_product_data["name"]
            assert product.price == sample_product_data["price"]

            saved_product = Product.query.first()
            assert saved_product.name == sample_product_data["name"]

    def test_get_product(self, test_app, sample_product_data):
        with test_app.app_context():
            created_product = add_product(**sample_product_data)
            
            retrieved_product = get_product(created_product.id)

            assert retrieved_product.id is not None
            assert retrieved_product.name == created_product.name
            assert retrieved_product.price == created_product.price


class TestInventoryFunctions:
    def test_add_inventory(self, test_app, sample_product_data):
        with test_app.app_context():
            product = add_product(**sample_product_data)
            inventory = add_inventory(product_id=product.id, amount=1)

            saved_inventory = Inventory.query.first()
            assert saved_inventory is not None
            assert saved_inventory.product_id == product.id
            assert saved_inventory.amount == 1

    def test_get_inventory_item(self, test_app, sample_product_data):
        with test_app.app_context():
            product = add_product(**sample_product_data)
            inventory = add_inventory(product_id=product.id, amount=1)

            retrieved_inventory = get_inventory_item(inventory.id)
            assert retrieved_inventory.id == inventory.id
            assert retrieved_inventory.amount == 1
    
    def test_update_inventory(self, test_app, sample_product_data):
        with test_app.app_context():
            product = add_product(**sample_product_data)
            inventory = add_inventory(product_id=product.id, amount=2)

            updated_inventory = update_inventory(1, inventory.id)

            assert updated_inventory.id == inventory.id
            assert inventory.amount == 1