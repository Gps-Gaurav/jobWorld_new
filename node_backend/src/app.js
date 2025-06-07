import express, { urlencoded } from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import compression from 'compression';
import mime from 'mime-types';

// Fix for ES Modules (__dirname and __filename)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

const allowedOrigins = [
    "https://jobworld-new.onrender.com",
    "http://localhost:4000",
    "http://localhost:5173",
];

// Add compression middleware
app.use(compression());

// Middleware
app.use(cors({
    origin: function (origin, callback) {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error("Not allowed by CORS"));
        }
    },
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allowedHeaders: ["Content-Type", "Authorization"],
}));

app.use((req, res, next) => {
    res.header("Access-Control-Allow-Credentials", "true");
    next();
});

// Request logging middleware
app.use((req, res, next) => {
    console.log('Request URL:', req.url);
    next();
});

app.use(express.json({ limit: "16kb" }));
app.use(urlencoded({ extended: true, limit: "16kb" }));
app.use(cookieParser());

const reactDistPath = path.resolve(__dirname, '../../React_frontend/dist');

// Verify build directory exists
if (!fs.existsSync(reactDistPath)) {
    console.error(`Build directory not found: ${reactDistPath}`);
    console.error('Please ensure you have built the React application');
    process.exit(1);
}

console.log('Serving static files from:', reactDistPath);

// Debug logging for asset requests
app.use((req, res, next) => {
    if (req.url.startsWith('/assets/')) {
        console.log('Asset request:', {
            url: req.url,
            path: path.join(reactDistPath, req.url)
        });
    }
    next();
});

// Serve assets with proper headers
app.use('/assets', express.static(path.join(reactDistPath, 'assets'), {
    setHeaders: (res, filePath) => {
        // Set content type based on file extension
        res.setHeader('Content-Type', mime.lookup(filePath) || 'application/octet-stream');
        // Add cache control headers
        res.setHeader('Cache-Control', 'public, max-age=31536000');
    },
    fallthrough: false // Return 404 instead of falling through
}));

// Serve other static files
app.use(express.static(reactDistPath));

// API routes
import userRouter from './routes/user.route.js';
import companyRouter from './routes/company.route.js';
import jobRouter from './routes/job.route.js';
import applicationRouter from './routes/application.route.js';
import dashboardRouter from './routes/dashboard.route.js';

app.use('/api/v1/user', userRouter);
app.use('/api/v1/company', companyRouter);
app.use('/api/v1/job', jobRouter);
app.use('/api/v1/application', applicationRouter);
app.use('/api/v1/dashboard', dashboardRouter);

// Explicit handler for asset files
app.get('/assets/*', (req, res, next) => {
    const filePath = path.join(reactDistPath, req.url);
    if (fs.existsSync(filePath)) {
        res.sendFile(filePath, (err) => {
            if (err) {
                console.error('Error sending file:', err);
                next(err);
            }
        });
    } else {
        next();
    }
});

// Enhanced fallback route with error handling
app.get('*', (req, res) => {
    const indexPath = path.join(reactDistPath, 'index.html');
    
    if (!fs.existsSync(indexPath)) {
        console.error(`Index file not found: ${indexPath}`);
        return res.status(500).send('Error: React build files not found. Please build the frontend application.');
    }
    
    res.sendFile(indexPath, (err) => {
        if (err) {
            console.error('Error sending index.html:', err);
            res.status(500).send('Error loading application: ' + err.message);
        }
    });
});

// Static file error handling
app.use((err, req, res, next) => {
    if (req.url.startsWith('/assets/')) {
        console.error('Static file error:', {
            url: req.url,
            error: err.message
        });
        return res.status(500).send('Error serving static file');
    }
    next(err);
});

// Global error handling middleware
app.use((err, req, res, next) => {
    console.error('Global error handler:', err.stack);
    res.status(500).send('Something broke!');
});

// CORS error handling
app.use((err, req, res, next) => {
    if (err.message === "Not allowed by CORS") {
        return res.status(403).json({
            success: false,
            message: "CORS error: Origin not allowed"
        });
    }
    next(err);
});

export { app };