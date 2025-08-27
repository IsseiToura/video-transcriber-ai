import { API_CONFIG, apiRequestWithAuth } from "../config/api";
import type { VideoInfo, VideoUploadResponse, ProcessResponse } from "../types";

export class VideoService {
  /**
   * Upload video or audio file
   */
  async uploadVideo(file: File, token: string): Promise<VideoUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.UPLOAD,
      token,
      {
        method: "POST",
        body: formData,
        headers: {
          // Content-Type is automatically set for FormData
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Process video or audio file (transcription, summary)
   */
  async processVideo(videoId: string, token: string): Promise<ProcessResponse> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.PROCESS(videoId),
      token,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`Processing failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all videos
   */
  async getAllVideos(token: string): Promise<VideoInfo[]> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.LIST,
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get videos: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get video or audio file information
   */
  async getVideoInfo(videoId: string, token: string): Promise<VideoInfo> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.DETAIL(videoId),
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get video info: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get transcript
   */
  async getTranscript(videoId: string, token: string): Promise<string> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.TRANSCRIPT(videoId),
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get transcript: ${response.statusText}`);
    }

    return response.text();
  }

  /**
   * Get summary
   */
  async getSummary(videoId: string, token: string): Promise<string> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.SUMMARY(videoId),
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get summary: ${response.statusText}`);
    }

    const data = await response.json();
    return data.summary;
  }

  /**
   * Delete a video or audio file and its artifacts
   */
  async deleteVideo(videoId: string, token: string): Promise<void> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.DETAIL(videoId),
      token,
      {
        method: "DELETE",
      }
    );

    if (response.status === 204 || response.ok) {
      return;
    }

    throw new Error(`Failed to delete video: ${response.statusText}`);
  }
}
