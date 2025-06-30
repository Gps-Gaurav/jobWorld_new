// 📦 Required Imports
import { compare } from "bcrypt";
import { Company } from "../models/company.model.js";
import { apiError } from "../utils.js/apiError.utils.js";
import { apiResponse } from "../utils.js/apiResponse.utils.js";
import { asyncHandler } from "../utils.js/asyncHandler.utils.js";
import { uploadOnCloudinary } from "../utils.js/cloudinary.utils.js";
import mongoose from "mongoose";
import fs from "fs";

// 🏢 Company Register karna
const registerCompany = asyncHandler(async (req, res) => {
    const { companyName, location, website, description } = req.body;

    // ❌ Validation: companyName required hai
    if (!companyName) {
        throw new apiError(404, "companyName is required");
    }

    // 🔍 Check karo ki same name wali company already exist to nahi karti
    let company = await Company.findOne({ companyName });
    if (company) {
        throw new apiError(401, `Company with ${companyName} name already exists! So try with another name`);
    }

    // ✅ Company create karo (logo skip kiya gaya abhi)
    company = await Company.create({
        companyName,
        description,
        location,
        website,
        userId: req.user._id
    });

    console.log("Created company is:", company);

    return res.status(200).json(
        new apiResponse(200, company, "Company created successfully")
    );
});

// 📋 Get all companies for current user
const getCompany = asyncHandler(async (req, res) => {
    const companies = await Company.find({ userId: req.user?._id });

    return res.status(200).json(
        new apiResponse(200, companies || [], "Companies retrieved successfully")
    );
});

// 🔍 Get company by ID
const getCompanyById = asyncHandler(async (req, res) => {
    const company = await Company.findById(req.params.id);
    if (!company) {
        throw new apiError(404, "Company not found");
    }

    return res.status(200).json(
        new apiResponse(200, company, "Company found successfully")
    );
});

// ✏️ Update company details
const updateCompany = asyncHandler(async (req, res) => {
    const { companyName, description, website, location } = req.body;

    // 🛑 Check karo ki company ID valid hai ya nahi
    if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
        throw new apiError(400, "Invalid company ID");
    }

    // 🔍 Check karo ki company exist karti hai ya nahi
    const existingCompany = await Company.findById(req.params.id);
    if (!existingCompany) {
        throw new apiError(404, "Company not found");
    }

    const logoLocalFilePath = req.files?.logo?.[0]?.path;
    let logo;

    try {
        // ☁️ Logo upload karo agar diya gaya hai
        if (logoLocalFilePath) {
            try {
                logo = await uploadOnCloudinary(logoLocalFilePath);
                if (!logo) {
                    throw new apiError(400, "Error uploading logo to cloudinary");
                }
            } catch (error) {
                console.error("Cloudinary upload error:", error);
                throw new apiError(400, "Error uploading logo: " + error.message);
            } finally {
                // 🧹 Local file ko delete karo
                if (fs.existsSync(logoLocalFilePath)) {
                    fs.unlinkSync(logoLocalFilePath);
                }
            }
        }

        // 🔁 Update data prepare karo
        const updateData = {};
        if (companyName) updateData.companyName = companyName;
        if (description) updateData.description = description;
        if (website) updateData.website = website;
        if (location) updateData.location = location;
        if (logo) updateData.logo = logo.secure_url;

        console.log("Update data:", updateData);

        // 🛠️ Update karo
        const company = await Company.findByIdAndUpdate(
            req.params.id,
            { $set: updateData },
            { new: true, runValidators: true }
        );

        return res.status(200).json(
            new apiResponse(200, company, "Company details updated successfully")
        );
    } catch (error) {
        // ❌ Error aane par bhi local file clean karo
        if (logoLocalFilePath && fs.existsSync(logoLocalFilePath)) {
            fs.unlinkSync(logoLocalFilePath);
        }
        console.error("Company update error:", error);
        throw error;
    }
});

// 📤 Export controller functions
export {
    registerCompany,
    getCompany,
    getCompanyById,
    updateCompany,
};
