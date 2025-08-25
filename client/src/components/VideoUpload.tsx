import { useState, useRef } from "react";
import {
  Upload,
  FileVideo,
  X,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Zap,
} from "lucide-react";
import type { Video } from "../types";
import { VideoService } from "../services";
import { useAuth } from "../contexts/AuthContext";

interface VideoUploadProps {
  onUploadComplete: (video: Video) => void;
}

const VideoUpload = ({ onUploadComplete }: VideoUploadProps) => {
  const { user } = useAuth();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedVideos, setUploadedVideos] = useState<Video[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach((file) => {
      if (file.type.startsWith("video/") || file.type.startsWith("audio/")) {
        uploadVideo(file);
      }
    });
  };

  const uploadVideo = async (file: File) => {
    if (!user?.access_token) {
      console.error("No authentication token available");
      return;
    }

    const video: Video = {
      id: Date.now().toString(),
      name: file.name,
      url: URL.createObjectURL(file),
      uploadedAt: new Date(),
      status: "uploading",
    };

    setUploadedVideos((prev) => [...prev, video]);
    setIsUploading(true);

    try {
      // Use VideoService for upload
      const videoService = new VideoService();
      const result = await videoService.uploadVideo(file, user.access_token);

      // Update video with server response - mark as uploaded, not processing
      const uploadedVideo = {
        ...video,
        id: result.video_id,
        status: "uploaded" as const,
      };

      setUploadedVideos((prev) =>
        prev.map((v) => (v.id === video.id ? uploadedVideo : v))
      );

      // Notify parent component that upload is complete
      onUploadComplete(uploadedVideo);
    } catch (error) {
      console.error("Upload error:", error);

      const errorVideo = {
        ...video,
        status: "error" as const,
      };

      setUploadedVideos((prev) =>
        prev.map((v) => (v.id === video.id ? errorVideo : v))
      );
    } finally {
      setIsUploading(false);
    }
  };

  const removeVideo = (id: string) => {
    setUploadedVideos((prev) => prev.filter((v) => v.id !== id));
  };

  const getStatusIcon = (status: Video["status"]) => {
    switch (status) {
      case "uploading":
        return (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
        );
      case "uploaded":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: Video["status"]) => {
    switch (status) {
      case "uploading":
        return "Uploading...";
      case "uploaded":
        return "Uploaded";
      case "error":
        return "Error";
      default:
        return "";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full mb-4 shadow-lg">
          <Sparkles className="h-5 w-5" />
          <span className="font-semibold">AI-Powered Video Analysis</span>
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Upload Your Video or Audio
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Transform your videos and audio files into intelligent insights with
          our advanced AI transcription and analysis technology
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ${
          dragActive
            ? "border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50 shadow-2xl scale-105"
            : "border-gray-300 bg-white/80 backdrop-blur-sm hover:border-blue-400 hover:shadow-xl"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="video/*,audio/*"
          onChange={handleFileInput}
          className="hidden"
        />

        <div className="space-y-6">
          <div className="mx-auto h-20 w-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl">
            <FileVideo className="h-10 w-10 text-white" />
          </div>

          <div>
            <div className="text-2xl font-bold text-gray-900 mb-2">
              Drop your video or audio files here
            </div>
            <p className="text-lg text-gray-500 mb-6">
              or click to browse files
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-blue-500/30 transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              <Upload className="h-5 w-5 mr-3" />
              Choose Files
            </button>
          </div>

          {/* Features */}
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span>Fast Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <span>AI Powered</span>
            </div>
            <div className="flex items-center space-x-2">
              <FileVideo className="h-4 w-4 text-blue-500" />
              <span>Multiple Formats</span>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Videos List */}
      {uploadedVideos.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-6">
            Upload Progress
          </h3>
          <div className="grid gap-6">
            {uploadedVideos.map((video) => (
              <div
                key={video.id}
                className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-white/40 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                      <FileVideo className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-gray-900">
                        {video.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        Uploaded {video.uploadedAt.toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(video.status)}
                      <span className="text-sm font-medium text-gray-600">
                        {getStatusText(video.status)}
                      </span>
                    </div>
                    <button
                      onClick={() => removeVideo(video.id)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors duration-200"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoUpload;
