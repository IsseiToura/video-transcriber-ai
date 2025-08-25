import { useState, useEffect } from "react";
import {
  History,
  MessageCircle,
  FileVideo,
  Calendar,
  Clock,
  Search,
  Filter,
} from "lucide-react";
import type { Video, Conversation } from "../types";

const ConversationHistory = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedVideoFilter, setSelectedVideoFilter] = useState<string>("all");
  const [expandedConversations, setExpandedConversations] = useState<
    Set<string>
  >(new Set());

  // Mock data for demonstration
  useEffect(() => {
    const mockVideos: Video[] = [
      {
        id: "1",
        name: "Machine Learning Basics.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-15"),
        status: "completed",
        transcript: "Sample transcript for machine learning video",
        summary: "Introduction to machine learning concepts",
      },
      {
        id: "2",
        name: "Data Science Fundamentals.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-20"),
        status: "completed",
        transcript: "Sample transcript for data science video",
        summary: "Overview of data science methodologies",
      },
    ];

    const mockConversations: Conversation[] = [
      {
        id: "1",
        videoId: "1",
        question: "What is supervised learning?",
        answer:
          "Supervised learning is a type of machine learning where the algorithm learns from labeled training data. It involves learning a mapping from input variables to output variables based on example input-output pairs.",
        timestamp: new Date("2024-01-15T10:30:00"),
      },
      {
        id: "2",
        videoId: "1",
        question: "Can you explain neural networks?",
        answer:
          "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information and can learn complex patterns through training.",
        timestamp: new Date("2024-01-15T11:15:00"),
      },
      {
        id: "3",
        videoId: "2",
        question: "What is data preprocessing?",
        answer:
          "Data preprocessing is the process of cleaning and transforming raw data into a format that is suitable for analysis. This includes handling missing values, normalizing data, and encoding categorical variables.",
        timestamp: new Date("2024-01-20T14:20:00"),
      },
      {
        id: "4",
        videoId: "2",
        question: "How do you handle outliers in data?",
        answer:
          "Outliers can be handled through various methods including statistical methods (z-score, IQR), visualization techniques, and domain knowledge. The approach depends on the nature of the data and the analysis goals.",
        timestamp: new Date("2024-01-20T15:45:00"),
      },
    ];

    setVideos(mockVideos);
    setConversations(mockConversations);
  }, []);

  const toggleExpanded = (conversationId: string) => {
    const newExpanded = new Set(expandedConversations);
    if (newExpanded.has(conversationId)) {
      newExpanded.delete(conversationId);
    } else {
      newExpanded.add(conversationId);
    }
    setExpandedConversations(newExpanded);
  };

  const filteredConversations = conversations.filter((conversation) => {
    const matchesSearch =
      conversation.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conversation.answer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesVideo =
      selectedVideoFilter === "all" ||
      conversation.videoId === selectedVideoFilter;
    return matchesSearch && matchesVideo;
  });

  const getVideoName = (videoId: string) => {
    return videos.find((v) => v.id === videoId)?.name || "Unknown Video";
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - timestamp.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 24) {
      return `${diffInHours} hours ago`;
    } else {
      return timestamp.toLocaleDateString();
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Conversation History
        </h2>
        <p className="text-gray-600">
          Review all your conversations about uploaded videos
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label
              htmlFor="search"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Search Conversations
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                id="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search questions and answers..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Video Filter */}
          <div>
            <label
              htmlFor="video-filter"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Filter by Video
            </label>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                id="video-filter"
                value={selectedVideoFilter}
                onChange={(e) => setSelectedVideoFilter(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Videos</option>
                {videos.map((video) => (
                  <option key={video.id} value={video.id}>
                    {video.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm text-center">
          <MessageCircle className="h-8 w-8 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {conversations.length}
          </div>
          <div className="text-sm text-gray-600">Total Conversations</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm text-center">
          <FileVideo className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {videos.length}
          </div>
          <div className="text-sm text-gray-600">Videos Discussed</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm text-center">
          <Clock className="h-8 w-8 text-purple-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {conversations.length > 0
              ? Math.round(
                  conversations.reduce(
                    (acc, conv) => acc + conv.answer.length,
                    0
                  ) / 100
                )
              : 0}
          </div>
          <div className="text-sm text-gray-600">Total Words Generated</div>
        </div>
      </div>

      {/* Conversations List */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">
          Conversations ({filteredConversations.length})
        </h3>

        {filteredConversations.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <History className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              No conversations found
            </h4>
            <p className="text-gray-500">
              {searchTerm || selectedVideoFilter !== "all"
                ? "Try adjusting your search or filters"
                : "Start chatting with your videos to see conversation history here"}
            </p>
          </div>
        ) : (
          filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
            >
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <FileVideo className="h-5 w-5 text-blue-600" />
                    <span className="text-sm font-medium text-gray-900">
                      {getVideoName(conversation.videoId)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Calendar className="h-4 w-4" />
                    <span>{formatTimestamp(conversation.timestamp)}</span>
                  </div>
                </div>

                <div className="space-y-3">
                  {/* Question */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      Question:
                    </h4>
                    <p className="text-sm text-gray-700">
                      {conversation.question}
                    </p>
                  </div>

                  {/* Answer */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      Answer:
                    </h4>
                    <div className="relative">
                      <p
                        className={`text-sm text-gray-700 ${
                          !expandedConversations.has(conversation.id)
                            ? "line-clamp-3"
                            : ""
                        }`}
                      >
                        {conversation.answer}
                      </p>
                      {conversation.answer.length > 150 && (
                        <button
                          onClick={() => toggleExpanded(conversation.id)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-1"
                        >
                          {expandedConversations.has(conversation.id)
                            ? "Show less"
                            : "Show more"}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationHistory;
