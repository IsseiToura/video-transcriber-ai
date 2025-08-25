import { useState, useEffect } from "react";
import {
  FileVideo,
  Download,
  Eye,
  MessageCircle,
  Calendar,
  Clock,
} from "lucide-react";
import type { Video } from "../types";

interface VideoListProps {
  onVideoSelect: (videoId: string | null) => void;
}

const VideoList = ({ onVideoSelect }: VideoListProps) => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    const mockVideos: Video[] = [
      {
        id: "1",
        name: "Sample Video 1.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-15"),
        status: "completed",
        transcript:
          "This is a sample transcript for the first video. It contains the spoken content and can be quite long depending on the video length.",
        summary:
          "This video discusses the basics of machine learning and artificial intelligence, covering key concepts and practical applications.",
      },
      {
        id: "2",
        name: "Sample Video 2.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-20"),
        status: "completed",
        transcript:
          "Another sample transcript for the second video. This demonstrates how transcripts are displayed in the interface.",
        summary:
          "A comprehensive overview of data science methodologies, including data collection, analysis, and visualization techniques.",
      },
      {
        id: "3",
        name: "Sample Video 3.mp4",
        url: "#",
        uploadedAt: new Date("2024-01-25"),
        status: "processing",
      },
    ];
    setVideos(mockVideos);
  }, []);

  const handleVideoSelect = (videoId: string) => {
    setSelectedVideo(videoId);
    onVideoSelect(videoId);
  };

  const downloadTranscript = (video: Video) => {
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

  const getStatusBadge = (status: Video["status"]) => {
    const statusConfig = {
      uploading: { color: "bg-blue-100 text-blue-800", text: "Uploading" },
      processing: {
        color: "bg-yellow-100 text-yellow-800",
        text: "Processing",
      },
      completed: { color: "bg-green-100 text-green-800", text: "Completed" },
      error: { color: "bg-red-100 text-red-800", text: "Error" },
    };

    const config = statusConfig[status];
    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        {config.text}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Video Library</h2>
        <p className="text-gray-600">View and manage your uploaded videos</p>
      </div>

      {videos.length === 0 ? (
        <div className="text-center py-12">
          <FileVideo className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No videos yet
          </h3>
          <p className="text-gray-500">
            Upload your first video to get started
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id}
              className={`bg-white rounded-lg border shadow-sm cursor-pointer transition-all hover:shadow-md ${
                selectedVideo === video.id
                  ? "ring-2 ring-blue-500 border-blue-500"
                  : "border-gray-200"
              }`}
              onClick={() => handleVideoSelect(video.id)}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <FileVideo className="h-8 w-8 text-gray-400 flex-shrink-0" />
                  {getStatusBadge(video.status)}
                </div>

                <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
                  {video.name}
                </h3>

                <div className="flex items-center text-sm text-gray-500 mb-3">
                  <Calendar className="h-4 w-4 mr-1" />
                  {video.uploadedAt.toLocaleDateString()}
                </div>

                {video.status === "completed" &&
                  video.transcript &&
                  video.summary && (
                    <div className="space-y-3 mb-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">
                          Summary
                        </h4>
                        <p className="text-sm text-gray-600 line-clamp-3">
                          {video.summary}
                        </p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">
                          Transcript Preview
                        </h4>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {video.transcript}
                        </p>
                      </div>
                    </div>
                  )}

                <div className="flex space-x-2">
                  {video.status === "completed" && (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadTranscript(video);
                        }}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleVideoSelect(video.id);
                        }}
                        className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Chat
                      </button>
                    </>
                  )}
                  {video.status === "processing" && (
                    <div className="flex-1 flex items-center justify-center text-sm text-gray-500">
                      <Clock className="h-4 w-4 mr-2 animate-pulse" />
                      Processing...
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedVideo && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">
                Selected: {videos.find((v) => v.id === selectedVideo)?.name}
              </span>
            </div>
            <button
              onClick={() => {
                setSelectedVideo(null);
                onVideoSelect(null);
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoList;
