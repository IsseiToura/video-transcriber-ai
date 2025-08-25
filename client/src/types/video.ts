// Video related types based on server schemas
export interface VideoUploadResponse {
  video_id: string;
  filename: string;
  message: string;
}

export interface VideoInfo {
  video_id: string;
  filename: string;
  summary?: string;
  transcript?: string;
  created_at: string; // ISO string format from server
  processed: boolean;
}

export interface ProcessResponse {
  message: string;
  video_id: string;
  status: string;
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources?: any; // In a full implementation, this would include source references
}

// Additional types for video management
export interface Video {
  id: string;
  name: string;
  url: string;
  uploadedAt: Date;
  status: "uploading" | "uploaded" | "processing" | "completed" | "error";
  transcript?: string;
  summary?: string;
}

export const VIDEO_STATUS = {
  UPLOADING: "uploading",
  UPLOADED: "uploaded",
  PROCESSING: "processing",
  COMPLETED: "completed",
  ERROR: "error",
} as const;

export const VIDEO_STATUS_LABELS = {
  [VIDEO_STATUS.UPLOADING]: "Uploading",
  [VIDEO_STATUS.UPLOADED]: "Uploaded",
  [VIDEO_STATUS.PROCESSING]: "Processing",
  [VIDEO_STATUS.COMPLETED]: "Ready",
  [VIDEO_STATUS.ERROR]: "Error",
} as const;

export const VIDEO_STATUS_STYLES = {
  [VIDEO_STATUS.UPLOADING]:
    "bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200",
  [VIDEO_STATUS.UPLOADED]:
    "bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200",
  [VIDEO_STATUS.PROCESSING]:
    "bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800 border border-yellow-200",
  [VIDEO_STATUS.COMPLETED]:
    "bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200",
  [VIDEO_STATUS.ERROR]:
    "bg-gradient-to-r from-red-100 to-pink-100 text-red-800 border border-red-200",
} as const;
