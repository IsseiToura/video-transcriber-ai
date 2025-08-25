import { API_CONFIG, apiRequestWithAuth } from "../config/api";
import type {
  VideoUploadResponse,
  ProcessResponse,
  VideoInfo,
  ChatRequest,
  ChatResponse,
} from "../types";

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

    const data = await response.json();
    return data.transcript;
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
   * Chat with video or audio file
   */
  async chatWithVideo(
    videoId: string,
    question: string,
    token: string
  ): Promise<ChatResponse> {
    const response = await apiRequestWithAuth(
      API_CONFIG.ENDPOINTS.VIDEOS.CHAT(videoId),
      token,
      {
        method: "POST",
        body: JSON.stringify({ question }),
      }
    );

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  }
}
