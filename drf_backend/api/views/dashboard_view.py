
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.db import users_collection, applications_collection, jobs_collection, companies_collection
from bson import ObjectId
from datetime import datetime, timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    try:
        user_id = request.user.id

        total_applied_jobs = applications_collection.count_documents({"applicant": ObjectId(user_id)})
        total_interviews = applications_collection.count_documents({"applicant": ObjectId(user_id), "status": "interview"})
        total_pending = applications_collection.count_documents({"applicant": ObjectId(user_id), "status": "pending"})
        total_rejected = applications_collection.count_documents({"applicant": ObjectId(user_id), "status": "rejected"})
        total_selected = applications_collection.count_documents({"applicant": ObjectId(user_id), "status": "selected"})
        total_jobs = jobs_collection.count_documents({})

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        profile = user.get("profile", {})
        profile_score = 0
        if profile.get("bio"): profile_score += 20
        if profile.get("skills"): profile_score += 20
        if profile.get("resume"): profile_score += 20
        if profile.get("avatar"): profile_score += 10
        if profile.get("coverImage"): profile_score += 10
        if user.get("phoneNumber"): profile_score += 10
        if user.get("email"): profile_score += 10

        return Response({
            "totalAppliedJobs": total_applied_jobs,
            "totalInterviews": total_interviews,
            "totalPending": total_pending,
            "totalRejected": total_rejected,
            "totalSelected": total_selected,
            "totalJobs": total_jobs,
            "profileScore": profile_score
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application_trends(request):
    try:
        user_id = request.user.id
        six_months_ago = datetime.utcnow() - timedelta(days=180)

        pipeline = [
            {
                "$match": {
                    "applicant": ObjectId(user_id),
                    "createdAt": {"$gte": six_months_ago}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$createdAt"},
                        "month": {"$month": "$createdAt"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]

        trends = list(applications_collection.aggregate(pipeline))

        formatted = [{
            "month": f"{item['_id']['year']}-{str(item['_id']['month']).zfill(2)}",
            "count": item['count']
        } for item in trends]

        return Response(formatted, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_skills(request):
    try:
        user_id = request.user.id
        user = users_collection.find_one({"_id": ObjectId(user_id)})

        profile = user.get("profile", {})
        skills = profile.get("skills", [])
        skills_data = [{"name": skill, "level": 80} for skill in skills]

        return Response(skills_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_global_stats(request):
    try:
        total_jobs = jobs_collection.count_documents({})
        total_users = users_collection.count_documents({})
        total_applications = applications_collection.count_documents({})
        total_companies = companies_collection.count_documents({})

        users = users_collection.find({}, {"profileScore": 1})
        total_score = sum(user.get("profileScore", 0) for user in users)
        average_score = round(total_score / total_users, 2) if total_users else 0

        return Response({
            "totalJobs": total_jobs,
            "totalUsers": total_users,
            "totalApplications": total_applications,
            "totalCompanies": total_companies,
            "averageProfileScore": average_score
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
