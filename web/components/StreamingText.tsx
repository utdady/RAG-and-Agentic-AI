"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { normalizeAssistantMarkdown } from "@/lib/markdown";

export function StreamingText({ text }: { text: string }) {
  if (!text) return null;
  const markdown = normalizeAssistantMarkdown(text);
  return (
    <div className="prose-stream">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
