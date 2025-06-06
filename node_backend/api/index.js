import dotenv from "dotenv";
dotenv.config();

import { connectDB } from "./src/db/connection.js";
import { app } from "./src/app.js";
import serverless from "serverless-http";

let isConnected = false;
const serverlessHandler = serverless(app);

export const handler = async (event, context) => {
  try {
    if (!isConnected) {
      await connectDB();
      isConnected = true;
    }
    return await serverlessHandler(event, context);
  } catch (error) {
    console.error("Handler error:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Internal Server Error" }),
    };
  }
};
