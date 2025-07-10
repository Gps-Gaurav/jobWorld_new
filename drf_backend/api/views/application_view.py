from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ApplicationView(APIView):
    """
    Ye Application endpoint ka base view hai.
    Abhi basic GET response return karta hai.
    """

    def get(self, request):
        return Response({"message": "Application endpoint working"}, status=status.HTTP_200_OK)
