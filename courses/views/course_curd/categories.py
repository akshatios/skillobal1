from core.database import categories_collection

async def get_all_categories():
    """Get all categories with id and category_name"""
    docs = await categories_collection.find({}).to_list(length=10000)
    
    categories = [
        {
            "id": str(doc.get("_id")),
            "category_name": doc.get("name")
        }
        for doc in docs
    ]
    
    return {
        "total_categories": len(categories),
        "categories": categories
    }