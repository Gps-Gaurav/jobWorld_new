import dotenv from 'dotenv';
dotenv.config();

import { connectDB } from '../src/db/connection.js';  // adjust relative path if needed
import { app } from '../src/app.js';
import serverless from 'serverless-http';

let isConnected = false;
const serverlessHandler = serverless(app);

export const handler = async (event, context) => {
  if (!isConnected) {
    try {
      await connectDB();
      console.log('Connected to MongoDB');
      isConnected = true;
    } catch (error) {
      console.error('MongoDB connection error:', error);
      throw error;  // so Vercel knows something went wrong
    }
  }
  return serverlessHandler(event, context);
};