import type { VideoInfo } from "../../types/video";
import { VIDEO_STATUS } from "../../types/video";
import VideoUpload from "../video/VideoUpload";
import VideoDetail from "../video/VideoDetail";
import VideoProcess from "../video/VideoProcess";

interface MainContentProps {
  selectedVideo: VideoInfo | null;
  onUploadComplete: (newVideo: VideoInfo) => void;
}

// Helper function to render appropriate content based on video status
const getContentByStatus = (
  selectedVideo: VideoInfo | null,
  onUploadComplete: (newVideo: VideoInfo) => void
) => {
  // No video selected - show upload form
  if (!selectedVideo) {
    return <VideoUpload onUploadComplete={onUploadComplete} />;
  }

  // Video is uploaded or processing - show process view
  if ( selectedVideo.status === VIDEO_STATUS.UPLOADED || selectedVideo.status === VIDEO_STATUS.PROCESSING) {
    return <VideoProcess video={selectedVideo} />;
  }

  // Video is completed - show detail view
  if (selectedVideo.status === VIDEO_STATUS.COMPLETED) {
    return <VideoDetail video={selectedVideo} />;
  }

  // Default - show upload form
  return <VideoUpload onUploadComplete={onUploadComplete} />;
};

const MainContent = ({
  selectedVideo,
  onUploadComplete,
}: MainContentProps) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="py-6 sm:py-8 lg:py-12">
          {getContentByStatus(selectedVideo, onUploadComplete)}
        </div>
      </div>
    </div>
  );
};

export default MainContent;
