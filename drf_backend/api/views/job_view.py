from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from api.db import jobs_collection, companies_collection
from api.db import users_collection  # If needed for auth

from datetime import datetime


#  Job Post (Protected)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_job(request):
    try:
        data = request.data
        user_id = request.user.id

        required_fields = [
            'title', 'description', 'requirements', 'salary',
            'location', 'experience', 'jobType', 'position', 'companyId'
        ]

        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Company check
        company = companies_collection.find_one({"_id": ObjectId(data['companyId'])})
        if not company:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        job = {
            "title": data['title'],
            "description": data['description'],
            "requirements": [r.strip() for r in data['requirements'].split(",")],
            "salary": float(data['salary']),
            "location": data['location'] if isinstance(data['location'], list) else [loc.strip() for loc in data['location'].split(",")],
            "jobType": data['jobType'],
            "experience": data['experience'],
            "position": data['position'],
            "company": ObjectId(data['companyId']),
            "created_by": ObjectId(user_id),
            "createdAt": datetime.utcnow()
        }

        result = jobs_collection.insert_one(job)
        job['_id'] = result.inserted_id

        return Response(job, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Get all jobs (with optional keyword search)
@api_view(['GET'])
def get_all_jobs(request):
    try:
        keyword = request.query_params.get('keyword', '')

        query = {
            "$or": [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}}
            ]
        } if keyword else {}

        jobs = list(jobs_collection.find(query).sort("createdAt", -1))

        for job in jobs:
            company = companies_collection.find_one(
                {"_id": job["company"]},
                {"companyName": 1, "description": 1, "website": 1, "location": 1, "logo": 1}
            )
            job["company"] = company

        if not jobs:
            return Response({"error": "No jobs found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(jobs, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Get job by ID
@api_view(['GET'])
def get_job_by_id(request, job_id):
    try:
        if not ObjectId.is_valid(job_id):
            return Response({"error": "Invalid Job ID"}, status=status.HTTP_400_BAD_REQUEST)

        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        if not job:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        company = companies_collection.find_one({"_id": job["company"]})
        job["company"] = company

        return Response(job, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Get all jobs created by the current admin
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jobs_by_admin(request):
    try:
        admin_id = request.user.id
        jobs = list(jobs_collection.find({"created_by": ObjectId(admin_id)}))

        for job in jobs:
            company = companies_collection.find_one({"_id": job["company"]})
            job["company"] = company

        if not jobs:
            return Response({"error": "No jobs found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(jobs, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Update job
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_job(request, job_id):
    try:
        if not ObjectId.is_valid(job_id):
            return Response({"error": "Invalid Job ID"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        update_data = {}

        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'requirements' in data:
            update_data['requirements'] = [r.strip() for r in data['requirements'].split(",")]
        if 'salary' in data:
            update_data['salary'] = float(data['salary'])
        if 'location' in data:
            update_data['location'] = data['location'] if isinstance(data['location'], list) else [loc.strip() for loc in data['location'].split(",")]
        if 'jobType' in data:
            update_data['jobType'] = data['jobType']
        if 'experience' in data:
            update_data['experience'] = data['experience']
        if 'position' in data:
            update_data['position'] = data['position']
        if 'companyId' in data:
            if not ObjectId.is_valid(data['companyId']):
                return Response({"error": "Invalid Company ID"}, status=status.HTTP_400_BAD_REQUEST)
            company = companies_collection.find_one({"_id": ObjectId(data['companyId'])})
            if not company:
                return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
            update_data['company'] = ObjectId(data['companyId'])

        result = jobs_collection.find_one_and_update(
            {"_id": ObjectId(job_id)},
            {"$set": update_data},
            return_document=True
        )

        if not result:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Delete job
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request, job_id):
    try:
        if not ObjectId.is_valid(job_id):
            return Response({"error": "Invalid Job ID"}, status=status.HTTP_400_BAD_REQUEST)

        result = jobs_collection.find_one_and_delete({"_id": ObjectId(job_id)})
        if not result:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
