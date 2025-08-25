import { useState } from "react";
import {
  FileVideo,
  Download,
  Send,
  Bot,
  User,
  Play,
  FileText,
  Sparkles,
  Zap,
  MessageCircle,
} from "lucide-react";
import type { Video } from "../types/video";
import type { Conversation } from "../types/common";

interface VideoDetailProps {
  video: Video;
  onGenerateTranscript: (videoId: string) => void;
}

const VideoDetail = ({ video, onGenerateTranscript }: VideoDetailProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateTranscript = () => {
    onGenerateTranscript(video.id);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const newConversation: Conversation = {
      id: Date.now().toString(),
      videoId: video.id,
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

  const downloadTranscript = () => {
    if (!video.transcript) return;

    const blob = new Blob([video.transcript], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${video.name.replace(/\.[^/.]+$/, "")}_transcript.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Video Header */}
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl">
        <div className="flex items-center space-x-6 mb-6">
          <div className="flex-shrink-0">
            {video.status === "completed" ? (
              <div className="h-16 w-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-2xl">
                <Play className="h-8 w-8 text-white" />
              </div>
            ) : video.status === "processing" ? (
              <div className="h-16 w-16 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-2xl">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              </div>
            ) : (
              <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl">
                <FileVideo className="h-8 w-8 text-white" />
              </div>
            )}
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {video.name}
            </h1>
            <p className="text-gray-500 text-lg">
              Uploaded {video.uploadedAt.toLocaleDateString()}
            </p>
            <div className="flex items-center mt-3">
              <span
                className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${
                  video.status === "completed"
                    ? "bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200"
                    : video.status === "processing"
                    ? "bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800 border border-yellow-200"
                    : "bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200"
                }`}
              >
                {video.status === "completed"
                  ? "Ready for Analysis"
                  : video.status === "processing"
                  ? "Processing"
                  : "Uploading"}
              </span>
            </div>
          </div>
          <div className="flex space-x-3">
            {video.status === "completed" && (
              <>
                <button
                  onClick={downloadTranscript}
                  className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-medium hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Transcript
                </button>
              </>
            )}
            {video.status === "uploading" && (
              <button
                onClick={handleGenerateTranscript}
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <FileText className="h-4 w-4 mr-2" />
                Generate Transcript
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Video Summary */}
      {video.status === "completed" && video.summary && (
        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="h-10 w-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              AI-Generated Summary
            </h2>
          </div>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200">
            <p className="text-gray-700 leading-relaxed text-lg">
              {video.summary}
            </p>
          </div>
        </div>
      )}

      {/* Transcript */}
      {video.status === "completed" && video.transcript && (
        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Full Transcript
            </h2>
          </div>
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200 max-h-96 overflow-y-auto">
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap text-lg">
              {video.transcript}
            </p>
          </div>
        </div>
      )}

      {/* Chat Interface */}
      {video.status === "completed" && (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-white/40 shadow-xl overflow-hidden">
          <div className="p-6 border-b border-white/40 bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                <MessageCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  AI Chat Assistant
                </h3>
                <p className="text-gray-600">
                  Ask questions about the video content and get intelligent
                  answers
                </p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-6 bg-gradient-to-br from-gray-50 to-blue-50">
            {conversations.length === 0 ? (
              <div className="text-center py-12">
                <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <h4 className="text-xl font-bold text-gray-900 mb-2">
                  Start a Conversation
                </h4>
                <p className="text-gray-600">
                  Ask your first question about the video content
                </p>
              </div>
            ) : (
              conversations.map((conversation) => (
                <div key={conversation.id} className="space-y-4">
                  {/* Question */}
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="bg-white p-4 rounded-2xl shadow-md border border-white/40">
                        <p className="text-gray-900 font-medium">
                          {conversation.question}
                        </p>
                      </div>
                      <p className="text-xs text-gray-500 mt-2 ml-2">
                        {conversation.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>

                  {/* Answer */}
                  {conversation.answer ? (
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-white p-4 rounded-2xl shadow-md border border-white/40">
                          <p className="text-gray-900">{conversation.answer}</p>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 ml-2">
                          {conversation.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="bg-white p-4 rounded-2xl shadow-md border border-white/40">
                          <div className="flex items-center space-x-3">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
                            <span className="text-gray-600 font-medium">
                              AI is thinking...
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
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-white p-4 rounded-2xl shadow-md border border-white/40">
                    <div className="flex items-center space-x-3">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
                      <span className="text-gray-600 font-medium">
                        Processing your question...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <div className="p-6 bg-white border-t border-white/40">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about the video content..."
                className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!question.trim() || isLoading}
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <Send className="h-5 w-5" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Processing State */}
      {video.status === "processing" && (
        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl text-center">
          <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">
            Generating Transcript
          </h3>
          <p className="text-gray-600 text-lg max-w-md mx-auto">
            Our AI is analyzing your video and creating a comprehensive
            transcript. This may take a few minutes...
          </p>
          <div className="flex items-center justify-center mt-6 space-x-4 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span>Processing Audio</span>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <span>AI Analysis</span>
            </div>
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-blue-500" />
              <span>Generating Summary</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoDetail;
