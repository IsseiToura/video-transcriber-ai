import { useEffect, useState, useRef } from "react";
import { Sparkles, Zap, FileText } from "lucide-react";
import type { VideoInfo } from "../types/video";
import VideoDetail from "./VideoDetail";
import { VideoService } from "../services";
import { useAuth } from "../contexts/AuthContext";
import toast from "react-hot-toast";

interface VideoProcessProps {
  video: VideoInfo;
}

const VideoProcess = ({ video }: VideoProcessProps) => {
  const { user } = useAuth();
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCompleted, setIsCompleted] = useState(video.status === "completed");
  const [processedVideo, setProcessedVideo] = useState<VideoInfo | null>(
    video.status === "completed" ? video : video
  );
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const completed = video.status === "completed";
    setIsProcessing(false);
    setIsCompleted(completed);
    setProcessedVideo(video); // Always set the current video state
  }, [video.video_id, video.status]);

  // Polling for status updates when video is processing
  useEffect(() => {
    const startPolling = () => {
      // Start polling if video is processing or uploaded (waiting for Lambda to start processing)
      if (
        (processedVideo?.status === "processing" ||
          processedVideo?.status === "uploaded") &&
        user?.access_token
      ) {
        pollingIntervalRef.current = setInterval(async () => {
          try {
            const videoService = new VideoService();
            const videoInfo = await videoService.getVideoInfo(
              processedVideo.video_id,
              user.access_token
            );

            // Update the processed video with latest info
            setProcessedVideo(videoInfo);

            if (videoInfo.status === "completed") {
              setIsCompleted(true);
              clearInterval(pollingIntervalRef.current!);
              pollingIntervalRef.current = null;
              toast.success("Video processing completed automatically!");
            } else if (videoInfo.status === "error") {
              setIsProcessing(false);
              clearInterval(pollingIntervalRef.current!);
              pollingIntervalRef.current = null;
              toast.error("Video processing failed");
            }
          } catch (error) {
            console.error("Error polling video status:", error);
          }
        }, 3000); // Poll every 3 seconds
      }
    };

    startPolling();

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [processedVideo?.status, processedVideo?.video_id, user?.access_token]);

  if (isCompleted && processedVideo) {
    return <VideoDetail video={processedVideo} />;
  }

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      {/* Video Header */}
      <div className="bg-white/80 backdrop-blur-sm p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl border border-white/40 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-6 space-y-4 sm:space-y-0 mb-4 sm:mb-6">
          <div className="flex-shrink-0 flex justify-center sm:justify-start">
            <div className="h-12 w-12 sm:h-16 sm:w-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-2xl">
              <FileText className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
            </div>
          </div>
          <div className="flex-1 text-center sm:text-left">
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-2">
              {video.filename}
            </h1>
            <p className="text-sm sm:text-base lg:text-lg text-gray-500">
              Uploaded {new Date(video.created_at).toLocaleDateString()}
            </p>
            <div className="flex justify-center sm:justify-start mt-3">
              <span
                className={`inline-flex items-center px-2 py-1 sm:px-3 sm:py-1.5 rounded-full text-xs sm:text-sm font-medium ${
                  processedVideo?.status === "processing"
                    ? "bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800 border border-yellow-200"
                    : "bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200"
                }`}
              >
                {processedVideo?.status === "processing"
                  ? "Processing in Progress"
                  : "Processing Will Start Automatically"}
              </span>
            </div>
          </div>
        </div>
        <div className="flex justify-center sm:justify-end mt-4">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">
              Processing will start automatically after upload
            </p>
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 rounded-lg border border-green-200">
              <Sparkles className="h-4 w-4 mr-2" />
              Auto-processing enabled
            </div>
          </div>
        </div>
      </div>

      {/* Processing State */}
      {(isProcessing ||
        processedVideo?.status === "processing" ||
        (processedVideo?.status === "uploaded" && !isCompleted)) && (
        <div className="bg-white/80 backdrop-blur-sm p-4 sm:p-6 lg:p-8 rounded-xl sm:rounded-2xl border border-white/40 shadow-xl text-center">
          <div className="h-12 w-12 sm:h-16 sm:w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-2xl">
            <div className="animate-spin rounded-full h-6 w-6 sm:h-8 sm:w-8 border-b-2 border-white"></div>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3">
            {processedVideo?.status === "processing"
              ? "Processing Your Video"
              : "Waiting for Processing to Start"}
          </h3>
          <p className="text-sm sm:text-base lg:text-lg text-gray-600 max-w-md mx-auto mb-4 sm:mb-6 px-4">
            {processedVideo?.status === "processing"
              ? "Our AI is analyzing your video and creating a comprehensive transcript. This may take a few minutes..."
              : "Your video has been uploaded successfully. Processing will start automatically via Lambda function..."}
          </p>

          {/* Processing Steps */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6 max-w-4xl mx-auto px-4">
            <div className="flex items-center space-x-3 p-3 sm:p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg sm:rounded-xl border border-blue-200">
              <div className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Zap className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
              </div>
              <div className="text-left min-w-0">
                <div className="font-semibold text-blue-800 text-sm sm:text-base">
                  Audio Processing
                </div>
                <div className="text-xs sm:text-sm text-blue-600">
                  Extracting audio
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 sm:p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg sm:rounded-xl border border-purple-200">
              <div className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
              </div>
              <div className="text-left min-w-0">
                <div className="font-semibold text-purple-800 text-sm sm:text-base">
                  AI Analysis
                </div>
                <div className="text-xs sm:text-sm text-purple-600">
                  Transcribing content
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 sm:p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg sm:rounded-xl border border-green-200 sm:col-span-2 lg:col-span-1">
              <div className="h-6 w-6 sm:h-8 sm:w-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center flex-shrink-0">
                <FileText className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
              </div>
              <div className="text-left min-w-0">
                <div className="font-semibold text-green-800 text-sm sm:text-base">
                  Summary
                </div>
                <div className="text-xs sm:text-sm text-green-600">
                  Generating insights
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoProcess;
