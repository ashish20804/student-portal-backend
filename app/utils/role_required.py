from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(required_role):
    """General decorator to check for any specific role."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            # Convert to string and lowercase to avoid case-sensitivity issues
            role = str(claims.get("role", "")).lower()

            if role != required_role.lower():
                return jsonify({"error": f"Unauthorized: {required_role} access required"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required(fn):
    """Specific decorator for Admin access that uses JWT claims."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 1. Ensure a valid JWT is present in the request
        verify_jwt_in_request()
        
        # 2. Get claims from the token (the data we set during login)
        claims = get_jwt()
        role = str(claims.get("role", "")).lower()

        # 3. Verify the role is 'admin'
        if role != "admin":
            return jsonify({"message": "Access Denied: Admin role required"}), 403

        return fn(*args, **kwargs)
    return wrapper