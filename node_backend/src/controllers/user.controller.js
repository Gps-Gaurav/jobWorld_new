import { asyncHandler } from "../utils.js/asyncHandler.utils.js";
import { apiError } from "../utils.js/apiError.utils.js";
import { User } from "../models/user.model.js";
import { apiResponse } from "../utils.js/apiResponse.utils.js";
import { uploadOnCloudinary, deleteFromCloudinary } from "../utils.js/cloudinary.utils.js";
import jwt from 'jsonwebtoken';
import getDataUri from "../utils.js/dataURI.utils.js";
import cloudinary from "../utils.js/file.cloudinary.utils.js";
import axios from "axios";
import path from 'path';
import { Application } from "../models/application.model.js";
import crypto from 'crypto';
import nodemailer from 'nodemailer';
import fs from 'fs';
import bcrypt from "bcrypt";

const generateAcessTokenAndRefreshToken = async (userId) => {
    try {
        const user = await User.findById(userId);
        if (!user) {
            throw new apiError(404, "User not found");
        }

        // Using the methods defined in your user model
        const accessToken = await user.genAccessToken();
        const refreshToken = await user.genRefreshToken();

        // Save refresh token to user
        user.refreshToken = refreshToken;
        await user.save({ validateBeforeSave: false });

        return { accessToken, refreshToken };
    } catch (error) {
        console.error("Token generation error:", error);
        throw new apiError(500, "Error while generating tokens");
    }
};

const loginUser = asyncHandler(async (req, res) => {
    try {
        // 1. Extract credentials
        const { identifier, password, role } = req.body;

        // 2. Validate input
        if (!identifier || !password || !role) {
            throw new apiError(400, "Email/Phone, password and role are required");
        }

        // 3. Validate role
        if (!["student", "recruiter"].includes(role)) {
            throw new apiError(400, "Invalid role specified");
        }

        // 4. Find user with exact role match
        const user = await User.findOne({
            $and: [
                { $or: [{ email: identifier }, { phoneNumber: identifier }] },
                { role: role }
            ]
        }).select("+password"); // Explicitly selecting password

        if (!user) {
            throw new apiError(401, `No ${role} account found with these credentials`);
        }

        // 5. Verify password using the comparePassword method from your schema
        const isPasswordValid = await user.comparePassword(password);
        if (!isPasswordValid) {
            throw new apiError(401, "Invalid password");
        }

        // 6. Generate tokens
        const { accessToken, refreshToken } = await generateAcessTokenAndRefreshToken(user._id);

        // 7. Get user without sensitive info
        const loggedInUser = await User.findById(user._id)
            .select("-password -refreshToken -resetPasswordToken -resetPasswordExpiry");

        // 8. Set cookie options
        const options = {
            httpOnly: true,
            secure: true,
            sameSite: "None",
            maxAge: 24 * 60 * 60 * 1000 // 24 hours
        };

        // 9. Add login timestamp in UTC
        const loginTimestamp = new Date().toISOString();
        user.lastLoginAt = loginTimestamp;
        await user.save({ validateBeforeSave: false });

        // 10. Send response
        return res
            .status(200)
            .cookie("accessToken", accessToken, options)
            .cookie("refreshToken", refreshToken, options)
            .json(
                new apiResponse(
                    200,
                    {
                        user: {
                            ...loggedInUser.toObject(),
                            lastLoginAt: loginTimestamp
                        },
                        accessToken,
                        refreshToken
                    },
                    `Welcome back, ${user.fullName}!`
                )
            );

    } catch (error) {
        console.error("Login error:", error);
        throw new apiError(
            error.statusCode || 500,
            error.message || "Login failed"
        );
    }
});
const registerUser = asyncHandler(async (req, res) => {
    // 1. Extract and validate required fields
    const { 
        fullName, 
        email, 
        password, 
        phoneNumber, 
        role, 
        bio = "" 
    } = req.body;

    // 2. Validate required fields
    if (!fullName || !email || !password || !phoneNumber || !role) {
        throw new apiError(400, "All required fields must be provided");
    }

    // 3. Validate email format
    const emailRegex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
    if (!emailRegex.test(email)) {
        throw new apiError(400, "Please provide a valid email address");
    }

    // 4. Validate phone number format (assuming 10 digits)
    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(phoneNumber)) {
        throw new apiError(400, "Please provide a valid phone number");
    }

    // 5. Check if user already exists
    const existingUser = await User.findOne({
        $or: [
            { email },
            { phoneNumber }
        ]
    });

    if (existingUser) {
        throw new apiError(
            400, 
            `User already exists with this ${existingUser.email === email ? 'email' : 'phone number'}`
        );
    }

    // 6. Handle file uploads
    let avatar = null;
    let coverImage = null;

    try {
        // Handle avatar upload
        if (req.files?.avatar?.[0]?.path) {
            const avatarResult = await uploadOnCloudinary(req.files.avatar[0].path);
            if (!avatarResult?.secure_url) {
                throw new apiError(400, "Error uploading avatar");
            }
            avatar = avatarResult.secure_url;
        }

        // Handle cover image upload
        if (req.files?.coverImage?.[0]?.path) {
            const coverImageResult = await uploadOnCloudinary(req.files.coverImage[0].path);
            if (!coverImageResult?.secure_url) {
                throw new apiError(400, "Error uploading cover image");
            }
            coverImage = coverImageResult.secure_url;
        }
    } catch (error) {
        throw new apiError(500, "Error while uploading images: " + error.message);
    }

    // 7. Create new user
    const user = await User.create({
        fullName: fullName.trim(),
        email: email.toLowerCase(),
        password,
        phoneNumber,
        role,
        profile: {
            bio: bio.trim(),
            avatar,
            coverImage
        }
    });

    // 8. Generate tokens for automatic login
    const { accessToken, refreshToken } = await generateAcessTokenAndRefreshToken(user._id);

    // 9. Fetch created user without sensitive information
    const createdUser = await User.findById(user._id)
        .select("-password -refreshToken");

    if (!createdUser) {
        throw new apiError(500, "Something went wrong while registering the user");
    }

    // 10. Set cookie options
    const options = {
        httpOnly: true,
        secure: true,
        sameSite: "None",
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    };

    // 11. Send response
    return res
        .status(201)  // Changed to 201 for resource creation
        .cookie("accessToken", accessToken, options)
        .cookie("refreshToken", refreshToken, options)
        .json(
            new apiResponse(
                201,
                {
                    user: createdUser,
                    accessToken,
                    refreshToken
                },
                `Welcome ${createdUser.fullName}! You are registered successfully`
            )
        );
});

