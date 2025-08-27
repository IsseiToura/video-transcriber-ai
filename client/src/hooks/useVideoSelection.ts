import { useState } from "react";
import type { VideoInfo } from "../types/video";

export const useVideoSelection = () => {
  const [selectedVideo, setSelectedVideo] = useState<VideoInfo | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  const selectVideo = (video: VideoInfo) => {
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

  const handleUploadComplete = (newVideo: VideoInfo) => {
    setShowUpload(false);
    setSelectedVideo(newVideo);
    return newVideo;
  };

  const clearSelection = () => {
    setSelectedVideo(null);
  };

  return {
    selectedVideo,
    showUpload,
    selectVideo,
    showUploadForm,
    hideUploadForm,
    handleUploadComplete,
    clearSelection,
  };
};
