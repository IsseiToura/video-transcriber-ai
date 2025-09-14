import { API_ENDPOINTS, apiRequestWithAuth } from "../config/api";
import type {
  VideoInfo,
  VideoUploadResponse,
  ProcessResponse,
  PresignedUrlResponse,
  VideoMetadataRequest,
} from "../types";

export class VideoService {
  /**
   * Upload video or audio file
   */
  async uploadVideo(
    file: File,
    token: string,
    onProgress?: (stage: string) => void
  ): Promise<VideoUploadResponse> {
    const presignResponse = await apiRequestWithAuth(
      `${API_ENDPOINTS.VIDEOS.PRESIGNED}?filename=${encodeURIComponent(
        file.name
      )}&content_type=${encodeURIComponent(file.type)}`,
      token,
      { method: "GET" }
    );

    if (!presignResponse.ok) {
      throw new Error(
        `Failed to get presigned URL: ${presignResponse.statusText}`
      );
    }

    const { uploadUrl, fileId, s3Key }: PresignedUrlResponse =
      (await presignResponse.json()) as PresignedUrlResponse;

    // Upload file to S3 using presigned URL
    onProgress?.("Uploading file...");
    const uploadResponse = await fetch(uploadUrl, {
      method: "PUT",
      body: file,
    });

    if (!uploadResponse.ok) {
      throw new Error(`S3 upload failed: ${uploadResponse.statusText}`);
    }

    const metadataResponse = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.METADATA,
      token,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileId,
          filename: file.name,
          s3Key,
        } as VideoMetadataRequest),
      }
    );

    if (!metadataResponse.ok) {
      throw new Error(
        `Failed to save metadata: ${metadataResponse.statusText}`
      );
    }

    onProgress?.("Upload completed!");
    return metadataResponse.json() as Promise<VideoUploadResponse>;
  }

  /**
   * Process video or audio file (transcription, summary)
   */
  async processVideo(videoId: string, token: string): Promise<ProcessResponse> {
    const response = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.PROCESS(videoId),
      token,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`Processing failed: ${response.statusText}`);
    }

    return response.json() as Promise<ProcessResponse>;
  }

  /**
   * Get all videos
   */
  async getAllVideos(token: string): Promise<VideoInfo[]> {
    const response = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.LIST,
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get videos: ${response.statusText}`);
    }

    return response.json() as Promise<VideoInfo[]>;
  }

  /**
   * Get video or audio file information
   */
  async getVideoInfo(videoId: string, token: string): Promise<VideoInfo> {
    const response = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.DETAIL(videoId),
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get video info: ${response.statusText}`);
    }

    return response.json() as Promise<VideoInfo>;
  }

  /**
   * Get transcript
   */
  async getTranscript(videoId: string, token: string): Promise<string> {
    const response = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.TRANSCRIPT(videoId),
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
      API_ENDPOINTS.VIDEOS.SUMMARY(videoId),
      token,
      {
        method: "GET",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get summary: ${response.statusText}`);
    }

    const data = (await response.json()) as { summary: string };
    return data.summary;
  }

  /**
   * Delete a video or audio file and its artifacts
   */
  async deleteVideo(videoId: string, token: string): Promise<void> {
    const response = await apiRequestWithAuth(
      API_ENDPOINTS.VIDEOS.DETAIL(videoId),
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
