import { useState, useEffect } from "react";
import {
  MessageCircle,
  Send,
  FileVideo,
  AlertCircle,
  Bot,
  User,
} from "lucide-react";
import type { Video, Conversation } from "../types";

interface VideoChatProps {
  videoId: string | null;
}

const VideoChat = ({ videoId }: VideoChatProps) => {
  const [question, setQuestion] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);

  // Mock video data
  useEffect(() => {
    if (videoId) {
      const mockVideo: Video = {
        id: videoId,
        name: "Sample Video.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-15"),
        status: "completed",
        transcript:
          "This is a comprehensive transcript of the video content. It includes all the spoken words and can be quite lengthy depending on the video duration. The transcript serves as the basis for answering questions about the video content.",
        summary:
          "This video provides an in-depth overview of machine learning concepts, including supervised learning, unsupervised learning, and neural networks. It covers practical applications and real-world examples.",
      };
      setSelectedVideo(mockVideo);
    } else {
      setSelectedVideo(null);
    }
  }, [videoId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || !selectedVideo) return;

    const newConversation: Conversation = {
      id: Date.now().toString(),
      videoId: selectedVideo.id,
      question: question.trim(),
      answer: "",
      timestamp: new Date(),
    };

    setConversations((prev) => [...prev, newConversation]);
    setQuestion("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const mockAnswer = `Based on the video content about "${question.trim()}", here's what I can tell you: The video discusses various aspects of this topic, including key concepts and practical applications. The transcript contains relevant information that addresses your question. For more specific details, you might want to review the full transcript or ask a more targeted question.`;

      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === newConversation.id
            ? { ...conv, answer: mockAnswer }
            : conv
        )
      );
      setIsLoading(false);
    }, 2000);
  };

  if (!videoId) {
    return (
      <div className="text-center py-12">
        <MessageCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Video Selected
        </h3>
        <p className="text-gray-500">
          Please select a video from the Video Library to start chatting
        </p>
      </div>
    );
  }

  if (!selectedVideo) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-500">Loading video information...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Video Chat</h2>
        <p className="text-gray-600">Ask questions about your uploaded video</p>
      </div>

      {/* Video Info */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <FileVideo className="h-8 w-8 text-blue-600" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {selectedVideo.name}
            </h3>
            <p className="text-sm text-gray-500">
              Uploaded {selectedVideo.uploadedAt.toLocaleDateString()}
            </p>
          </div>
        </div>

        {selectedVideo.summary && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Video Summary
            </h4>
            <p className="text-sm text-gray-600">{selectedVideo.summary}</p>
          </div>
        )}
      </div>

      {/* Chat Interface */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Chat with AI</h3>
          <p className="text-sm text-gray-500">
            Ask questions about the video content and get AI-powered answers
          </p>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {conversations.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">
                Start a Conversation
              </h4>
              <p className="text-gray-500">
                Ask your first question about the video content
              </p>
            </div>
          ) : (
            conversations.map((conversation) => (
              <div key={conversation.id} className="space-y-3">
                {/* Question */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <User className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="bg-blue-50 rounded-lg p-3">
                      <p className="text-sm text-gray-900">
                        {conversation.question}
                      </p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {conversation.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>

                {/* Answer */}
                {conversation.answer ? (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-900">
                          {conversation.answer}
                        </p>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {conversation.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                          <span className="text-sm text-gray-500">
                            Thinking...
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-gray-600" />
                </div>
              </div>
              <div className="flex-1">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                    <span className="text-sm text-gray-500">
                      Processing your question...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <div className="p-4 border-t border-gray-200">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about the video content..."
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!question.trim() || isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900 mb-1">
              Tips for Better Questions
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>
                • Ask specific questions about concepts mentioned in the video
              </li>
              <li>• Request clarification on technical terms or processes</li>
              <li>• Ask for examples or practical applications</li>
              <li>• Request summaries of specific sections or topics</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoChat;
