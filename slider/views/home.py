from core.database import slider_collection

async def slider_home():
    """Get total sliders and all slider info"""
    # Fetch sliders from MongoDB
    docs = await slider_collection.find().to_list(length=10000)
    sliders = [
        {
            "id": str(doc.get("_id")),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "img_url": doc.get("img_url"),
            "cat_id": str(doc.get("cat_id")) if doc.get("cat_id") else None,
        }
        for doc in docs
    ]
    
    return {"total": len(sliders), "sliders": sliders}
