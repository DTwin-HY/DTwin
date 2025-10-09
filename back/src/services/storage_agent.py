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