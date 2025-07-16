from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from api.db import applications_collection, jobs_collection
from api.utils.jwt_auth import get_user_from_request  # Assume this gets user from JWT
from core.response import error_response, success_response

class ApplyJobView(APIView):
    def post(self, request, job_id):
        try:
            user = get_user_from_request(request)
            user_id = user["_id"]

            # 1. Already applied check
            existing = applications_collection.find_one({
                "job": ObjectId(job_id),
                "applicant": ObjectId(user_id)
            })

            if existing:
                return error_response("Already applied", status=400)

            # 2. Job existence check
            job = jobs_collection.find_one({"_id": ObjectId(job_id)})
            if not job:
                return error_response("Job not found", status=404)

            # 3. Create application
            application = {
                "job": ObjectId(job_id),
                "applicant": ObjectId(user_id),
                "status": "pending"
            }

            result = applications_collection.insert_one(application)

            # 4. Update job with application ID
            jobs_collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$push": {"applications": result.inserted_id}}
            )

            return success_response(message="Applied successfully")

        except Exception as e:
            return error_response("Something went wrong", status=500, details=str(e))


# Get all jobs applied by a user
class GetAppliedJobsView(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        user_id = user["_id"]

        applied_jobs = list(applications_collection.find({"applicant": ObjectId(user_id)}))

        if not applied_jobs:
            return Response({"error": "No applications found"}, status=404)

        # Optionally: populate job info manually
        for app in applied_jobs:
            job = jobs_collection.find_one({"_id": app["job"]})
            app["job_detail"] = job

        return Response(applied_jobs, status=200)


# 👥 Get applicants of a job
class GetApplicantsView(APIView):
    def get(self, request, job_id):
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})

        if not job or "applications" not in job or not job["applications"]:
            return Response({"error": "No applicants found"}, status=404)

        applicants = []
        for app_id in job["applications"]:
            app = applications_collection.find_one({"_id": ObjectId(app_id)})
            applicants.append(app)

        return Response(applicants, status=200)


# Update application status
class UpdateApplicationStatusView(APIView):
    def patch(self, request, app_id):
        status_new = request.data.get("status")
        if not status_new:
            return Response({"error": "Status is required"}, status=400)

        result = applications_collection.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {"status": status_new.lower()}}
        )

        if result.matched_count == 0:
            return Response({"error": "Application not found"}, status=404)

        return Response({"message": "Status updated"}, status=200)
