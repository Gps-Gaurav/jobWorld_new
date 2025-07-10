from rest_framework.response import Response

def success_response(message="", data=None, status_code=200):
    """
    Success response with optional message and data
    """
    return Response({
        "success": True,
        "message": message,
        "data": data or {}
    }, status=status_code)


def error_response(message="", errors=None, status_code=400):
    """
    Error response with optional message and error details
    """
    return Response({
        "success": False,
        "message": message,
        "errors": errors or {}
    }, status=status_code)
