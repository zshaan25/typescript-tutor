# TypeScript Tutor

An AI tutor that answers questions about **TypeScript only**. It runs on Google Gemini, is served with Gradio from Google Colab, and comes with a custom web frontend (`index.html`).

Every answer follows the same structure: a **Quick answer**, **How it works**, a runnable **Example**, **Watch out for**, and a short **Try it yourself** exercise. Questions about anything else are politely declined.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zshaan25/typescript-tutor/blob/main/typescript_tutor.ipynb)

## Features

- TypeScript-only scope: types, generics, utility types, narrowing, classes, modules, tsconfig, tooling, and TypeScript with Node and React
- Three learner levels (Beginner, Intermediate, Advanced) that change the depth of every answer
- Streaming responses with syntax-highlighted code and a copy button
- Topic shortcuts and starter questions for quick learning
- Two interfaces: the built-in Gradio chat and the custom `index.html` frontend

## How it works

```
index.html  --->  Gradio server (Colab)  --->  Gemini API
 (browser)        app.py / notebook
```

The Colab notebook starts a Gradio server and prints a public `gradio.live` link. The Gemini API key stays inside Colab and is never exposed to the browser.

## Project structure

| File | Purpose |
|---|---|
| `typescript_tutor.ipynb` | Colab notebook that installs dependencies and starts the app |
| `app.py` | Same app as a plain Python file |
| `index.html` | Custom chat frontend |
| `requirements.txt` | Python dependencies |

## Setup

1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Click the **Open in Colab** badge above, or upload `typescript_tutor.ipynb` to [colab.research.google.com](https://colab.research.google.com).
3. In Colab, open **Secrets** (key icon in the left sidebar), add a secret named `chatbot` with your API key as the value, and turn on **Notebook access**.
4. Run both code cells. When the app starts, it prints a public link ending in `gradio.live`.

## Usage

**Option A: Gradio interface.** Open the `gradio.live` link directly and start chatting.

**Option B: Custom frontend.**

1. Download `index.html` and open it in a browser.
2. Paste the `gradio.live` link into the Connect window and click **Connect**. The link is remembered for next time.
3. Pick your level, choose a topic or type a question, and press Enter.

You can also open the page with the link pre-filled: `index.html?url=https://xxxx.gradio.live`

## Customization

- **Model:** change the `MODEL` variable near the top of the app code.
- **Answer format and scope:** edit the `SYSTEM` prompt.
- **Colors:** edit the CSS variables at the top of `index.html`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Status shows Offline or no reply | The Colab cell stopped. Run it again and paste the new link. |
| Link stopped working | Share links change on every run and expire after about a week. |
| Invalid API key error | Check that the secret is named exactly `chatbot` and notebook access is on. |
| Model not found | Set `MODEL` to a Gemini model your key can use. |

## Limitations

The tutor is only available while the Colab cell is running, and the public link changes each time. For a permanent deployment, host the same app on a Hugging Face Space and use its fixed URL in `index.html`.

## Security

Never commit your API key. Keep it in Colab Secrets only.

## License

MIT
