// 📦 Required imports
import { Application } from "../models/application.model.js";
import { Job } from "../models/job.model.js";
import { asyncHandler } from "../utils.js/asyncHandler.utils.js";
import { apiResponse } from "../utils.js/apiResponse.utils.js";
import { apiError } from "../utils.js/apiError.utils.js";

// ✅ Job ke liye apply karna
const applyJob = asyncHandler(async (req, res) => {
    const userId = req.user?.id;
    const jobId = req.params?.id;

    // 🛑 jobId na ho to error
    if (!jobId) {
        throw new apiError(404, "jobId is required");
    }

    // 🔍 Check agar already applied hai to
    const existingApplication = await Application.findOne({
        job: jobId,
        applicant: userId,
    });
    if (existingApplication) {
        throw new apiError(400, "You have already applied for this job");
    }

    // 📄 Job exist karta hai ya nahi
    const job = await Job.findById(jobId);
    if (!job) {
        throw new apiError(404, "Job not found");
    }

    // 🆕 Application create karo
    const newApplication = await Application.create({
        job: jobId,
        applicant: userId,
    });

    // 📌 Job ke andar application push karo
    await Job.findByIdAndUpdate(jobId, {
        $push: { applications: newApplication._id }
    });

    return res.status(200).json(
        new apiResponse(200, newApplication, "Job applied successfully")
    );
});

// 📋 User ke sare applied jobs lana
const getAppliedJobs = asyncHandler(async (req, res) => {
    const userId = req.user?._id;

    // 🧾 Jobs fetch karo + populate job & company
    const appliedJobs = await Application.find({ applicant: userId })
        .sort({ createdAt: -1 })
        .populate({
            path: "job",
            options: { sort: { createdAt: -1 } },
            populate: {
                path: "company",
                options: { sort: { createdAt: -1 } },
            },
        });

    if (appliedJobs.length === 0) {
        throw new apiError(404, "You have not applied to any jobs yet");
    }

    return res.status(200).json(new apiResponse(200, appliedJobs));
});

// 👥 Kisi particular job ke applicants laana
const getApplicants = asyncHandler(async (req, res) => {
    const jobId = req.params.id;

    const job = await Job.findById(jobId).populate({
        path: 'applications',
        options: { sort: { createdAt: -1 } },
        populate: {
            path: 'applicant',
        },
    });

    if (!job || !job.applications.length) {
        throw new apiError(404, "No one has applied for this job");
    }

    return res.status(200).json(new apiResponse(200, job));
});

// 🛠️ Application status update karna
const updateStatus = asyncHandler(async (req, res) => {
    const applicationId = req.params.id;
    const { status } = req.body;

    // ❗ Status required hai
    if (!status) {
        throw new apiError(400, "Status is required");
    }

    const application = await Application.findById(applicationId);
    if (!application) {
        throw new apiError(400, "Application not found");
    }

    // 🔄 Status update karo
    application.status = status.toLowerCase();
    await application.save();

    return res.status(200).json(
        new apiResponse(200, application, "Application status updated successfully")
    );
});

// 📤 Export all controllers
export {
    applyJob,
    getAppliedJobs,
    getApplicants,
    updateStatus
};
