import mongoose from "mongoose";

const connectDB = async () => {
  try {
    const connectionInstance = await mongoose.connect(process.env.MONGODB_URL, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    console.log(`✅ MONGODB CONNECTED! HOST: ${connectionInstance.connection.host}`);
  } catch (error) {
    console.error("❌ MONGODB CONNECTION FAILED!", error);
    throw error;  // IMPORTANT: Throw instead of exiting the process (Vercel-safe)
  }
};

export { connectDB };