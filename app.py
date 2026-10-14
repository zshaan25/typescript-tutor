import json
from getpass import getpass

import gradio as gr
from google import genai
from google.genai import types

# The Gemini key is stored in Colab Secrets under the name "chatbot"
try:
    from google.colab import userdata
    API_KEY = userdata.get("chatbot")
except Exception:
    API_KEY = getpass("Gemini API key: ")

MODEL = "gemini-2.5-flash"  # change if your key uses a different Gemini model
client = genai.Client(api_key=API_KEY)

SYSTEM = """You are TypeScript Tutor, a friendly teacher who answers questions about TypeScript only.

Scope: the TypeScript language and type system, tsc, tsconfig, tooling, and TypeScript with Node, React, Angular and similar. Plain JavaScript only when needed to explain TypeScript.
If a question is outside this scope, do not answer it. Reply in one or two friendly sentences saying you only cover TypeScript, and suggest a related TypeScript question.

Always format answers exactly like this (skip a section only if it adds nothing):

> **Quick answer:** one or two plain sentences that directly answer the question.

### How it works
3 to 5 short bullet points. One idea per bullet, plain language, key terms in **bold**.

### Example
One minimal, runnable example in a ```ts block with short comments. Add one line after it saying what it shows.

### Watch out for
2 or 3 bullets on common mistakes or strict-mode gotchas.

### Try it yourself
One small practice task the learner can do in a few minutes.

Rules: no long paragraphs, no filler, no preamble before the Quick answer. Use a table only when comparing two or more things. Never invent APIs or compiler options. Keep the whole answer under about 350 words unless asked for more."""

LEVELS = {
    "Beginner": "The learner is new to TypeScript. Use simple words, define any jargon, keep examples tiny.",
    "Intermediate": "The learner knows the basics. Focus on practical patterns and why they work.",
    "Advanced": "The learner is experienced. Be concise and cover type-level details and edge cases.",
}


def stream_reply(message, history, level):
    contents = []
    for m in history[-20:]:
        if isinstance(m.get("content"), str) and m["content"].strip():
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM + "\n\n" + LEVELS.get(level, LEVELS["Beginner"]),
        temperature=0.4,
        max_output_tokens=2048,
    )
    text = ""
    try:
        for chunk in client.models.generate_content_stream(model=MODEL, contents=contents, config=config):
            if chunk.text:
                text += chunk.text
                yield text
        if not text:
            yield "No response came back. Try rephrasing your question."
    except Exception as e:
        yield f"Something went wrong: {e}"


def respond(message, history, level):
    if not message or not message.strip():
        yield history, ""
        return
    history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": ""}]
    yield history, ""
    for partial in stream_reply(message, history[:-2], level):
        history[-1]["content"] = partial
        yield history, ""


def api_chat(message, history_json, level):  # used by index.html
    try:
        history = json.loads(history_json or "[]")
    except Exception:
        history = []
    yield from stream_reply(message, history, level)


STARTERS = [
    "Explain generics with a simple example",
    "Interface vs type: when should I use which?",
    "How does type narrowing work?",
    "Set up a strict tsconfig.json for a Node project",
    "What are utility types like Pick, Omit and Partial?",
]

CSS = """
.gradio-container{max-width:940px!important;margin:0 auto!important;background:#f3f6fd!important}
#hero{background:linear-gradient(135deg,#14214f,#2563eb 60%,#6d5dfc);border-radius:20px;padding:28px 30px;color:#fff;
  box-shadow:0 14px 40px #2563eb33;margin-top:12px}
#hero .badge{display:inline-grid;place-items:end;width:44px;height:44px;border-radius:11px;background:#fff;color:#2563eb;
  font:800 18px/1 monospace;padding:5px 7px;margin-bottom:14px}
#hero h1{font-size:32px;font-weight:800;letter-spacing:-.02em;margin:0 0 6px;color:#fff}
#hero p{margin:0;color:#dbe6ff}
#chat{border:1px solid #dfe6f5!important;border-radius:18px!important;background:#fff!important}
#chat blockquote{background:#eef4ff;border-left:4px solid #2563eb;border-radius:8px;padding:8px 14px;margin:0 0 10px}
#chat h3{font-size:16px;font-weight:700;color:#14214f;margin:14px 0 6px}
#chat pre{border-radius:10px!important}
footer{display:none!important}
"""

theme = gr.themes.Soft(
    primary_hue="indigo", secondary_hue="blue", neutral_hue="slate",
    font=[gr.themes.GoogleFont("Bricolage Grotesque"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
)

HERO = """<div id="hero"><div class="badge">TS</div><h1>TypeScript Tutor</h1>
<p>Clear, structured answers on types, generics, tsconfig and tooling.</p></div>"""

with gr.Blocks(theme=theme, css=CSS, title="TypeScript Tutor") as demo:
    gr.HTML(HERO)
    level = gr.Radio(list(LEVELS), value="Beginner", label="Your level")
    chat = gr.Chatbot(type="messages", height=520, show_label=False, elem_id="chat",
                      placeholder="Ask a TypeScript question or paste code you want explained.")
    with gr.Row():
        box = gr.Textbox(placeholder="Ask about TypeScript...", show_label=False,
                         container=False, scale=8, lines=1, max_lines=6)
        send = gr.Button("Send", variant="primary", scale=1)
    gr.Examples(examples=[[q] for q in STARTERS], inputs=box, label="Try asking")
    gr.ClearButton([chat, box], value="Clear chat", size="sm")

    box.submit(respond, [box, chat, level], [chat, box])
    send.click(respond, [box, chat, level], [chat, box])

    with gr.Row(visible=False):  # hidden endpoint for index.html
        a_msg, a_hist, a_level, a_out = gr.Textbox(), gr.Textbox(), gr.Textbox(), gr.Textbox()
        a_btn = gr.Button()
    a_btn.click(api_chat, [a_msg, a_hist, a_level], a_out, api_name="chat")

demo.queue().launch(share=True, debug=True)  # copy the public link into index.html
