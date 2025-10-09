class StorageAgent:
    def __init__(self, storage_tool):
        self.tool = storage_tool

    def handle_request(self, request):
        task = request.get("task")
        
        if task == "check_inventory":
            return self.tool.query_inventory(request["product_id"])
        
        elif task == "restock":
            return self.tool.order_stock(request["product_id"], request["amount"])
        
        else:
            return {"status": "error", "message": f"Unknown task: {task}"}
        

class HardCodedStorageTool:
    def __init__(self):
        self.inventory = {
            "A100": 50,
            "B200": 20,
            "C300": 0
        }

    def query_inventory(self, product_id):
        if product_id in self.inventory:
            return {"status": "ok", "inventory_level": self.inventory[product_id]}
        else:
            return {"status": "error", "message": "Product not found"}

    def order_stock(self, product_id, amount):
        if product_id in self.inventory:
            self.inventory[product_id] += amount
            return {"status": "ok", "new_inventory_level": self.inventory[product_id]}
        else:
            return {"status": "error", "message": "Product not found"}