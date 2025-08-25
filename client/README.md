# Video Transcriber

A modern web application built with React, TypeScript, and Vite for video transcription, analysis, and AI-powered conversations.

## Features

### 🎥 Video Upload

- Drag and drop video file uploads
- Support for multiple video formats
- Real-time upload progress tracking
- File validation and error handling

### 📝 Transcription & Summary

- Automatic video transcription processing
- AI-generated content summaries
- Downloadable transcript files
- Processing status indicators

### 💬 AI Video Chat

- Ask questions about video content
- AI-powered responses based on transcripts
- Real-time conversation interface
- Context-aware answers

### 📚 Video Library

- Organized video management
- Status tracking (uploading, processing, completed)
- Quick access to transcripts and summaries
- Video selection for chat sessions

### 📖 Conversation History

- Complete chat history tracking
- Search and filter conversations
- Statistics and analytics
- Expandable conversation views

## Technology Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React Hooks
- **UI Components**: Custom components with Tailwind

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd VideoTransraper
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── VideoUpload.tsx     # Video upload interface
│   ├── VideoList.tsx       # Video library display
│   ├── VideoChat.tsx       # AI chat interface
│   └── ConversationHistory.tsx # Chat history
├── types/              # TypeScript type definitions
│   └── index.ts
├── App.tsx            # Main application component
├── main.tsx           # Application entry point
└── index.css          # Global styles and Tailwind
```

## Usage

### 1. Upload Videos

- Navigate to the "Upload Video" tab
- Drag and drop video files or click to browse
- Monitor upload and processing progress

### 2. View Video Library

- Go to "Video Library" to see all uploaded videos
- Click on videos to select them for chat
- Download transcripts and view summaries

### 3. Chat with Videos

- Select a video from the library
- Go to "Video Chat" tab
- Ask questions about the video content
- Receive AI-generated answers

### 4. Review History

- Visit "Conversation History" to see all chats
- Search and filter conversations
- View statistics and analytics

## Features in Detail

### Video Processing Pipeline

1. **Upload**: File validation and upload initiation
2. **Processing**: Video transcription and analysis
3. **Completion**: Transcript generation and summary creation
4. **Ready**: Available for chat and download

### AI Chat System

- Context-aware responses based on video transcripts
- Natural language question processing
- Intelligent answer generation
- Conversation memory and history

### Data Management

- Local state management with React hooks
- Mock data for demonstration purposes
- Extensible architecture for backend integration

## Customization

### Styling

The application uses Tailwind CSS for styling. Customize the design by:

- Modifying `tailwind.config.js`
- Adding custom CSS in `src/index.css`
- Updating component classes

### Adding New Features

- Create new components in `src/components/`
- Add new types in `src/types/index.ts`
- Update the main App component for navigation

## Future Enhancements

- [ ] Backend API integration
- [ ] Real video transcription service
- [ ] User authentication and accounts
- [ ] Video playback integration
- [ ] Advanced AI features
- [ ] Export and sharing capabilities
- [ ] Mobile responsive design improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions and support, please open an issue in the repository.
