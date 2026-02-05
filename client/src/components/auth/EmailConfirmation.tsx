import { useState } from "react";
import { Mail, ArrowLeft, RefreshCw, Video } from "lucide-react";
import { cognitoService } from "../../services/cognitoService";

interface EmailConfirmationProps {
  username: string;
  email: string;
  onSuccess: () => void;
  onBack: () => void;
}

const EmailConfirmation = ({
  username,
  email,
  onSuccess,
  onBack,
}: EmailConfirmationProps) => {
  const [confirmationCode, setConfirmationCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);

  const handleConfirmCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!confirmationCode) {
      setError("Please enter the confirmation code");
      return;
    }

    if (confirmationCode.length !== 6) {
      setError("Confirmation code must be 6 digits");
      return;
    }

    setIsLoading(true);

    try {
      await cognitoService.confirmSignUp(username, confirmationCode);
      setSuccess("Email confirmed successfully! You can now sign in.");

      // Wait a moment to show success message, then redirect
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (error: any) {
      console.error("Confirm sign up error:", error);

      if (error.name === "CodeMismatchException") {
        setError(
          "Invalid confirmation code. Please check your email and try again."
        );
      } else if (error.name === "ExpiredCodeException") {
        setError("Confirmation code has expired. Please request a new one.");
      } else if (error.name === "NotAuthorizedException") {
        setError("This account has already been confirmed.");
        setTimeout(() => {
          onSuccess();
        }, 2000);
      } else {
        setError(error.message || "An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError("");
    setSuccess("");
    setIsResending(true);

    try {
      await cognitoService.resendSignUpCode(username);
      setSuccess("New confirmation code sent to your email.");
    } catch (error: any) {
      console.error("Resend code error:", error);
      setError(
        error.message || "Failed to resend confirmation code. Please try again."
      );
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-20 w-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-6 shadow-2xl">
            <Video className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-2">
            Verify Your Email
          </h2>
          <p className="text-indigo-200 text-lg">
            Check your email for the confirmation code
          </p>
        </div>

        {/* Confirmation Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
          <div className="text-center mb-6">
            <div className="mx-auto h-16 w-16 bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
              <Mail className="h-8 w-8 text-blue-400" />
            </div>
            <p className="text-indigo-200 text-sm">
              We've sent a 6-digit confirmation code to:
            </p>
            <p className="text-white font-medium mt-1">{email}</p>
          </div>

          <form onSubmit={handleConfirmCode} className="space-y-6">
            {error && (
              <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-3">
                <p className="text-red-200 text-sm text-center">{error}</p>
              </div>
            )}

            {success && (
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-3">
                <p className="text-green-200 text-sm text-center">{success}</p>
              </div>
            )}

            {/* Confirmation Code Field */}
            <div>
              <label
                htmlFor="confirmationCode"
                className="block text-sm font-medium text-indigo-200 mb-2"
              >
                Confirmation Code
              </label>
              <input
                id="confirmationCode"
                type="text"
                value={confirmationCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, "").slice(0, 6);
                  setConfirmationCode(value);
                  setError("");
                }}
                className="block w-full px-4 py-3 border border-white/20 rounded-lg bg-white/10 text-white placeholder-indigo-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-center text-2xl tracking-widest"
                placeholder="000000"
                maxLength={6}
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || confirmationCode.length !== 6}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Verifying...</span>
                </div>
              ) : (
                "Verify Email"
              )}
            </button>

            {/* Resend Code */}
            <div className="text-center">
              <p className="text-indigo-200 text-sm mb-2">
                Didn't receive the code?
              </p>
              <button
                type="button"
                onClick={handleResendCode}
                disabled={isResending}
                className="text-blue-400 hover:text-blue-300 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto space-x-2"
              >
                {isResending ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    <span>Resend Code</span>
                  </>
                )}
              </button>
            </div>

            {/* Back Button */}
            <div className="text-center">
              <button
                type="button"
                onClick={onBack}
                className="text-indigo-300 hover:text-indigo-200 font-medium transition-colors flex items-center justify-center mx-auto space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Sign In</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EmailConfirmation;
