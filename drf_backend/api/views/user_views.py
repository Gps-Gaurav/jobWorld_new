from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserView(APIView):
    """
    Ye User endpoint ka base view hai.
    Abhi basic GET response return karta hai.
    """

    def get(self, request):
        return Response({"message": "User endpoint working"}, status=status.HTTP_200_OK)
