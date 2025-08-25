import { Zap, Play, FileText } from "lucide-react";
import {
  type Video,
  VIDEO_STATUS,
  VIDEO_STATUS_LABELS,
  VIDEO_STATUS_STYLES,
} from "../types/video";

interface SidebarProps {
  videos: Video[];
  selectedVideo: Video | null;
  onVideoSelect: (video: Video) => void;
}

export const Sidebar = ({
  videos,
  selectedVideo,
  onVideoSelect,
}: SidebarProps) => {
  const getStatusIcon = (status: Video["status"]) => {
    switch (status) {
      case VIDEO_STATUS.COMPLETED:
        return (
          <div className="h-10 w-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
            <Play className="h-5 w-5 text-white" />
          </div>
        );
      case VIDEO_STATUS.PROCESSING:
        return (
          <div className="h-10 w-10 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          </div>
        );
      default:
        return (
          <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <FileText className="h-5 w-5 text-white" />
          </div>
        );
    }
  };

  return (
    <aside className="w-80 bg-white/80 backdrop-blur-lg border-r border-white/20 shadow-lg overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-6">
          <Zap className="h-5 w-5 text-yellow-500" />
          <h2 className="text-xl font-semibold text-gray-800">Video Library</h2>
        </div>

        <div className="space-y-3">
          {videos.map((video) => (
            <div
              key={video.id}
              onClick={() => onVideoSelect(video)}
              className={`p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                selectedVideo?.id === video.id
                  ? "bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 shadow-lg transform scale-105"
                  : "bg-white/60 hover:bg-white/80 border border-white/40 hover:shadow-md hover:scale-105"
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {getStatusIcon(video.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">
                    {video.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {video.uploadedAt.toLocaleDateString()}
                  </p>
                  <div className="flex items-center mt-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        VIDEO_STATUS_STYLES[video.status]
                      }`}
                    >
                      {VIDEO_STATUS_LABELS[video.status]}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
