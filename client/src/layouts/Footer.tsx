import React from "react";

interface FooterProps {
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({ className = "" }) => {
  return (
    <div className={`text-center ${className}`}>
      <p className="text-indigo-200 text-sm">
        © 2025 Video Transcriber AI. All rights reserved.
      </p>
    </div>
  );
};
