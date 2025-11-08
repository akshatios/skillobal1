from core.database import layout_collection, courses_collection
from bson import ObjectId

async def get_top_courses():
    """Get top courses based on layout linked_courses"""
    try:
        # Get the specific layout document with ID 68d0d3643deb5b22c6613b61
        layout_id = "68d0d3643deb5b22c6613b61"
        layout_doc = await layout_collection.find_one({"_id": ObjectId(layout_id)})
        
        if not layout_doc:
            return {
                "message": "Layout document not found",
                "top_courses": [],
                "total": 0
            }
        
        # Get linked_courses from layout document
        linked_courses = layout_doc.get("linked_courses", [])
        
        if not linked_courses:
            return {
                "message": "No linked courses found in layout",
                "top_courses": [],
                "total": 0
            }
        
        # Convert string IDs to ObjectIds for query
        course_object_ids = []
        for course_id in linked_courses:
            try:
                course_object_ids.append(ObjectId(course_id))
            except:
                # Skip invalid ObjectId strings
                continue
        
        if not course_object_ids:
            return {
                "message": "No valid course IDs found in linked_courses",
                "top_courses": [],
                "total": 0
            }
        
        # Fetch matching courses from courses collection
        courses_docs = await courses_collection.find(
            {"_id": {"$in": course_object_ids}}
        ).to_list(length=1000)
        
        # Format course data
        top_courses = [
            {
                "id": str(doc.get("_id")),
                "title": doc.get("title"),
                "description": doc.get("description"),
                "course_image_url": doc.get("course_image_url") or doc.get("image_url"),
                "rating": doc.get("rating"),
                "price": doc.get("price"),
                "visible": doc.get("visible"),
                "instructor": doc.get("instructor"),
                "cat_id": str(doc.get("cat_id")) if doc.get("cat_id") else None,
            }
            for doc in courses_docs
        ]
        
        return {
            "message": "Top courses retrieved successfully",
            "layout_id": layout_id,
            "linked_courses_count": len(linked_courses),
            "matched_courses_count": len(top_courses),
            "top_courses": top_courses,
            "total": len(top_courses)
        }
        
    except Exception as e:
        return {
            "message": "Error retrieving top courses",
            "error": str(e),
            "top_courses": [],
            "total": 0
        }
