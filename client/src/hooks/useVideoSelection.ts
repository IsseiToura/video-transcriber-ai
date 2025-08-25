import { useState } from "react";
import type { Video } from "../types/video";

export const useVideoSelection = () => {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  const selectVideo = (video: Video) => {
    setSelectedVideo(video);
    setShowUpload(false);
  };

  const showUploadForm = () => {
    setShowUpload(true);
    setSelectedVideo(null);
  };

  const hideUploadForm = () => {
    setShowUpload(false);
  };

  const handleUploadComplete = (newVideo: Video) => {
    setShowUpload(false);
    return newVideo;
  };

  return {
    selectedVideo,
    showUpload,
    selectVideo,
    showUploadForm,
    hideUploadForm,
    handleUploadComplete,
  };
};
