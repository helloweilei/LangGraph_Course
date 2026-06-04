"use client";

interface TimelineStep {
  toolType: "search" | "result";
  content: string;
}

interface TimelineProps {
  steps: TimelineStep[];
}

export function Timeline({ steps }: TimelineProps) {
  if (steps.length === 0) return null;

  return (
    <div className="mb-4 space-y-2">
      {steps.map((step, index) => (
        <div key={index} className="flex items-start gap-3">
          <div
            className={`w-3 h-3 rounded-full mt-1 shrink-0 ${
              step.toolType === "result" ? "bg-cyan-500" : "bg-yellow-500"
            }`}
          />
          <div className="text-sm">
            {step.toolType === "search" && (
              <div>
                <p className="font-semibold text-gray-700">
                  🔍 Searching the web...
                </p>
                {step.content && (
                  <p className="text-xs text-gray-600">Tool: {step.content}</p>
                )}
              </div>
            )}
            {step.toolType === "result" && (
              <div>
                <p className="font-semibold text-gray-700">Searching Result:</p>
                <p className="text-xs text-gray-600  max-w-[75%]">
                  {step.content}
                </p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
