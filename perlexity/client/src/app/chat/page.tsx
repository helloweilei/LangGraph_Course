"use client";

import { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { ChatMessage } from "@/components/ChatMessage";
import { streamChat, ChatEvent } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp: Date;
  toolType?: "search" | "result";
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    let assistantMessage = "";

    try {
      await streamChat(
        input,
        threadId,
        (event: ChatEvent) => {
          if (event.type === "thread_id" && event.thread_id) {
            setThreadId(event.thread_id);
          } else if (event.type === "message" && event.message) {
            assistantMessage += event.message;
            setMessages((prev) => {
              const updated = [...prev];
              const lastMsg = updated[updated.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                lastMsg.content = assistantMessage;
              } else {
                assistantMessage = "";
                updated.push({
                  id: Date.now().toString(),
                  role: "assistant",
                  content: event.message!,
                  timestamp: new Date(),
                });
              }
              return updated;
            });
          } else if (
            event.type === "tool_call" ||
            event.type === "tool_result"
          ) {
            setMessages((prev) => {
              const updated = [
                ...prev,
                {
                  id: (Date.now() + 1).toString(),
                  role: "tool",
                  content: event.tool || event.content || "",
                  timestamp: new Date(),
                  toolType: event.type === "tool_call" ? "search" : "result",
                } as Message,
              ];
              return updated;
            });
          } else if (event.type === "done") {
            setIsLoading(false);
          }
        },
        (error: Error) => {
          console.error("Chat error:", error);
          setMessages((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              role: "assistant",
              content: `Error: ${error.message}`,
              timestamp: new Date(),
            },
          ]);
        },
      );
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      <Header />

      <div className="flex-1 flex flex-col max-w-6xl mx-auto w-full px-4 py-8 overflow-y-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto mb-8 space-y-4 px-2">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <p className="text-gray-600 text-lg">
                  我是你的智能搜索助手，开始你的搜索之旅吧！
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id}>
                  <ChatMessage
                    type={msg.role}
                    content={msg.content}
                    toolType={msg.toolType}
                    isLoading={isLoading}
                  />
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="flex gap-3 items-end">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message"
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:bg-gray-100"
          />
          <button
            type="button"
            className="p-2 text-gray-400 hover:text-gray-600"
            title="Attach file"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-3 bg-cyan-500 text-white rounded-full hover:bg-cyan-600 disabled:bg-gray-300 transition cursor-pointer"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16417951 C3.34915502,0.9 2.40734225,0.99 1.77946707,1.4429026 C0.994623095,2.0766753 0.837654306,3.16604506 1.15159189,3.95153188 L3.03521743,10.3925249 C3.03521743,10.5496223 3.34915502,10.7067197 3.50612381,10.7067197 L16.6915026,11.4922066 C16.6915026,11.4922066 17.1624089,11.4922066 17.1624089,11.0409145 L17.1624089,12.4744748 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
