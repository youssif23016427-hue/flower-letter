from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
import socketserver
import webbrowser


HTML_FILE_NAME = "flower_letter.html"
PORT = 8000


HTML_CONTENT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Flower Letter</title>
  <style>
    :root {
      --bg1: #fff6e9;
      --bg2: #ffe2d1;
      --ink: #3d2d2a;
      --accent: #e07a5f;
      --paper: #fffef8;
      --envelope: #f3b59f;
      --envelope-dark: #dd9a83;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 10%, #fffbe6 0%, transparent 25%),
        radial-gradient(circle at 80% 30%, #ffd8e3 0%, transparent 30%),
        linear-gradient(135deg, var(--bg1), var(--bg2));
      display: grid;
      place-items: center;
      padding: 20px;
    }

    .wrap {
      width: min(980px, 100%);
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .panel {
      background: rgba(255, 255, 255, 0.75);
      backdrop-filter: blur(6px);
      border: 1px solid rgba(61, 45, 42, 0.1);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 8px 22px rgba(52, 35, 30, 0.12);
    }

    h1 {
      margin: 0 0 12px;
      font-size: clamp(1.4rem, 2.5vw, 2rem);
    }

    .label {
      font-weight: 600;
      margin: 8px 0 6px;
      display: block;
    }

    textarea {
      width: 100%;
      min-height: 120px;
      border-radius: 12px;
      border: 1px solid rgba(61, 45, 42, 0.2);
      padding: 10px;
      font-size: 1rem;
      resize: vertical;
      background: #fff;
    }

    .btns {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 12px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 10px 16px;
      font-weight: 700;
      cursor: pointer;
      color: white;
      background: linear-gradient(140deg, var(--accent), #ce5f40);
      box-shadow: 0 5px 14px rgba(224, 122, 95, 0.35);
    }

    button.secondary {
      background: linear-gradient(140deg, #5f6cd3, #4652ba);
      box-shadow: 0 5px 14px rgba(70, 82, 186, 0.35);
    }

    .share {
      margin-top: 12px;
      display: grid;
      gap: 8px;
    }

    .share input {
      width: 100%;
      border: 1px solid rgba(61, 45, 42, 0.2);
      border-radius: 10px;
      padding: 10px;
      font-size: 0.95rem;
    }

    .hint {
      margin-top: 10px;
      font-size: 0.9rem;
      opacity: 0.78;
    }

    .stage {
      min-height: 420px;
      display: grid;
      place-items: center;
      position: relative;
      overflow: hidden;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.6));
    }

    .envelope {
      width: min(320px, 85%);
      height: 220px;
      position: relative;
      perspective: 1200px;
      transform-style: preserve-3d;
      transition: transform 0.6s ease;
    }

    .envelope:hover {
      transform: translateY(-4px);
    }

    .back {
      position: absolute;
      inset: 0;
      background: var(--envelope);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 14px 20px rgba(82, 42, 31, 0.25);
    }

    .back::before {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      margin: auto;
      width: 0;
      height: 0;
      border-left: 160px solid transparent;
      border-right: 160px solid transparent;
      border-top: 100px solid var(--envelope-dark);
      transform-origin: top;
      transition: transform 0.9s ease;
      z-index: 4;
    }

    .letter {
      position: absolute;
      left: 50%;
      bottom: 10px;
      transform: translateX(-50%) translateY(0);
      width: 88%;
      height: 180px;
      background: var(--paper);
      border-radius: 8px;
      padding: 16px;
      line-height: 1.4;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
      transition: transform 0.9s ease, height 0.9s ease;
      z-index: 3;
      overflow: auto;
      white-space: pre-wrap;
    }

    .front {
      position: absolute;
      inset: 0;
      z-index: 5;
      pointer-events: none;
    }

    .front::before,
    .front::after {
      content: "";
      position: absolute;
      bottom: 0;
      width: 0;
      height: 0;
      border-bottom: 110px solid #e8a78f;
    }

    .front::before {
      left: 0;
      border-right: 160px solid transparent;
    }

    .front::after {
      right: 0;
      border-left: 160px solid transparent;
    }

    .flower {
      position: absolute;
      opacity: 0;
      transform: translateY(10px) scale(0.8);
      transition: all 0.8s ease;
      font-size: 1.8rem;
      filter: drop-shadow(0 4px 5px rgba(0, 0, 0, 0.2));
    }

    .f1 { left: 12%; top: 26%; }
    .f2 { left: 20%; top: 64%; }
    .f3 { right: 14%; top: 24%; }
    .f4 { right: 18%; top: 66%; }

    .open .back::before {
      transform: rotateX(180deg);
    }

    .open .letter {
      transform: translateX(-50%) translateY(-112px);
      height: 230px;
    }

    .open ~ .flower,
    .open .flower {
      opacity: 1;
      transform: translateY(0) scale(1);
    }

    @media (max-width: 860px) {
      .wrap {
        grid-template-columns: 1fr;
      }

      .stage {
        min-height: 360px;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="panel">
      <h1>Make a Flower Letter</h1>
      <label class="label" for="message">Letter message</label>
      <textarea id="message"></textarea>

      <div class="btns">
        <button id="prepareBtn">Wrap Message In Letter</button>
        <button id="openBtn" class="secondary">Open Envelope</button>
      </div>

      <div class="share">
        <label class="label" for="shareLink">Sendable link</label>
        <input id="shareLink" type="text" readonly />
        <div class="btns">
          <button id="copyBtn">Copy Link</button>
        </div>
      </div>

      <div class="hint">100% free: Host this single HTML file on GitHub Pages or Netlify to share publicly.</div>
    </section>

    <section class="panel stage">
      <div id="envelope" class="envelope">
        <div class="back"></div>
        <div id="letter" class="letter"></div>
        <div class="front"></div>
      </div>

      <div class="flower f1">🌸</div>
      <div class="flower f2">🌻</div>
      <div class="flower f3">🌷</div>
      <div class="flower f4">🌼</div>
    </section>
  </div>

  <script>
    const DEFAULT_MESSAGE = "To someone special,\\n\\nYou make life brighter every day.\\nWith love and flowers.";

    const messageInput = document.getElementById("message");
    const letter = document.getElementById("letter");
    const envelope = document.getElementById("envelope");
    const shareLink = document.getElementById("shareLink");

    function currentBaseUrl() {
      const base = new URL(window.location.href);
      base.search = "";
      base.hash = "";
      return base.toString();
    }

    function updateLetterAndLink() {
      const text = messageInput.value.trim() || DEFAULT_MESSAGE;
      letter.textContent = text;

      const url = new URL(currentBaseUrl());
      url.searchParams.set("m", text);
      shareLink.value = url.toString();
    }

    document.getElementById("prepareBtn").addEventListener("click", () => {
      envelope.classList.remove("open");
      updateLetterAndLink();
    });

    document.getElementById("openBtn").addEventListener("click", () => {
      envelope.classList.add("open");
    });

    document.getElementById("copyBtn").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(shareLink.value);
      } catch {
        shareLink.select();
        document.execCommand("copy");
      }
    });

    const params = new URLSearchParams(window.location.search);
    const startMessage = params.get("m") || DEFAULT_MESSAGE;
    messageInput.value = startMessage;
    updateLetterAndLink();
  </script>
</body>
</html>
"""


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    html_path = script_dir / HTML_FILE_NAME
    html_path.write_text(HTML_CONTENT, encoding="utf-8")

    handler = partial(SimpleHTTPRequestHandler, directory=str(script_dir))
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        local_url = f"http://127.0.0.1:{PORT}/{HTML_FILE_NAME}"
        webbrowser.open(local_url)

        print("Flower Letter is running (100% free mode).")
        print(f"Open this URL: {local_url}")
        print("\nTo get a public free link:")
        print("1) Upload flower_letter.html to GitHub Pages (free) OR Netlify Drop (free)")
        print("2) Open the hosted URL")
        print("3) Type your message, click 'Wrap Message In Letter', copy link, send it")
        print("\nPress Ctrl+C to stop this local server.")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()