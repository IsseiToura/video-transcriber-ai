import { useAuth } from "./contexts/AuthContext";
import { useVideos } from "./hooks/useVideos";
import { useVideoSelection } from "./hooks/useVideoSelection";
import { Header, Sidebar, MainContent, Footer, Login } from "./layouts";

function App() {
  const { user, logout, isLoading } = useAuth();
  const { videos, addVideo, handleTranscriptGeneration } = useVideos();
  const {
    selectedVideo,
    showUpload,
    selectVideo,
    showUploadForm,
    handleUploadComplete,
  } = useVideoSelection();

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!user) {
    return <Login />;
  }

  const handleUploadCompleteWithAdd = (newVideo: any) => {
    const video = handleUploadComplete(newVideo);
    addVideo(video);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Header user={user} onLogout={logout} onShowUpload={showUploadForm} />

      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar
          videos={videos}
          selectedVideo={selectedVideo}
          onVideoSelect={selectVideo}
        />

        <main className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
          <MainContent
            selectedVideo={selectedVideo}
            onUploadComplete={handleUploadCompleteWithAdd}
            onGenerateTranscript={handleTranscriptGeneration}
          />
        </main>
      </div>

      <Footer className="mt-8" />
    </div>
  );
}

export default App;
