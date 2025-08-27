import { useState, useEffect } from "react";
import { VideoService } from "../services/videoService";
import { useAuth } from "../contexts/AuthContext";
import type { VideoInfo } from "../types/video";

export const useVideos = () => {
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const videoService = new VideoService();

  // Fetch videos from server
  const fetchVideos = async () => {
    if (!user?.access_token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const fetchedVideos = await videoService.getAllVideos(user.access_token);
      setVideos(fetchedVideos);
    } catch (err) {
      console.error("Error fetching videos:", err);
      setError("Failed to fetch videos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, [user?.access_token]);

  const addVideo = (newVideo: VideoInfo) => {
    setVideos((prev) => [...prev, newVideo]);
  };

  const updateVideoStatus = (videoId: string, status: VideoInfo["status"]) => {
    setVideos((prev) =>
      prev.map((v) => (v.video_id === videoId ? { ...v, status } : v))
    );
  };

  const removeVideo = (videoId: string) => {
    setVideos((prev) => prev.filter((v) => v.video_id !== videoId));
  };

  const refreshVideos = () => {
    fetchVideos();
  };

  return {
    videos,
    loading,
    error,
    addVideo,
    updateVideoStatus,
    removeVideo,
    refreshVideos,
  };
};
