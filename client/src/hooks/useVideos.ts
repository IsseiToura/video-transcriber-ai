import { useState, useEffect } from "react";
import type { Video } from "../types/video";
import { mockVideos } from "../data/mockVideos";

export const useVideos = () => {
  const [videos, setVideos] = useState<Video[]>([]);

  useEffect(() => {
    setVideos(mockVideos);
  }, []);

  const addVideo = (newVideo: Video) => {
    setVideos((prev) => [...prev, newVideo]);
  };

  const updateVideoStatus = (videoId: string, status: Video["status"]) => {
    setVideos((prev) =>
      prev.map((v) => (v.id === videoId ? { ...v, status } : v))
    );
  };

  const updateVideoTranscript = (
    videoId: string,
    transcript: string,
    summary: string
  ) => {
    setVideos((prev) =>
      prev.map((v) =>
        v.id === videoId
          ? { ...v, transcript, summary, status: "completed" }
          : v
      )
    );
  };

  const handleTranscriptGeneration = async (videoId: string) => {
    // Simulate transcript generation
    updateVideoStatus(videoId, "processing");

    setTimeout(() => {
      updateVideoTranscript(
        videoId,
        "This is a generated transcript for the video content. It contains all the spoken words and can be used for analysis and question answering.",
        "This is an AI-generated summary of the video content, highlighting key points and main concepts discussed."
      );
    }, 3000);
  };

  return {
    videos,
    addVideo,
    updateVideoStatus,
    updateVideoTranscript,
    handleTranscriptGeneration,
  };
};
