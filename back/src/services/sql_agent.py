import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from ..graph.llm_utils import llm

from ..extensions import db as app_db
from ..models.models import Inventory, Product

load_dotenv()

# SQLDatabase and toolkit
sql_db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))
toolkit = SQLDatabaseToolkit(db=sql_db, llm=llm)
tools = toolkit.get_tools()


class SqlStorageTool:
    """Domain-specific inventory tools using SQLAlchemy ORM."""

    def _find_product_by_code(self, product_code: str):
        """Return the Product object matching the given code, or None if not found."""
        return Product.query.filter_by(name=product_code).first()

    def check_inventory(self, product_id: str) -> dict:
        """Return the stock level of a specific product by its code."""
        product = self._find_product_by_code(product_id)
        if not product:
            return {"status": "error", "message": "Product not found"}
        inv = Inventory.query.filter_by(product_id=product.id).first()
        amount = inv.amount if inv else 0
        return {"status": "ok", "inventory_level": amount}

    def list_inventory(self) -> dict:
        """Return a dictionary of all products and their stock levels."""
        results = {}
        for p in Product.query.all():
            inv = Inventory.query.filter_by(product_id=p.id).first()
            results[p.name] = inv.amount if inv else 0
        return {"status": "ok", "inventory": results}

    def low_stock_alert(self, threshold: int) -> dict:
        """Return products with stock below the given threshold."""
        low = {}
        items = (
            app_db.session.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.id)
            .filter(Inventory.amount < threshold)
            .all()
        )
        for inv, prod in items:
            low[prod.name] = inv.amount
        return {"status": "ok", "low_stock": low}


sql_storage_tool = SqlStorageTool()


@tool
def check_inventory(product_id: Annotated[str, "The product ID to check (e.g., 'A100')"]) -> dict:
    """
    Check the inventory for the inventory level of the given product.
    """
    return sql_storage_tool.check_inventory(product_id)


@tool
def list_inventory() -> dict:
    """
    List all items in the inventory.
    """
    return sql_storage_tool.list_inventory()


@tool
def low_stock_alert(threshold: Annotated[int, "Minimum stock level to trigger alert"]) -> dict:
    """
    List all products with levels below the threshold.
    """
    return sql_storage_tool.low_stock_alert(threshold)


# Add domain tools to toolkit tools
tools += [check_inventory, list_inventory, low_stock_alert]

sql_react_agent = create_react_agent(
    name="sql_storage_agent",
    model="openai:gpt-5-nano",
    tools=tools,
    prompt=(
        "You are a **warehouse inventory management agent**.\n\n"
        "You can use the following tools to get inventory data:\n"
        "- SQLDatabaseToolkit tools for general SQL queries\n"
        "- `check_inventory(product_id)` - Get stock level for a product\n"
        "- `list_inventory()` - List all products and quantities\n"
        "- `low_stock_alert(threshold)` - List products below a threshold\n\n"
        "**Response rules:**\n"
        "- Always respond strictly in JSON format\n"
        "- No markdown, no natural language text, no explanations\n"
        '- Example valid response: `{ "A100": 50 }`\n'
        '- If you cannot find data, respond with `{ "error": "reason here" }`.\n'
    ),
)

if __name__ == "__main__":
    result = sql_react_agent.invoke(
        {"messages": [HumanMessage(content="Check inventory for A100")]}
    )
    print("Agent response:", result["messages"][-1].content)
