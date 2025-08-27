import type { VideoInfo } from "../types/video";
import VideoUpload from "../components/VideoUpload";
import VideoDetail from "../components/VideoDetail";
import VideoProcess from "../components/VideoProcess";

interface MainContentProps {
  selectedVideo: VideoInfo | null;
  onUploadComplete: (newVideo: VideoInfo) => void;
}

export const MainContent = ({
  selectedVideo,
  onUploadComplete,
}: MainContentProps) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="py-6 sm:py-8 lg:py-12">
          {renderContent(selectedVideo, onUploadComplete)}
        </div>
      </div>
    </div>
  );
};

const renderContent = (
  selectedVideo: VideoInfo | null,
  onUploadComplete: (newVideo: VideoInfo) => void
) => {
  if (
    selectedVideo &&
    (selectedVideo.status === "uploaded" ||
      selectedVideo.status === "processing")
  ) {
    return <VideoProcess video={selectedVideo} />;
  }

  if (selectedVideo && selectedVideo.status === "completed") {
    return <VideoDetail video={selectedVideo} />;
  }

  return <VideoUpload onUploadComplete={onUploadComplete} />;
};
