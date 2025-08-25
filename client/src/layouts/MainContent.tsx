import type { Video } from "../types/video";
import VideoUpload from "../components/VideoUpload";
import VideoDetail from "../components/VideoDetail";
import VideoProcess from "../components/VideoProcess";

interface MainContentProps {
  selectedVideo: Video | null;
  onUploadComplete: (newVideo: Video) => void;
  onGenerateTranscript: (videoId: string) => void;
}

export const MainContent = ({
  selectedVideo,
  onUploadComplete,
  onGenerateTranscript,
}: MainContentProps) => {
  if (!selectedVideo) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="py-6 sm:py-8 lg:py-12">
            <VideoUpload onUploadComplete={onUploadComplete} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="py-6 sm:py-8 lg:py-12">
          {renderVideoContent(selectedVideo, onGenerateTranscript)}
        </div>
      </div>
    </div>
  );
};

const renderVideoContent = (
  video: Video,
  onGenerateTranscript: (videoId: string) => void
) => {
  if (video.status === "uploaded" || video.status === "processing") {
    return (
      <VideoProcess video={video} onGenerateTranscript={onGenerateTranscript} />
    );
  }

  return (
    <VideoDetail video={video} onGenerateTranscript={onGenerateTranscript} />
  );
};
