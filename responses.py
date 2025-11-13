from flask import jsonify

# GET/PATCH/PUT/DELETE
def success_response(message: str, data=None):
    """Generate a standardized success response. GET PUT/PATCH/DELETE
    """
    return jsonify({            
        "success": True,
        "message": message,
        "data": data    
    }), 200


def not_found_response(entity: str):
    """Generate a standardized not found response.
    """
    return jsonify({
        "success": False,
        "message": f"{entity} not found"
    }), 404  




