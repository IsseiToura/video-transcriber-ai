import { Zap, Play, FileText, Trash2 } from "lucide-react";
import { useEffect, useState, useMemo } from "react";
import {
  type VideoInfo,
  VIDEO_STATUS,
  VIDEO_STATUS_LABELS,
  VIDEO_STATUS_STYLES,
} from "../../types/video";
import { useAuth } from "../../contexts/AuthContext";
import { VideoService } from "../../services";
import { toast } from "react-hot-toast";

interface SidebarProps {
  videos: VideoInfo[];
  selectedVideo: VideoInfo | null;
  onVideoSelect: (video: VideoInfo) => void;
  onVideoDeleted?: (videoId: string) => void;
}

// Helper function to get status icon based on video status
const getStatusIcon = (status: VideoInfo["status"]) => {
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

const Sidebar = ({
  videos,
  selectedVideo,
  onVideoSelect,
  onVideoDeleted,
}: SidebarProps) => {
  const { user } = useAuth();
  const videoService = useMemo(() => new VideoService(), []);
  const [displayVideos, setDisplayVideos] = useState<VideoInfo[]>(videos);

  useEffect(() => {
    setDisplayVideos(videos);
  }, [videos]);

  const handleSelect = async (video: VideoInfo) => {
    // Fetch latest info before selecting so status/summary are up to date
    if (!user?.access_token) {
      onVideoSelect(video);
      return;
    }
    try {
      const latest = await videoService.getVideoInfo(
        video.video_id,
        user.access_token
      );
      onVideoSelect(latest);
    } catch (e) {
      // Fall back to the item from the list if fetching detail fails
      onVideoSelect(video);
    }
  };

  const handleDelete = async (
    e: React.MouseEvent<HTMLButtonElement>,
    videoId: string
  ) => {
    e.stopPropagation();
    if (!user?.access_token) return;
    try {
      await videoService.deleteVideo(videoId, user.access_token);
      // Optimistically remove from local list so UI reflects deletion immediately
      setDisplayVideos((prev) => prev.filter((v) => v.video_id !== videoId));
      onVideoDeleted?.(videoId);
      toast.success("Deleted successfully.");
    } catch (err) {
      // eslint-disable-next-line no-alert
      alert("Failed to delete");
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
          {displayVideos.map((video) => (
            <div
              key={video.video_id}
              onClick={() => handleSelect(video)}
              className={`p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                selectedVideo?.video_id === video.video_id
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
                    {video.filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(video.created_at).toLocaleDateString()}
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
                <div>
                  <button
                    onClick={(e) => handleDelete(e, video.video_id)}
                    className="p-2 rounded-md text-gray-500 hover:text-red-600 hover:bg-red-50"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
