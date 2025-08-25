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

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

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
