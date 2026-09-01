/** Normalize legacy demo output into fenced markdown code blocks. */
export function normalizeAssistantMarkdown(text: string): string {
  let out = text;

  // Legacy Data Viz suffix: "--- generated code ---" + raw python
  if (out.includes("--- generated code ---")) {
    const segments = out.split("--- generated code ---");
    out = segments[0]?.trimEnd() ?? "";
    for (let i = 1; i < segments.length; i++) {
      const code = formatLegacyCodeBlock(segments[i] ?? "");
      if (code) {
        out += "\n\n### Generated code\n\n" + code;
      }
    }
  }

  return out;
}

function formatLegacyCodeBlock(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "";
  if (trimmed.startsWith("```")) return trimmed;
  let normalized = trimmed.replace(/;\s+/g, ";\n").replace(/;(?=\S)/g, ";\n");
  normalized = normalized.replace(/(\bimport\s+\S+)\s+(?=\w)/, "$1\n");
  return "```python\n" + normalized.trim() + "\n```";
}
