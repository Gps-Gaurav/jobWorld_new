import dotenv from "dotenv";
dotenv.config();

import { connectDB } from "./src/db/connection.js";
import { app } from "./src/app.js";
import serverless from "serverless-http";

let isConnected = false;
const serverlessHandler = serverless(app);

export const handler = async (event, context) => {
    console.log('Handler invoked!');
    try {
      if (!isConnected) {
        console.log('Connecting to MongoDB...');
        await connectDB();
        isConnected = true;
      }
      console.log('Passing to serverless handler...');
      return await serverlessHandler(event, context);
    } catch (error) {
      console.error('Error in handler:', error);
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Internal Server Error' }),
      };
    }
  };
