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

        elif task == "restock":
            return self.tool.order_stock(request["product_id"], request["amount"])

        elif task == "list_inventory":
            return self.tool.list_inventory()

        elif task == "low_stock_alert":
            return self.tool.low_stock_alert(request["threshold"])

        elif task == "add_product":
            return self.tool.add_product(request["product_id"], request["initial_stock"])

        elif task == "remove_product":
            return self.tool.remove_product(request["product_id"])

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


    def order_stock(self, product_id, amount):
        """Increase stock of an existing product by the given amount."""
        if product_id in self.inventory:
            self.inventory[product_id] += amount
            return {"status": "ok", "new_inventory_level": self.inventory[product_id]}
        else:
            return {"status": "error", "message": "Product not found"}


    def list_inventory(self):
        """List all products and their inventory levels."""
        return {"status": "ok", "inventory": self.inventory}


    def low_stock_alert(self, threshold):
        """Return all products with stock below a given threshold."""
        low = {pid: qty for pid, qty in self.inventory.items() if qty < threshold}
        return {"status": "ok", "low_stock": low}

    def add_product(self, product_id, initial_stock):
        """Add a new product to inventory."""
        if product_id in self.inventory:
            return {"status": "error", "message": "Product already exists"}
        self.inventory[product_id] = initial_stock
        return {"status": "ok", "message": f"Added {product_id} with {initial_stock} units"}
    

    def remove_product(self, product_id):
        """Remove a product from inventory."""
        if product_id not in self.inventory:
            return {"status": "error", "message": "Product not found"}
        del self.inventory[product_id]
        return {"status": "ok", "message": f"Removed {product_id}"}


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
def restock_product(
    product_id: Annotated[str, "The product ID to restock"],
    amount: Annotated[int, "The quantity to add to inventory"],
) -> dict:
    """Restock a product by adding the specified amount to its inventory."""
    request = {"task": "restock", "product_id": product_id, "amount": amount}
    return storage_agent.handle_request(request)


storage_react_agent = create_react_agent(
    name="storage_agent",
    model="openai:gpt-5-nano",
    tools=[check_inventory, restock_product],
    prompt=(
        "You are a storage checker agent.\n\n"
        "Instructions:\n"
        "- Your tasks are to either check inventory or to restock products.\n"
        "- Respond only with the results of your work in json format (e.g. {product_id: amount}), do not include any other text."
    ),
)


if __name__ == "__main__":
    result = storage_react_agent.invoke(
        {"messages": [HumanMessage(content="Check inventory for A100")]}
    )
    print(result["messages"][-1].content)
