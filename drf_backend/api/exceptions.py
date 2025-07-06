from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        response.data['status'] = 'error'
        response.data['detail'] = str(exc)
    return response