const logOut = asyncHandler(async (req, res) => {
    // Remove token from database
    await User.findByIdAndUpdate(
        req.user._id,
        { $unset: { accessToken: 1 } }, // Removes the accessToken field
        { new: true }
    );

    // Remove token from cookies
    res.clearCookie("accessToken", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production", // ✅ Secure only in production
        sameSite: "None", // ✅ Required for cross-origin requests
    });

    return res.status(200).json(
        new apiResponse(200, {}, "User logged out successfully")
    );
});
const refreshToken = asyncHandler(async (req, res) => {
    const incomingRefreshToken = req.cookies.refreshToken || req.body.refreshToken;

    if (!incomingRefreshToken) {
        throw new apiError(400, "incomingRefreshToken Not found");
    }
    const decodedToken = jwt.verify(incomingRefreshToken, process.env.REFRESH_TOKEN_SECRET);
    // console.log("decodedToken", decodedToken)
    //ye decodedToken conatain kr rha h user ki _id,ye hr haal, me verify hoga ydi incomingrefreshToken ka structure shi h,but,problem is that,how to check this is actual user ki hi _id h, kisi dusre ki bhi to _id ho skti h.. ese check krne k liye   (incomingRefreshToken != user.refreshToken) ese check kro
    const user = await User.findById(decodedToken._id);
    if (!user) {
        throw new apiError(400, "Unauthorized access due to invalid refrshtoken");
    }
    // console.log("user is", user)
    // console.log("user.refreshToken", user.refreshToken);
    if (incomingRefreshToken != user.refreshToken) {
        throw new apiError(400, "refresh token is  expired or used");
    }

    const { accessToken, refreshToken } = await generateAcessTokenAndRefreshToken(user._id);
    //sending new refreshtoken
    const options = {
        httpOnly: true,
        secure: true,
    }
    return res
        .status(200)
        .cookie("accesstoken", accessToken, options)
        .cookie("refreshToken", refreshToken, options)
        .json(
            new apiResponse(200, { accessToken, refreshToken }, "User token refreshed sucessfuuly")
        )
})
const changePassword = asyncHandler(async (req, res) => {
    const { oldPassword, newPassword } = req.body;
    // console.log("oldPassword", oldPassword);
    // console.log("newPassword", newPassword);
    const user = await User.findById(req.user?._id);
    // console.log(user);
    const isPasswordCorrect = await user.comparePassword(oldPassword);
    // console.log(isPasswordCorrect);
    if (!isPasswordCorrect) {
        throw new apiError(401, "Old password is incorrect");
    }
    user.password = newPassword;
    await user.save({ validateBeforeSave: false });
    return res
        .status(200)
        .json(new apiResponse(200, {}, "Password changed successfully"));
})
const getCurrentUser = asyncHandler(async (req, res) => {
    const user = await User.findById(req.user?._id).select('-password');
    // console.log(user);
    return res
        .status(200)
        .json(
            new apiResponse(200, user, "User data fetched successfully")
        )

})
const updateAvatar = asyncHandler(async (req, res) => {
    // console.log(req.file);
    const avatarLocalPath = req.file?.path;
    if (!avatarLocalPath) {
        throw new apiError(400, "Avatar file is missing");
    }
    const avatar = await uploadOnCloudinary(avatarLocalPath);
    if (!avatar.url) {
        throw new apiError(401, "Error while Uploading avatar on Cloudinary");
    }
    const user = await User.findByIdAndUpdate(req.user._id, {
        $set: {
            avatar: avatar.url,
        }
    }, { new: true }).select('-password');
    return res
        .status(200)
        .json(
            new apiResponse(200, user, "User Avatar Upadated Successfully")
        )
})
const updateUserCoverImage = asyncHandler(async (req, res) => {
    const coverImageLocalPath = req.file?.path;

    if (!coverImageLocalPath) {
        throw new apiError(400, "Cover image file is missing");
    }

    try {
        const coverImage = await uploadOnCloudinary(coverImageLocalPath);

        if (!coverImage.url) {
            throw new apiError(401, "Error while uploading cover image to cloudinary");
        }

        const user = await User.findByIdAndUpdate(
            req.user?._id,
            {
                $set: {
                    "profile.coverImage": coverImage.url
                }
            },
            { new: true }
        ).select('-password');

        if (!user) {
            throw new apiError(404, "User not found");
        }

        return res.status(200).json({
            success: true,
            message: "Cover image updated successfully",
            data: user
        });
    } catch (error) {
        // Clean up the local file if it exists
        if (coverImageLocalPath) {
            fs.unlinkSync(coverImageLocalPath);
        }
        throw error;
    }
});
const deleteUserCoverImage = asyncHandler(async (req, res) => {
    try {
        const user = await User.findByIdAndUpdate(
            req.user?._id,
            {
                $set: {
                    "profile.coverImage": ""
                }
            },
            { new: true }
        ).select('-password');

        if (!user) {
            throw new apiError(404, "User not found");
        }

        return res.status(200).json({
            success: true,
            message: "Cover image removed successfully",
            data: user
        });
    } catch (error) {
        throw error;
    }
});
const updateAccountDetails = asyncHandler(async (req, res) => {
    try {
        const {
            fullName,
            email,
            phoneNumber,
            bio,
            skills,
            location,
            education,
            experience,
            languages,
            certifications,
            socialLinks,
            interests,
            preferredJobTypes,
            expectedSalary
        } = req.body;
        const file = req.file;

        // Validate file type if present
        if (file) {
            const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!allowedTypes.includes(file.mimetype)) {
                throw new apiError(400, "Invalid file type. Please upload a PDF or Word document.");
            }
        }

        // Process skills
        let skillsArray = [];
        if (skills) {
            skillsArray = skills.split(",").map(skill => skill.trim());
        }

        // Get user ID from middleware
        const userId = req.user._id;

        // Find user in the database
        let user = await User.findById(userId);
        if (!user) {
            throw new apiError(404, "User not found.");
        }

        // Update basic fields
        if (fullName) user.fullName = fullName;
        if (email) user.email = email;
        if (phoneNumber) user.phoneNumber = phoneNumber;
        if (bio) user.profile.bio = bio;
        if (skills) user.profile.skills = skillsArray;

        // Safely parse and update complex fields
        try {
            if (location) user.profile.location = JSON.parse(location);
            if (education) user.profile.education = JSON.parse(education);
            if (experience) user.profile.experience = JSON.parse(experience);
            if (languages) user.profile.languages = JSON.parse(languages);
            if (certifications) user.profile.certifications = JSON.parse(certifications);
            if (socialLinks) user.profile.socialLinks = JSON.parse(socialLinks);
            if (interests) user.profile.interests = JSON.parse(interests);
            if (preferredJobTypes) user.profile.preferredJobTypes = JSON.parse(preferredJobTypes);
            if (expectedSalary) user.profile.expectedSalary = JSON.parse(expectedSalary);
        } catch (parseError) {
            throw new apiError(400, "Invalid JSON data in one or more fields.");
        }

        // Handle file upload for resume
        if (file) {
            try {
                const fileUri = getDataUri(file);
                const cloudResponse = await cloudinary.uploader.upload(fileUri.content, {
                    resource_type: 'raw',
                    folder: 'resumes',
                    flags: 'attachment:true',
                    format: path.extname(file.originalname).slice(1),
                    use_filename: true,
                    unique_filename: false,
                    filename_override: file.originalname
                });
                user.profile.resume = cloudResponse.secure_url;
                user.profile.resumeOriginalName = file.originalname;
            } catch (uploadError) {
                throw new apiError(500, "Error uploading resume to cloud storage.");
            }
        }

        // Save updated user details to the database with validateBeforeSave: false to skip password validation
        await user.save({ validateBeforeSave: false });

        // Return success response
        return res.status(200).json({
            success: true,
            message: "Profile updated successfully",
            user: user
        });

    } catch (error) {
        console.error("Error in updateAccountDetails:", error);
        return res.status(error.statusCode || 500).json({
            success: false,
            message: error.message || "Error updating profile"
        });
    }
});
const AI = asyncHandler(async (req, res) => {
    console.log("Backend is working!");

    try {
        const userMessage = req.body.message;

        if (!userMessage || typeof userMessage !== 'string') {
            return res.status(400).json({ error: 'Valid message is required' });
        }

        // Constructing the request payload for the Gemini API
        const payload = {
            contents: [
                {
                    parts: [
                        {
                            text: userMessage,
                        },
                    ],
                },
            ],
        };

        // Call the Gemini API
        const response = await axios.post(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
            payload,
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        // Extracting the bot's reply from the Gemini API response
        const botReply = response.data?.candidates?.[0]?.content?.parts?.[0]?.text ||
            'Sorry, I couldn\'t generate a reply. Please try again later.';

        console.log('Bot Reply:', botReply);

        return res.json({ reply: botReply });
    } catch (error) {
        console.error('Error during API request:', error.response?.data || error.message);

        // Respond with an error message if something goes wrong
        return res
            .status(500)
            .json({ error: 'Something went wrong with the chat request.' });
    }
});
const forgotPassword = asyncHandler(async (req, res) => {
    const { email } = req.body;

    if (!email) {
        throw new apiError(400, "Email is required");
    }

    const user = await User.findOne({ email });
    if (!user) {
        throw new apiError(404, "User not found");
    }

    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetTokenExpiry = Date.now() + 10 * 60 * 1000; // 10 minutes

    // Save reset token to user
    user.resetPasswordToken = resetToken;
    user.resetPasswordExpiry = resetTokenExpiry;
    await user.save({ validateBeforeSave: false });

    // Create reset URL with query parameter
    const resetUrl = `${process.env.FRONTEND_URL}/reset-password?token=${resetToken}`;

    // Create email transporter with more detailed configuration
    const transporter = nodemailer.createTransport({
        host: 'smtp.gmail.com',
        port: 587,
        secure: false, // true for 465, false for other ports
        auth: {
            user: process.env.EMAIL_USER,
            pass: process.env.EMAIL_PASSWORD
        },
        tls: {
            rejectUnauthorized: false // Only use this in development
        }
    });

    // Email content with better formatting
    const mailOptions = {
        from: `"Workify Support" <${process.env.EMAIL_USER}>`,
        to: email,
        subject: 'Password Reset Request - Workify',
        html: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Password Reset Request</h2>
                <p>Hello ${user.fullName},</p>
                <p>We received a request to reset your password. Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="${resetUrl}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">This link will expire in 10 minutes.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">This is an automated email, please do not reply.</p>
            </div>
        `
    };

    try {
        // Verify transporter configuration
        await transporter.verify();

        // Send email
        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent:', info.messageId);

        return res.status(200).json(
            new apiResponse(200, {}, "Password reset email sent successfully")
        );
    } catch (error) {
        console.error('Email error:', error);

        // Clear reset token on error
        user.resetPasswordToken = undefined;
        user.resetPasswordExpiry = undefined;
        await user.save({ validateBeforeSave: false });

        throw new apiError(500, "Error sending email. Please try again later.");
    }
});
const resetPassword = asyncHandler(async (req, res) => {
    const { token, newPassword } = req.body;

    if (!token || !newPassword) {
        throw new apiError(400, "Token and new password are required");
    }

    const user = await User.findOne({
        resetPasswordToken: token,
        resetPasswordExpiry: { $gt: Date.now() }
    });

    if (!user) {
        throw new apiError(400, "Invalid or expired reset token");
    }

    // Update password
    user.password = newPassword;
    user.resetPasswordToken = undefined;
    user.resetPasswordExpiry = undefined;
    await user.save();

    return res.status(200).json(
        new apiResponse(200, {}, "Password reset successful")
    );
});
const validateResetToken = asyncHandler(async (req, res) => {
    const { token } = req.query;

    if (!token) {
        throw new apiError(400, "Token is required");
    }

    const user = await User.findOne({
        resetPasswordToken: token,
        resetPasswordExpiry: { $gt: Date.now() }
    });

    if (!user) {
        throw new apiError(400, "Invalid or expired reset token");
    }

    return res.status(200).json(
        new apiResponse(200, { valid: true }, "Token is valid")
    );
});
export {
    AI,
    registerUser,
    loginUser,
    logOut,
    refreshToken,
    changePassword,
    getCurrentUser,
    updateAvatar,
    updateUserCoverImage,
    deleteUserCoverImage,
    updateAccountDetails,
    forgotPassword,
    resetPassword,
    validateResetToken
};