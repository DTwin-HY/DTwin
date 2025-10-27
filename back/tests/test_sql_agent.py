import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
import sqlalchemy
from flask_migrate import Migrate

from back.src.extensions import db
from back.src.index import app
from back.src.models.models import Inventory, Product

from ..src.services.sql_agent import SqlStorageTool


@pytest.fixture
def test_app():
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
        }
    )

    if "sqlalchemy" not in app.extensions:
        db.init_app(app)
    Migrate(app, db)

    try:
        from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

        if not hasattr(SQLiteTypeCompiler, "visit_JSONB"):

            def _visit_JSONB(self, type_, **kw):
                return self.visit_JSON(type_, **kw)

            SQLiteTypeCompiler.visit_JSONB = _visit_JSONB
    except Exception:
        pass

    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture
def sql_storage_tool():
    return SqlStorageTool()


def test_check_inventory_not_found(test_app, sql_storage_tool):
    resp = sql_storage_tool.check_inventory("NON_EXISTENT")
    assert isinstance(resp, dict)
    assert resp.get("status") == "error"


def test_check_inventory_found(test_app, sql_storage_tool):
    p = Product(name="A100", price=0.0)
    db.session.add(p)
    db.session.commit()

    inv = Inventory(product_id=p.id, amount=10)
    db.session.add(inv)
    db.session.commit()

    resp = sql_storage_tool.check_inventory("A100")
    assert isinstance(resp, dict)
    assert resp.get("status") == "ok"
    assert resp.get("inventory_level") == 10


def test_list_inventory_with_and_without_stock(test_app, sql_storage_tool):
    from back.src.models.models import Inventory, Product

    p1 = Product(name="B200", price=0.0)
    db.session.add(p1)
    db.session.commit()
    inv1 = Inventory(product_id=p1.id, amount=5)
    db.session.add(inv1)

    p2 = Product(name="C300", price=0.0)
    db.session.add(p2)

    db.session.commit()

    resp = sql_storage_tool.list_inventory()
    assert isinstance(resp, dict)
    assert resp.get("status") == "ok"
    inventory = resp.get("inventory")
    assert isinstance(inventory, dict)
    assert inventory.get("B200") == 5
    assert inventory.get("C300") == 0


def test_low_stock_alert_returns_only_below_threshold(test_app, sql_storage_tool):
    from back.src.models.models import Inventory, Product

    p_low = Product(name="D400", price=0.0)
    db.session.add(p_low)
    db.session.commit()
    inv_low = Inventory(product_id=p_low.id, amount=2)
    db.session.add(inv_low)

    p_ok = Product(name="E500", price=0.0)
    db.session.add(p_ok)
    db.session.commit()
    inv_ok = Inventory(product_id=p_ok.id, amount=20)
    db.session.add(inv_ok)

    db.session.commit()

    resp = sql_storage_tool.low_stock_alert(10)
    assert isinstance(resp, dict)
    assert resp.get("status") == "ok"
    low = resp.get("low_stock")
    assert isinstance(low, dict)
    assert "D400" in low and low["D400"] == 2
    assert "E500" not in low
