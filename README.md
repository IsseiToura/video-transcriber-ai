# Video Transcriber Project

This is a full-stack video transcription and analysis application with AI-powered features.

## Project Structure

```
VideoTransraper/
├── client/                 # Frontend React Application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── types/         # TypeScript type definitions
│   │   ├── App.tsx        # Main application component
│   │   └── main.tsx       # Application entry point
│   ├── public/            # Static assets
│   ├── package.json       # Dependencies and scripts
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── vite.config.ts     # Vite build configuration
│   └── README.md          # Frontend documentation
└── README.md              # This file - Project overview
```

## Features

### 🔐 Authentication

- User login/logout functionality
- Session management with localStorage
- Secure access to video features

### 🎥 Video Management

- Drag & drop video upload
- Multiple video format support
- Upload progress tracking
- Video library organization

### 🤖 AI-Powered Analysis

- Automatic video transcription
- AI-generated content summaries
- Intelligent question answering
- Chat interface for video content

### 🎨 Modern UI/UX

- Responsive design with Tailwind CSS
- Glass morphism effects
- Gradient backgrounds and animations
- Professional enterprise-grade interface

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Icons**: Lucide React
- **Backend**: FastAPI + Python
- **Database**: DynamoDB
- **Storage**: AWS S3
- **Cache**: AWS ElastiCache Memcached
- **Authentication**: AWS Cognito

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- Python 3.8+
- AWS Account with ElastiCache, DynamoDB, S3, and Cognito access

### Environment Configuration

The application requires the following environment variables to be configured:

#### AWS Services

- `AWS_REGION`: AWS region (default: ap-southeast-2)
- `S3_BUCKET`: S3 bucket name for video storage
- `DDB_VIDEOS_TABLE`: DynamoDB table name for video metadata
- `COGNITO_USER_POOL_ID`: AWS Cognito User Pool ID
- `COGNITO_APP_CLIENT_ID`: AWS Cognito App Client ID

#### ElastiCache Memcached

- `ELASTICACHE_MEMCACHED_ENDPOINT`: ElastiCache cluster endpoint
- `ELASTICACHE_MEMCACHED_TTL`: Cache TTL in seconds (default: 3600)

#### AI Services

- `OPENAI_API_KEY`: OpenAI API key for AI features

Copy `server/env.example` to `server/.env` and configure the values for your environment.

### Frontend Setup

```bash
cd client
npm install
npm run dev
```

### Build for Production

```bash
cd client
npm run build
```

## Demo Credentials

- **Email**: demo@example.com
- **Password**: password

## Development

The frontend application is located in the `client/` directory and contains all the React components, styling, and configuration files needed to run the video transcription application.

For detailed frontend documentation, see `client/README.md`.
