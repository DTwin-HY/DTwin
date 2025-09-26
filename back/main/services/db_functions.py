from main.models.inventory import Inventory
from back.index import db


def update_inventory(quantity: int, item_id: int) -> Inventory:
  item = Inventory.get(Inventory, item_id)
  item.amount -= quantity

  db.session.commit()

  return item