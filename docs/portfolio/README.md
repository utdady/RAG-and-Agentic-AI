# Portfolio page for AI Lab

Copy `ai-lab.html` into your GitHub Pages portfolio repo:

```
utdady.github.io/ai-lab.html
```

## Before publishing

1. Replace `LIVE_HUB_URL` in the HTML with your Vercel URL (or custom domain like `https://lab.utdady.dev`).
2. Add a nav link on your main portfolio page:

```html
<a href="/ai-lab.html">AI Lab</a>
```

3. On Vercel, set `NEXT_PUBLIC_PORTFOLIO_URL=https://utdady.github.io` so the live hub links back.

Full deploy steps: [`../../DEPLOY.md`](../../DEPLOY.md). API hosting: [`../../docs/deploy/oracle.md`](../../docs/deploy/oracle.md).
