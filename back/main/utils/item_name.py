'''
return a user-friendly name for an item_id
'''
def item_name(item_id):
    names = {
        "strawberries_small": "Small box of strawberries",
        "strawberries_medium": "Medium box of strawberries"
    }
    return names.get(item_id, item_id)