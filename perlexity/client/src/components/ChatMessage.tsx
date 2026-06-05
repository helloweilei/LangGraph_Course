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
      className={`flex gap-2 ${isUser ? "justify-end" : "justify-start"} mb-4 items-start`}
    >
      <div className={`max-w-[70%] order-2`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser ? "bg-violet-600 text-white" : "bg-gray-200 text-gray-900"
          }`}
        >
          <p className="text-sm">{content}</p>
          {isLoading && <span className="animate-pulse">...</span>}
        </div>
      </div>
      <div className={`w-8 h-8 text-2xl ${isUser ? "order-3" : "order-1"}`}>
        {isUser ? "🧑" : "🤖"}
      </div>
    </div>
  );
}
