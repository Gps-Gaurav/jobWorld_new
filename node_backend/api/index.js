// 📦 .env config load karo (sensitive config env se)
import dotenv from "dotenv";
dotenv.config();

// 🔌 Database connection aur express app import karo
import { connectDB } from "../src/db/connection.js";
import { app } from "../src/app.js";

// 🖥️ Serverless lambda ke liye handler wrap karo
import serverless from "serverless-http";

let isConnected = false; // ✅ MongoDB connection ka track
const serverlessHandler = serverless(app); // 🔄 Express app ko Lambda compatible banaya

// 📤 AWS Lambda handler function
export const handler = async (event, context) => {
  try {
    // 🧠 Agar abhi tak DB se connect nahi hue ho, toh ab connect karo
    if (!isConnected) {
      console.log("Connecting to MongoDB...");
      await connectDB();
      isConnected = true;
    }

    // 🧾 Lambda ko request bhejna
    return await serverlessHandler(event, context);
  } catch (error) {
    // ❌ Error agar aaya toh log karo aur 500 return karo
    console.error("Handler Error:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "Internal Server Error",
        details: error.message
      }),
    };
  }
};
