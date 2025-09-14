import { useAuth } from "./contexts/AuthContext";
import { useVideos } from "./hooks/useVideos";
import { useVideoSelection } from "./hooks/useVideoSelection";
import {
  Header,
  Sidebar,
  MainContent,
  Footer,
  SignIn,
  SignUp,
  EmailConfirmation,
} from "./layouts";
import type { VideoInfo } from "./types/video";
import { Toaster } from "react-hot-toast";

function App() {
  const {
    user,
    logout,
    isLoading,
    authView,
    pendingUsername,
    pendingEmail,
    checkAuth,
    handleSignUpSuccess,
    handleEmailConfirmationSuccess,
    handleSwitchToSignIn,
    handleSwitchToSignUp,
  } = useAuth();

  const { videos, addVideo, removeVideo, loading: videosLoading } = useVideos();
  const {
    selectedVideo,
    selectVideo,
    showUploadForm,
    handleUploadComplete,
    clearSelection,
  } = useVideoSelection();

  const handleSignInSuccess = async () => {
    await checkAuth();
  };

  // Show loading state
  if (isLoading || videosLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Show auth screens if not authenticated
  if (!user) {
    switch (authView) {
      case "signup":
        return (
          <SignUp
            onSuccess={handleSignUpSuccess}
            onSwitchToSignIn={handleSwitchToSignIn}
          />
        );
      case "email-confirmation":
        return (
          <EmailConfirmation
            username={pendingUsername}
            email={pendingEmail}
            onSuccess={handleEmailConfirmationSuccess}
            onBack={handleSwitchToSignIn}
          />
        );
      default:
        return (
          <SignIn
            onSuccess={handleSignInSuccess}
            onSwitchToSignUp={handleSwitchToSignUp}
          />
        );
    }
  }

  const handleUploadCompleteWithAdd = (newVideo: VideoInfo) => {
    const video = handleUploadComplete(newVideo);
    addVideo(video);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50">
      <Header user={user} onLogout={logout} onShowUpload={showUploadForm} />

      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar
          videos={videos}
          selectedVideo={selectedVideo}
          onVideoSelect={selectVideo}
          onVideoDeleted={(deletedId: string) => {
            removeVideo(deletedId);
            if (selectedVideo?.video_id === deletedId) {
              clearSelection();
            }
          }}
        />

        <main className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-50">
          <MainContent
            selectedVideo={selectedVideo}
            onUploadComplete={handleUploadCompleteWithAdd}
          />
        </main>
      </div>

      <Footer className="mt-8 bg-white" />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#363636",
            color: "#fff",
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: "#10B981",
              secondary: "#fff",
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: "#EF4444",
              secondary: "#fff",
            },
          },
        }}
      />
    </div>
  );
}

export default App;
