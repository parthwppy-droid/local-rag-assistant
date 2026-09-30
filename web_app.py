"""
Apex AI - Next-Gen Local RAG & Universal AI Web Application
Modern, luxury glassmorphism interface with custom branding, code copy buttons, and responsive design.
"""
import http.server
import socketserver
import json
import urllib.parse
import os
import webbrowser
import threading
import socket
import sys

from rag_pipeline import LocalRAGPipeline

DEFAULT_PORT = 5000
docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
db_path = os.path.join(os.path.dirname(__file__), "vector_store.json")
pipeline = LocalRAGPipeline(docs_dir=docs_dir, db_path=db_path)

# BUG FIX: unlike main.py, this file never triggered ingestion — so the web UI
# was always querying an empty vector DB regardless of what was in sample_docs.
if not os.path.exists(db_path) or len(pipeline.vector_db.chunks) == 0:
    print("Vector DB not found or empty. Running Phase 1 Ingestion first...")
    pipeline.run_ingestion()
else:
    print(f"[OK] Found existing Vector DB with {len(pipeline.vector_db.chunks)} indexed chunk(s).")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Apex AI - Next-Gen Intelligence</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    body { 
      font-family: 'Plus Jakarta Sans', sans-serif; 
      background: radial-gradient(circle at top left, #0f172a, #090d16 60%, #020617);
      color: #f8fafc;
    }
    
    .glass-card {
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .glass-sidebar {
      background: rgba(10, 15, 30, 0.85);
      backdrop-filter: blur(20px);
      border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    .gradient-text {
      background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .chat-bubble-user {
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
      border-radius: 20px 20px 4px 20px;
    }

    .chat-bubble-ai {
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(12px);
      border-radius: 20px 20px 20px 4px;
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .prompt-card {
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .prompt-card:hover {
      transform: translateY(-3px);
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 12px 30px -10px rgba(56, 189, 248, 0.2);
    }

    pre {
      background: #090d16 !important;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 14px;
      overflow-x: auto;
      font-family: 'Fira Code', monospace;
      font-size: 13px;
      color: #38bdf8;
      position: relative;
    }
    
    code {
      background: rgba(56, 189, 248, 0.1);
      color: #38bdf8;
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 13px;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 4px; }
  </style>
</head>
<body class="h-screen flex overflow-hidden">

  <!-- Sidebar -->
  <div class="w-72 glass-sidebar flex flex-col justify-between p-5 hidden md:flex z-20">
    <div class="space-y-6">
      
      <!-- Brand Header -->
      <div class="flex items-center gap-3 px-1">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-indigo-500/30">
          ⚡
        </div>
        <div>
          <h1 class="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
            Apex <span class="gradient-text">AI</span>
          </h1>
          <p class="text-[11px] font-medium text-slate-400">Universal Intelligence</p>
        </div>
      </div>

      <!-- Action Button -->
      <button onclick="clearChat()" class="w-full py-3 px-4 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition shadow-sm">
        <i class="fa-solid fa-plus text-cyan-400"></i> New Conversation
      </button>

      <!-- Knowledge Base Badge -->
      <div class="pt-4 border-t border-slate-800/60 space-y-3">
        <div class="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          <span>Active Engines</span>
          <span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">ONLINE</span>
        </div>
        <div class="space-y-2 text-xs">
          <div class="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <i class="fa-solid fa-database text-cyan-400"></i>
            <div class="truncate">
              <div class="font-semibold text-slate-200 text-[12px]">Local Document RAG</div>
              <div class="text-[10px] text-slate-400">Vector Search Active</div>
            </div>
          </div>
          <div class="flex items-center gap-2.5 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <i class="fa-solid fa-globe text-purple-400"></i>
            <div class="truncate">
              <div class="font-semibold text-slate-200 text-[12px]">World Knowledge Engine</div>
              <div class="text-[10px] text-slate-400">Live Web & Trivia Search</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Profile Footer -->
    <div class="pt-4 border-t border-slate-800/60 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-xs shadow">U</div>
        <div class="text-xs">
          <div class="font-semibold text-slate-200">Local User</div>
          <div class="text-[10px] text-slate-400">Apex System v2.0</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Chat Container -->
  <div class="flex-1 flex flex-col h-full relative">
    
    <!-- Mobile Header -->
    <div class="md:hidden p-4 bg-[#0a0f1e] border-b border-slate-800 flex items-center justify-between z-30">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold">⚡</div>
        <span class="font-extrabold text-base text-white">Apex <span class="gradient-text">AI</span></span>
      </div>
      <button onclick="clearChat()" class="text-xs px-3 py-1.5 bg-slate-800 rounded-lg text-slate-200 border border-slate-700">New Chat</button>
    </div>

    <!-- Messages Window -->
    <div id="messages-container" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 max-w-4xl mx-auto w-full">
      
      <!-- Welcome Hero -->
      <div id="welcome-card" class="text-center py-16 space-y-6">
        <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500/20 via-indigo-500/20 to-purple-500/20 border border-cyan-500/30 flex items-center justify-center text-4xl mx-auto shadow-2xl shadow-cyan-500/10">
          ⚡
        </div>
        <div class="space-y-2">
          <h2 class="text-3xl font-extrabold text-white tracking-tight">What can <span class="gradient-text">Apex AI</span> answer for you?</h2>
          <p class="text-sm text-slate-400 max-w-md mx-auto">
            Universal intelligence for complex trivia, coding, official processes, live news, and local document analysis.
          </p>
        </div>

        <!-- Suggestion Chips -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs max-w-xl mx-auto pt-6">
          <button onclick="usePrompt('Which country has the most time zones - and it\'s not Russia?')" class="prompt-card p-4 glass-card rounded-2xl text-left border border-slate-800 space-y-1">
            <div class="font-bold text-cyan-400 flex items-center gap-1.5"><i class="fa-solid fa-globe"></i> World Trivia</div>
            <div class="text-slate-300">Which country has the most time zones?</div>
          </button>

          <button onclick="usePrompt('What does CAPTCHA actually stand for?')" class="prompt-card p-4 glass-card rounded-2xl text-left border border-slate-800 space-y-1">
            <div class="font-bold text-purple-400 flex items-center gap-1.5"><i class="fa-solid fa-key"></i> Acronyms & Terms</div>
            <div class="text-slate-300">What does CAPTCHA stand for?</div>
          </button>

          <button onclick="usePrompt('What is the process for passport?')" class="prompt-card p-4 glass-card rounded-2xl text-left border border-slate-800 space-y-1">
            <div class="font-bold text-emerald-400 flex items-center gap-1.5"><i class="fa-solid fa-passport"></i> Process Guides</div>
            <div class="text-slate-300">Step-by-step passport application guide</div>
          </button>

          <button onclick="usePrompt('How does dynamic memory allocation work in C?')" class="prompt-card p-4 glass-card rounded-2xl text-left border border-slate-800 space-y-1">
            <div class="font-bold text-amber-400 flex items-center gap-1.5"><i class="fa-solid fa-file-code"></i> Local Document RAG</div>
            <div class="text-slate-300">How does malloc work in C notes?</div>
          </button>
        </div>
      </div>

    </div>

    <!-- Input Bar Area -->
    <div class="p-4 bg-transparent max-w-4xl mx-auto w-full z-20">
      <div class="relative glass-card border border-slate-700/60 focus-within:border-cyan-500/60 rounded-2xl shadow-2xl p-2 flex items-center gap-3">
        <textarea id="user-input" rows="1" class="flex-1 bg-transparent text-sm text-white focus:outline-none px-4 py-2 resize-none max-h-36 placeholder-slate-500" placeholder="Ask Apex AI anything..." onkeydown="handleKeyDown(event)"></textarea>
        <button id="send-btn" onclick="sendMessage()" class="w-10 h-10 bg-gradient-to-tr from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white rounded-xl flex items-center justify-center transition shadow-lg shadow-cyan-500/25 shrink-0">
          <i class="fa-solid fa-paper-plane text-xs"></i>
        </button>
      </div>
      <p class="text-[11px] text-slate-500 text-center mt-2 font-medium">Apex AI v2.0 · Universal Multi-Domain & Local RAG System</p>
    </div>

  </div>

  <script>
    function usePrompt(text) {
      document.getElementById('user-input').value = text;
      sendMessage();
    }

    function handleKeyDown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    }

    function clearChat() {
      const container = document.getElementById('messages-container');
      container.innerHTML = '';
      appendWelcomeCard();
    }

    function appendWelcomeCard() {
      const container = document.getElementById('messages-container');
      container.innerHTML = `
        <div id="welcome-card" class="text-center py-16 space-y-6">
          <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500/20 via-indigo-500/20 to-purple-500/20 border border-cyan-500/30 flex items-center justify-center text-4xl mx-auto shadow-2xl">⚡</div>
          <div class="space-y-2">
            <h2 class="text-3xl font-extrabold text-white tracking-tight">What can <span class="gradient-text">Apex AI</span> answer for you?</h2>
            <p class="text-sm text-slate-400 max-w-md mx-auto">Universal intelligence for trivia, processes, coding, live news, and local documents.</p>
          </div>
        </div>
      `;
    }

    function formatMarkdown(text) {
      text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
      text = text.replace(/```([a-z]*)\\n([\\s\\S]*?)```/g, '<div class="relative my-3"><button onclick="copyCode(this)" class="absolute top-2 right-2 px-2.5 py-1 text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"><i class="fa-regular fa-copy"></i> Copy</button><pre><code>$2</code></pre></div>');
      text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
      text = text.replace(/\\n/g, '<br>');
      return text;
    }

    function copyCode(btn) {
      const pre = btn.parentElement.querySelector('pre');
      navigator.clipboard.writeText(pre.innerText.replace('Copy', '').trim());
      btn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> Copied!';
      setTimeout(() => { btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy'; }, 2000);
    }

    async function sendMessage() {
      const input = document.getElementById('user-input');
      const text = input.value.trim();
      if (!text) return;

      const welcomeCard = document.getElementById('welcome-card');
      if (welcomeCard) welcomeCard.remove();

      const container = document.getElementById('messages-container');

      // Append User Message
      const userDiv = document.createElement('div');
      userDiv.className = 'flex justify-end';
      userDiv.innerHTML = `
        <div class="chat-bubble-user p-4 text-sm text-white max-w-2xl leading-relaxed">
          ${text}
        </div>
      `;
      container.appendChild(userDiv);
      input.value = '';

      // Append Apex AI Thinking Placeholder
      const aiDiv = document.createElement('div');
      aiDiv.className = 'flex gap-3 items-start';
      const aiId = 'ai-msg-' + Date.now();
      aiDiv.innerHTML = `
        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0 mt-1 shadow-md">⚡</div>
        <div id="${aiId}" class="chat-bubble-ai p-4 text-sm text-slate-200 max-w-2xl leading-relaxed space-y-2">
          <div class="flex items-center gap-2 text-cyan-400 text-xs font-semibold">
            <i class="fa-solid fa-spinner fa-spin"></i> Apex AI Thinking...
          </div>
        </div>
      `;
      container.appendChild(aiDiv);
      container.scrollTop = container.scrollHeight;

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: text })
        });
        const data = await response.json();
        
        const aiMsgBox = document.getElementById(aiId);
        aiMsgBox.innerHTML = formatMarkdown(data.answer);

      } catch (err) {
        const aiMsgBox = document.getElementById(aiId);
        aiMsgBox.innerHTML = '<span class="text-rose-400 font-semibold">Error connecting to Apex AI server.</span>';
      }

      container.scrollTop = container.scrollHeight;
    }
  </script>
</body>
</html>
"""

class RAGRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/chat':
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8')
            data = json.loads(post_body)
            question = data.get('question', '')

            result = pipeline.query(question)

            response_data = {
                'question': question,
                'answer': result['answer']
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404)

def find_available_port(start_port=5000):
    port = start_port
    while port < start_port + 20:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    return start_port

def auto_open_url(url):
    try:
        if sys.platform == 'win32':
            os.system(f'start {url}')
        else:
            webbrowser.open(url)
    except Exception:
        pass

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    active_port = find_available_port(DEFAULT_PORT)
    url = f"http://localhost:{active_port}"

    threading.Timer(0.8, lambda: auto_open_url(url)).start()

    with socketserver.TCPServer(("", active_port), RAGRequestHandler) as httpd:
        print(f"\n============================================================")
        print(f"⚡ APEX AI LOCAL APP IS RUNNING!")
        print(f"👉 Open in your web browser: {url}")
        print(f"============================================================\n")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
