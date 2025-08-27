import { Download, Play, Sparkles } from "lucide-react";
import type { VideoInfo } from "../types";
import { useAuth } from "../contexts/AuthContext";
import { VideoService } from "../services";

interface VideoDetailProps {
  video: VideoInfo;
}

const VideoDetail = ({ video }: VideoDetailProps) => {
  const { user } = useAuth();
  const videoService = new VideoService();

  const downloadTranscript = async () => {
    if (!user?.access_token) return;
    try {
      const transcriptText = await videoService.getTranscript(
        video.video_id,
        user.access_token
      );
      if (!transcriptText) return;
      const blob = new Blob([transcriptText], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${video.filename.replace(/\.[^/.]+$/, "")}_transcript.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to download transcript", e);
    }
  };

  return (
    <div className="space-y-8">
      {/* Video Header */}
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl">
        <div className="flex items-center space-x-6 mb-6">
          <div className="flex-shrink-0">
            <div className="h-16 w-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-2xl">
              <Play className="h-8 w-8 text-white" />
            </div>
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {video.filename}
            </h1>
            <p className="text-gray-500 text-lg">
              Uploaded {new Date(video.created_at).toLocaleDateString()}
            </p>
            <div className="flex items-center mt-3">
              <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200">
                Ready for Analysis
              </span>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={downloadTranscript}
              className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-medium hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              <Download className="h-4 w-4 mr-2" />
              Download Transcript
            </button>
          </div>
        </div>
      </div>

      {/* Video Summary */}
      {video.summary && (
        <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-white/40 shadow-xl">
          <div className="flex items-center space-x-3 mb-6">
            <div className="h-10 w-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              AI-Generated Summary
            </h2>
          </div>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-200">
            <div className="text-gray-700 leading-relaxed text-lg">
              {video.summary
                .replace(/\*\*Summary\*\*/g, "\n**Summary**")
                .replace(/\*\*Key Details\*\*/g, "\n**Key Details**")
                .replace(/\*\*Takeaways\*\*/g, "\n**Takeaways**")
                .replace(/- /g, "\n- ")
                .trim()
                .split("\n")
                .map((line, index) => (
                  <p key={index} className="mb-2">
                    {line}
                  </p>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoDetail;
