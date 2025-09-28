import pytest
from back.index import app, db
from main.models.models import Log, User, Counter, History, Inventory, Product, Sale

from main.services.db_functions import (
    add_product,
    get_product,
    add_inventory,
    get_inventory_item,
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
def sample_product(test_app):
    with test_app.app_context():
        product = Product(name="testproduct", price=0.99)
        return product


class TestProductFunctions:
    def test_add_product(self, test_app):
        with test_app.app_context():
            product = add_product(name="testproduct", price=0.99)

            retrieved_product = Product.query.first()
            assert retrieved_product.name == "testproduct"

    def test_get_product(self, test_app, sample_product):
        with test_app.app_context():
            product = add_product(sample_product.name, sample_product.price)

            retrieved_product = get_product(product.id)

            assert retrieved_product.id == product.id


class TestInventoryFunctions:
    def test_add_inventory(self, test_app, sample_product):
        with test_app.app_context():
            product = add_product(sample_product.name, sample_product.price)
            inventory = add_inventory(product_id=product.id, amount=1)

            saved_inventory = Inventory.query.first()
            assert saved_inventory is not None

    def test_get_inventory_item(self, test_app, sample_product):
        with test_app.app_context():
            product = add_product(sample_product.name, sample_product.price)
            inventory = add_inventory(product_id=product.id, amount=1)

            retrieved_inventory = get_inventory_item(inventory.id)

            assert retrieved_inventory.id == inventory.id