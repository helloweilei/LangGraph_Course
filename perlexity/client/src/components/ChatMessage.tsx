"use client";

import { Timeline } from "./Timeline";

interface ChatMessageProps {
  type: "user" | "assistant" | "tool";
  content: string;
  isLoading?: boolean;
  toolType?: "search" | "result";
}

export function ChatMessage({
  type,
  toolType,
  content,
  isLoading,
}: ChatMessageProps) {
  const isUser = type === "user";

  return type === "tool" ? (
    <Timeline steps={[{ toolType: toolType!, content }]} />
  ) : (
    <div
      className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div className={`max-w-[70%] ${isUser ? "order-2" : "order-1"}`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser ? "bg-violet-600 text-white" : "bg-gray-200 text-gray-900"
          }`}
        >
          <p className="text-sm">{content}</p>
          {isLoading && <span className="animate-pulse">...</span>}
        </div>
      </div>
    </div>
  );
}
