from rest_framework.exceptions import APIException

class BadRequest(APIException):
    status_code = 400
    default_detail = "Bad request"
    default_code = "bad_request"


class Unauthorized(APIException):
    status_code = 401
    default_detail = "Unauthorized access"
    default_code = "unauthorized"


class Forbidden(APIException):
    status_code = 403
    default_detail = "Forbidden access"
    default_code = "forbidden"


class NotFound(APIException):
    status_code = 404
    default_detail = "Resource not found"
    default_code = "not_found"
