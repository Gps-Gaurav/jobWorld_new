import { Job } from "../models/job.model.js";
import { apiError } from "../utils.js/apiError.utils.js";
import { asyncHandler } from "../utils.js/asyncHandler.utils.js";
import { apiResponse } from "../utils.js/apiResponse.utils.js";
import mongoose from "mongoose";
import { Company } from "../models/company.model.js";

// ✅ New Job Post Karne Ka Handler
const postJob = asyncHandler(async (req, res) => {
    const {
        title, description, requirements, salary,
        location, jobType, position, companyId, experience
    } = req.body;

    // Sabhi fields ka validation
    if (!title || !description || !requirements || !salary ||
        !location || !experience || !jobType || !position || !companyId) {
        throw new apiError(400, "All fields are required");
    }

    // Company ID valid hai ya nahi
    const company = await Company.findById(companyId);
    if (!company) {
        throw new apiError(404, "Company not found");
    }

    // Job Create Karna
    const newJob = await Job.create({
        title,
        description,
        requirements: requirements.split(",").map(req => req.trim()),
        salary: Number(salary),
        location: Array.isArray(location) ? location : location.split(",").map(loc => loc.trim()),
        jobType,
        experience,
        position,
        company: companyId,
        created_by: req.user._id,
    });

    return res.status(201).json(new apiResponse(201, newJob, "Job Posted Successfully"));
});

// ✅ Sabhi Jobs Ko Fetch Karna (Search ke saath)
const getAllJobs = asyncHandler(async (req, res) => {
    const keyword = req.query.keyword || "";
    const query = {
        $or: [
            { title: { $regex: keyword, $options: "i" } },
            { description: { $regex: keyword, $options: "i" } }
        ]
    };

    const jobs = await Job.find(query)
        .populate({
            path: "company",
            select: "companyName description website location logo userId",
        })
        .sort({ createdAt: -1 });

    if (!jobs || jobs.length === 0) {
        throw new apiError(404, "No jobs found");
    }

    return res.status(200).json(new apiResponse(200, jobs, "Jobs Retrieved Successfully"));
});

// ✅ Single Job Details Fetch Karna by Job ID
const getJobById = asyncHandler(async (req, res) => {
    const jobId = req.params.id;

    // Object ID validate karna
    if (!mongoose.Types.ObjectId.isValid(jobId)) {
        throw new apiError(400, "Invalid Job ID");
    }

    const job = await Job.findById(jobId)
        .populate({ path: "company" })
        .populate({ path: "applications" });

    if (!job) {
        throw new apiError(404, "Job not found");
    }

    return res.status(200).json(new apiResponse(200, job, "Job Retrieved Successfully"));
});

// ✅ Admin Ke Banaye Sabhi Jobs Fetch Karna
const getJobsByAdmin = asyncHandler(async (req, res) => {
    const adminId = req.user?._id;

    if (!adminId) {
        throw new apiError(403, "Admin ID not found");
    }

    const jobs = await Job.find({ created_by: adminId })
        .populate({ path: "company" });

    if (!jobs || jobs.length === 0) {
        throw new apiError(404, "No jobs found");
    }

    return res.status(200).json(new apiResponse(200, jobs, "Jobs Retrieved Successfully"));
});

// ✅ Job Update Karne Ka Handler
const updateJob = asyncHandler(async (req, res) => {
    const jobId = req.params.id;
    const {
        title, description, requirements, salary,
        location, jobType, position, companyId, experience
    } = req.body;

    if (!mongoose.Types.ObjectId.isValid(jobId)) {
        throw new apiError(400, "Invalid Job ID");
    }

    // Agar company id di gayi hai to uska existence check karo
    if (companyId) {
        const company = await Company.findById(companyId);
        if (!company) {
            throw new apiError(404, "Company not found");
        }
    }

    // Dynamic update fields
    const updateData = {};
    if (title) updateData.title = title;
    if (description) updateData.description = description;
    if (requirements) updateData.requirements = requirements.split(",").map(req => req.trim());
    if (salary) updateData.salary = Number(salary);
    if (location) updateData.location = Array.isArray(location) ? location : location.split(",").map(loc => loc.trim());
    if (jobType) updateData.jobType = jobType;
    if (experience) updateData.experience = experience;
    if (position) updateData.position = position;
    if (companyId) updateData.company = companyId;

    const updatedJob = await Job.findByIdAndUpdate(
        jobId,
        { $set: updateData },
        { new: true }
    ).populate({ path: "company" });

    if (!updatedJob) {
        throw new apiError(404, "Job not found");
    }

    return res.status(200).json(new apiResponse(200, updatedJob, "Job updated successfully"));
});

// ✅ Job Delete Karne Ka Handler
const deleteJob = asyncHandler(async (req, res) => {
    const jobId = req.params.id;

    if (!mongoose.Types.ObjectId.isValid(jobId)) {
        throw new apiError(400, "Invalid Job ID");
    }

    const deletedJob = await Job.findByIdAndDelete(jobId);
    if (!deletedJob) {
        throw new apiError(404, "Job not found");
    }

    return res.status(200).json(new apiResponse(200, deletedJob, "Job deleted successfully"));
});

export {
    postJob,
    getAllJobs,
    getJobById,
    getJobsByAdmin,
    updateJob,
    deleteJob
};
