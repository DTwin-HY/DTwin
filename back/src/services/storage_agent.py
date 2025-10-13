from typing import Annotated

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


class StorageAgent:
    def __init__(self, storage_tool):
        self.tool = storage_tool

    def handle_request(self, request):
        """Handle structured requests and route them to the correct tool method."""
        task = request.get("task")

        if task == "check_inventory":
            return self.tool.query_inventory(request["product_id"])

        elif task == "list_inventory":
            return self.tool.list_inventory()

        elif task == "low_stock_alert":
            return self.tool.low_stock_alert(request["threshold"])

        else:
            return {"status": "error", "message": f"Unknown task: {task}"}



class HardCodedStorageTool:
    def __init__(self):
        self.inventory = {"A100": 50, "B200": 20, "C300": 0}


    def query_inventory(self, product_id):
        """Return the stock level for a given product ID."""
        if product_id in self.inventory:
            return {"status": "ok", "inventory_level": self.inventory[product_id]}
        else:
            return {"status": "error", "message": "Product not found"}


    def list_inventory(self):
        """List all products and their inventory levels."""
        return {"status": "ok", "inventory": self.inventory}


    def low_stock_alert(self, threshold):
        """Return all products with stock below a given threshold."""
        low = {pid: qty for pid, qty in self.inventory.items() if qty < threshold}
        return {"status": "ok", "low_stock": low}
    



storage_tool = HardCodedStorageTool()
storage_agent = StorageAgent(storage_tool)


@tool
def check_inventory(
    product_id: Annotated[str, "The product ID to check (for example 'A100', 'B200', 'C300')"],
) -> dict:
    """Check the inventory for a specific product.

    Args:
      product_id (str)

    Returns:
      dict: A dictionary with keys "status", "inventory_level" and optionally "message" if a product is not found.
    """
    request = {"task": "check_inventory", "product_id": product_id}
    return storage_agent.handle_request(request)


@tool
def list_inventory() -> dict:
    """List all products and their inventory levels."""
    request = {"task": "list_inventory"}
    return storage_agent.handle_request(request)


@tool
def low_stock_alert(
    threshold: Annotated[int, "The minimum stock level to trigger an alert"],
) -> dict:
    """List products where stock is below a given threshold."""
    request = {"task": "low_stock_alert", "threshold": threshold}
    return storage_agent.handle_request(request)





storage_react_agent = create_react_agent(
    name="storage_agent",
    model="openai:gpt-5-nano",
    tools=[
        check_inventory,
        list_inventory,
        low_stock_alert,
    ],
    prompt=(
        "You are a warehouse management agent.\n\n"
        "You can check inventory, restock, add, remove, or list products.\n"
        "Respond strictly in JSON format for example ({product_id: amount}) with no extra text at all."
    ),
)


if __name__ == "__main__":
    result = storage_react_agent.invoke(
        {"messages": [HumanMessage(content="Check inventory for A100")]}
    )
    print(result["messages"][-1].content)
