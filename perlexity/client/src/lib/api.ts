const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatEvent {
  type: "thread_id" | "message" | "tool_call" | "tool_result" | "done";
  thread_id?: string;
  message?: string;
  tool?: string;
  tool_message?: string;
  content?: string;
}

export async function streamChat(
  message: string,
  threadId: string | null,
  onEvent: (event: ChatEvent) => void,
  onError: (error: Error) => void,
) {
  try {
    const params = new URLSearchParams({ message });
    if (threadId) {
      params.append("thread_id", threadId);
    }

    const response = await fetch(`${API_BASE_URL}/chat/${message}?${params}`, {
      method: "GET",
      headers: {
        Accept: "text/event-stream",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Response body is not readable");
    }

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const dataStr = line.slice(6);
          if (dataStr.trim()) {
            try {
              const event = JSON.parse(dataStr) as ChatEvent;
              onEvent(event);
            } catch (e) {
              console.error("Failed to parse event:", dataStr, e);
            }
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error(String(error)));
  }
}

export async function streamChat2(
  message: string,
  threadId: string | null,
  onEvent: (event: ChatEvent) => void,
  onError: (error: Error) => void,
) {
  const params = new URLSearchParams();
  if (threadId) {
    params.append("thread_id", threadId);
  }

  const eventSource = new EventSource(
    `${API_BASE_URL}/chat/${message}?${params}`,
  );

  eventSource.onmessage = (event) => {
    try {
      const eventData = JSON.parse(event.data) as ChatEvent;
      onEvent(eventData);
      if (eventData.type === "done") {
        eventSource.close();
      }
    } catch (e) {
      console.error("Failed to parse event:", event.data, e);
    }
  };
  eventSource.onerror = (error) => {
    eventSource.close();
    onError(error instanceof Error ? error : new Error(String(error)));
  };
}
