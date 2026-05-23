// frontend/src/pages/AIContentGenerator.tsx
import { useState } from "react";

const API_BASE_URL = String(
  import.meta.env.VITE_API_BASE_URL ??
    (import.meta.env.DEV ? "http://localhost:8000" : "")
).replace(/\/+$/, "");
const API_URL = API_BASE_URL
  ? `${API_BASE_URL}/api/v1/generate-content`
  : "/api/v1/generate-content";

const AIContentGenerator = () => {
  const [topic, setTopic] = useState("");
  const [level, setLevel] = useState("Beginner");
  const [generatedContent, setGeneratedContent] = useState("");
  const [leftContent, setLeftContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateContent = async () => {
    if (!topic.trim()) {
      setError("Please enter a topic to generate content");
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic: topic.trim(), level }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data?.detail || data?.message || `HTTP error ${response.status}`;
        throw new Error(message);
      }

      setGeneratedContent(data.content || "");
      if (!data.content) {
        throw new Error("No content returned from the API.");
      }
      setError("");
    } catch (error) {
      console.error("Error generating content:", error);
      setError(error instanceof Error ? error.message : "Failed to generate content. Please try again.");
      setGeneratedContent("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyFromAI = () => {
    if (!generatedContent) {
      setError("Please generate content first before copying");
      return;
    }
    setLeftContent(generatedContent);
    setError("");
  };

  const handleDownloadGenerated = () => {
    if (!generatedContent) {
      setError("Please generate content first before downloading");
      return;
    }

    const blob = new Blob([generatedContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ai-generated-content-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setError("");
  };

  const handleDownload = () => {
    if (!leftContent.trim()) {
      setError("Please add content to the editor before downloading");
      return;
    }

    const blob = new Blob([leftContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `content-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setError("");
  };

  return (
    <div className="container mx-auto p-6 h-screen flex flex-col bg-gray-50">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2 text-blue-600">
          <span className="text-2xl">✨</span>
          AI Content Generator
        </h1>
        <p className="text-gray-600 mt-1">
          Generate high-quality educational content using AI
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="flex gap-6 flex-1 min-h-0">
        {/* LEFT SIDE - Editable Editor */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm flex-1 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800">Content Editor</h2>
              <p className="text-sm text-gray-600">
                Edit and refine your content here
              </p>
            </div>
            <div className="flex-1 p-4">
              <textarea
                value={leftContent}
                onChange={(e) => setLeftContent(e.target.value)}
                placeholder="Your content will appear here. You can edit it freely..."
                className="w-full h-full resize-none border border-gray-300 rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                style={{ minHeight: 0 }}
              />
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleCopyFromAI}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!generatedContent || isLoading}
            >
              📋 Copy from AI
            </button>
            <button
              onClick={handleDownload}
              className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!leftContent.trim() || isLoading}
            >
              💾 Download as Text File
            </button>
          </div>
        </div>

        {/* RIGHT SIDE - AI Generator */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <span className="text-xl">✨</span>
                AI Content Generator
              </h2>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Enter your topic here..."
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => e.key === "Enter" && !isLoading && handleGenerateContent()}
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Level
                </label>
                <select
                  value={level}
                  onChange={(e) => setLevel(e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <button
                onClick={handleGenerateContent}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                disabled={isLoading || !topic.trim()}
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Generating...
                  </>
                ) : (
                  <>
                    <span className="mr-2">✨</span>
                    Generate Content
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Generated Content Display */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm flex-1 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800">Generated Content</h2>
              <p className="text-sm text-gray-600">
                AI-generated content will appear here
              </p>
            </div>
            <div className="flex-1 p-4 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="animate-spin text-2xl mb-3">⏳</div>
                    <p className="text-gray-600">Generating your content...</p>
                    <p className="text-xs text-gray-500 mt-1">
                      This may take a few seconds
                    </p>
                  </div>
                </div>
              ) : generatedContent ? (
                <div>
                  <pre className="whitespace-pre-wrap font-sans text-sm text-gray-800 mb-4">
                    {generatedContent}
                  </pre>
                  <button
                    onClick={handleDownloadGenerated}
                    className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isLoading}
                  >
                    💾 Download Generated Content
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p className="text-center">
                    Generated content will appear here
                    <br />
                    <span className="text-xs">
                      Enter a topic and click "Generate Content" to start
                    </span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIContentGenerator;