"use client";

import katex from "katex";
import type { ReactNode } from "react";

const LATEX_RE =
  /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$)/g;

function renderMath(latex: string, displayMode: boolean, key: string) {
  try {
    const html = katex.renderToString(latex.trim(), {
      displayMode,
      throwOnError: false,
      strict: "ignore",
    });
    if (displayMode) {
      return (
        <div
          key={key}
          className="my-2 overflow-x-auto"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    }
    return (
      <span
        key={key}
        className="mx-0.5 inline-block align-middle"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  } catch {
    return (
      <code key={key} className="font-mono text-xs">
        {latex}
      </code>
    );
  }
}

function parsePart(part: string, key: string): ReactNode {
  if (part.startsWith("$$") && part.endsWith("$$")) {
    return renderMath(part.slice(2, -2), true, key);
  }
  if (part.startsWith("\\[") && part.endsWith("\\]")) {
    return renderMath(part.slice(2, -2), true, key);
  }
  if (part.startsWith("\\(") && part.endsWith("\\)")) {
    return renderMath(part.slice(2, -2), false, key);
  }
  if (part.startsWith("$") && part.endsWith("$") && part.length > 1) {
    return renderMath(part.slice(1, -1), false, key);
  }
  return part;
}

export function MathText({ text }: { text: string }) {
  const nodes: ReactNode[] = [];
  let last = 0;
  let i = 0;

  for (const match of text.matchAll(LATEX_RE)) {
    const start = match.index ?? 0;
    if (start > last) {
      nodes.push(text.slice(last, start));
    }
    nodes.push(parsePart(match[0], `m-${i++}`));
    last = start + match[0].length;
  }

  if (last < text.length) {
    nodes.push(text.slice(last));
  }

  return <>{nodes}</>;
}
