from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from api.db import companies_collection
from api.utils.jwt_auth import get_user_from_request
from api.utils.bson_parser import convert_objectid
from api.utils.cloudinary_upload import upload_to_cloudinary  # Custom helper
import os
from datetime import datetime
from api.permissions import IsAuthenticatedWithJWT, IsAdminOrRecruiter
from rest_framework.decorators import permission_classes


#  Register company
class RegisterCompanyView(APIView):
     @permission_classes([IsAuthenticatedWithJWT, IsAdminOrRecruiter])
     def post(self, request):
        data = request.data
        required = ["companyName", "location"]

        for field in required:
            if field not in data:
                return Response({"error": f"{field} is required"}, status=400)

        if companies_collection.find_one({"companyName": data["companyName"]}):
            return Response({"error": "Company with same name exists"}, status=400)

        user = get_user_from_request(request)

        company = {
            "companyName": data["companyName"],
            "description": data.get("description", ""),
            "website": data.get("website", ""),
            "location": data["location"],
            "logo": data.get("logo", ""),
            "userId": user["_id"],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

        inserted = companies_collection.insert_one(company)  # ✅ FIXED

        return Response({
            "message": "Company registered",
            "company": {
                "_id": str(inserted.inserted_id),  # ✅ No more NameError
                "companyName": company["companyName"],
                "location": company["location"]
            }
        }, status=201)
#  Get all companies for current user

class GetCompanyView(APIView):
    permission_classes = [IsAuthenticatedWithJWT, IsAdminOrRecruiter]

    def get(self, request):
        user = get_user_from_request(request)
        print("👤 User:", user)

        user_id = user.get("_id")

        # Handle both string and ObjectId in DB
        companies = list(companies_collection.find({
            "$or": [
                {"userId": user_id},
                {"userId": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"_id": None}
            ]
        }))
        print("🏢 Companies:", companies)

        return Response(convert_objectid(companies), status=200)


#  Get single company

class GetCompanyByIdView(APIView):
    @permission_classes([IsAuthenticatedWithJWT, IsAdminOrRecruiter])
    def get(self, request, company_id):
        company = companies_collection.find_one({"_id": ObjectId(company_id)})
        if not company:
            return Response({"error": "Company not found"}, status=404)
        return Response(convert_objectid(company), status=200)


# Update company with optional logo upload

class UpdateCompanyView(APIView):
    @permission_classes([IsAuthenticatedWithJWT, IsAdminOrRecruiter])
    def put(self, request, company_id):
        user = get_user_from_request(request)
        data = request.data
        logo_file = request.FILES.get("logo")

        company = companies_collection.find_one({"_id": ObjectId(company_id)})
        if not company:
            return Response({"error": "Company not found"}, status=404)

        update_data = {}
        for field in ["companyName", "description", "location", "website"]:
            if data.get(field):
                update_data[field] = data.get(field)

        if logo_file:
            logo_url = upload_to_cloudinary(logo_file)
            if not logo_url:
                return Response({"error": "Cloudinary upload failed"}, status=400)
            update_data["logo"] = logo_url

        companies_collection.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": update_data}
        )

        updated = companies_collection.find_one({"_id": ObjectId(company_id)})
        return Response(convert_objectid(updated), status=200)
