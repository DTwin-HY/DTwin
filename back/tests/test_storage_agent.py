import pytest

from ..src.services.storage_agent import HardCodedStorageTool


@pytest.fixture
def storage_tool():
    return HardCodedStorageTool()


class TestStorageTool:
    def test_storage_tool_checks_inventory(self, storage_tool):
        product_id = "A100"
        query_result = storage_tool.check_inventory(product_id)

        assert query_result["inventory_level"] == 50
        assert query_result["status"] == "ok"

    def test_storage_tool_check_returns_error(self, storage_tool):
        product_id = "X100"
        query_result = storage_tool.check_inventory(product_id)

        assert query_result["message"] == "Product not found"
        assert query_result["status"] == "error"

    def test_storage_tool_lists_inventory(self, storage_tool):
        query_result = storage_tool.list_inventory()

        assert len(query_result["inventory"]) == 3

    def test_low_stock_alert(self, storage_tool):
        query_result = storage_tool.low_stock_alert(30)

        assert len(query_result["low_stock"]) == 2
