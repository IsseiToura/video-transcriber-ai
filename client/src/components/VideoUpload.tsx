import { useState, useRef } from "react";
import { Upload, FileVideo, Sparkles, Zap } from "lucide-react";
import type { VideoInfo } from "../types/video";
import { VideoService } from "../services";
import { useAuth } from "../contexts/AuthContext";
import toast from "react-hot-toast";

interface VideoUploadProps {
  onUploadComplete: (video: VideoInfo) => void;
}

const VideoUpload = ({ onUploadComplete }: VideoUploadProps) => {
  const { user } = useAuth();
  const [dragActive, setDragActive] = useState(false);
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

    const video: VideoInfo = {
      video_id: Date.now().toString(),
      filename: file.name,
      created_at: new Date().toISOString(),
      status: "uploading",
    };

    // Show initial uploading toast
    const uploadingToast = toast.loading("Starting upload...");

    try {
      // Use VideoService for upload with progress callback
      const videoService = new VideoService();
      const result = await videoService.uploadVideo(
        file,
        user.access_token,
        (stage: string) => {
          // Update the loading toast with current stage
          toast.loading(stage, { id: uploadingToast });
        }
      );

      // Update video with server response - mark as uploaded
      const uploadedVideo = {
        ...video,
        video_id: result.video_id,
        status: "uploaded" as const,
      };

      // Notify parent component that upload is complete (this will also select the video)
      onUploadComplete(uploadedVideo);

      // Dismiss loading toast and show success toast
      toast.dismiss(uploadingToast);
      toast.success(
        "Video uploaded successfully! Processing will start automatically..."
      );
    } catch (error) {
      console.error("Upload error:", error);
      // Dismiss loading toast and show error toast
      toast.dismiss(uploadingToast);
      toast.error(
        `Upload failed: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
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
              <span>Auto Processing</span>
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
    </div>
  );
};

export default VideoUpload;
