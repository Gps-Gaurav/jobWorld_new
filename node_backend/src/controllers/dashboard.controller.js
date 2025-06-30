// 📦 Required Imports
import { asyncHandler } from "../utils.js/asyncHandler.utils.js";
import { apiError } from "../utils.js/apiError.utils.js";
import { apiResponse } from "../utils.js/apiResponse.utils.js";
import { User } from "../models/user.model.js";
import { Application } from "../models/application.model.js";
import { Job } from "../models/job.model.js";
import { Company } from "../models/company.model.js";

// 📊 Ek user ke stats nikalne ke liye
const getUserStats = asyncHandler(async (req, res) => {
    try {
        const userId = req.user?._id;
        if (!userId) throw new apiError(401, "User not authenticated");

        // 👇 Multiple queries parallel mein chala rahe hain performance ke liye
        const [
            totalAppliedJobs,
            totalInterviews,
            totalPending,
            totalRejected,
            totalSelected,
            totalJobs
        ] = await Promise.all([
            Application.countDocuments({ applicant: userId }),
            Application.countDocuments({ applicant: userId, status: 'interview' }),
            Application.countDocuments({ applicant: userId, status: 'pending' }),
            Application.countDocuments({ applicant: userId, status: 'rejected' }),
            Application.countDocuments({ applicant: userId, status: 'selected' }),
            Job.countDocuments({})
        ]);

        // 🔍 User data fetch karke profileScore calculate kar rahe hain
        const user = await User.findById(userId);
        if (!user) throw new apiError(404, "User not found");

        let profileScore = 0;
        if (user?.profile?.bio) profileScore += 20;
        if (user?.profile?.skills?.length > 0) profileScore += 20;
        if (user?.profile?.resume) profileScore += 20;
        if (user?.profile?.avatar) profileScore += 10;
        if (user?.profile?.coverImage) profileScore += 10;
        if (user?.phoneNumber) profileScore += 10;
        if (user?.email) profileScore += 10;

        return res.status(200).json(
            new apiResponse(200, {
                totalAppliedJobs,
                totalInterviews,
                totalPending,
                totalRejected,
                totalSelected,
                totalJobs,
                profileScore
            }, "User stats fetched successfully")
        );
    } catch (error) {
        console.error("Error in getUserStats:", error);
        throw new apiError(500, error.message || "Error fetching user stats");
    }
});

// 📈 Application trends (last 6 months)
const getApplicationTrends = asyncHandler(async (req, res) => {
    try {
        const userId = req.user?._id;
        if (!userId) throw new apiError(401, "User not authenticated");

        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

        const trends = await Application.aggregate([
            {
                $match: {
                    applicant: userId,
                    createdAt: { $gte: sixMonthsAgo }
                }
            },
            {
                $group: {
                    _id: {
                        year: { $year: "$createdAt" },
                        month: { $month: "$createdAt" }
                    },
                    count: { $sum: 1 }
                }
            },
            {
                $sort: { "_id.year": 1, "_id.month": 1 }
            }
        ]);

        const formattedTrends = trends.map(trend => ({
            month: `${trend._id.year}-${trend._id.month.toString().padStart(2, '0')}`,
            count: trend.count
        }));

        return res.status(200).json(
            new apiResponse(200, formattedTrends, "Application trends fetched successfully")
        );
    } catch (error) {
        console.error("Error in getApplicationTrends:", error);
        throw new apiError(500, error.message || "Error fetching application trends");
    }
});

// 🧠 User ki skills aur level dekhna
const getUserSkills = asyncHandler(async (req, res) => {
    try {
        const userId = req.user?._id;
        if (!userId) throw new apiError(401, "User not authenticated");

        const user = await User.findById(userId);
        if (!user) throw new apiError(404, "User not found");

        const skillsData = user.profile?.skills?.map(skill => ({
            name: skill,
            level: 80 // Default level - future mein customize kar sakte ho
        })) || [];

        return res.status(200).json(
            new apiResponse(200, skillsData, "User skills fetched successfully")
        );
    } catch (error) {
        console.error("Error in getUserSkills:", error);
        throw new apiError(500, error.message || "Error fetching user skills");
    }
});

// 🌐 Global stats sab users, jobs, companies ke liye
const getGlobalStats = asyncHandler(async (req, res) => {
    try {
        const [totalJobs, totalUsers, totalApplications, totalCompanies, users] = await Promise.all([
            Job.countDocuments(),
            User.countDocuments(),
            Application.countDocuments(),
            Company.countDocuments(),
            User.find({}, 'profileScore')
        ]);

        const totalScore = users.reduce((sum, user) => sum + (user.profileScore || 0), 0);
        const averageProfileScore = users.length > 0
            ? Math.round((totalScore / users.length) * 100) / 100
            : 0;

        res.status(200).json({
            success: true,
            data: {
                totalJobs,
                totalUsers,
                totalApplications,
                totalCompanies,
                averageProfileScore
            }
        });
    } catch (error) {
        console.error('Error fetching global stats:', error);
        res.status(500).json({
            success: false,
            message: 'Error fetching global statistics',
            error: error.message
        });
    }
});

// 📤 Export all controller functions
export {
    getUserStats,
    getApplicationTrends,
    getUserSkills,
    getGlobalStats
};