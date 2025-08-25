import type { Video } from "../types/video";

export const mockVideos: Video[] = [
  {
    id: "1",
    name: "Machine Learning Basics.mp4",
    url: "#",
    uploadedAt: new Date("2024-01-15"),
    status: "completed",
    transcript:
      "This is a comprehensive transcript of the machine learning video. It covers supervised learning, unsupervised learning, and neural networks with practical examples and real-world applications.",
    summary:
      "This video provides an in-depth overview of machine learning concepts, including supervised learning, unsupervised learning, and neural networks. It covers practical applications and real-world examples.",
  },
  {
    id: "2",
    name: "Data Science Fundamentals.mp4",
    url: "#",
    uploadedAt: new Date("2024-01-20"),
    status: "completed",
    transcript:
      "A comprehensive overview of data science methodologies, including data collection, analysis, and visualization techniques. The video explains key concepts like data preprocessing, statistical analysis, and machine learning integration.",
    summary:
      "A comprehensive overview of data science methodologies, including data collection, analysis, and visualization techniques.",
  },
  {
    id: "3",
    name: "Sample Video 3.mp4",
    url: "#",
    uploadedAt: new Date("2024-01-25"),
    status: "processing",
  },
];
