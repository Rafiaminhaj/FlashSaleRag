import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

from app.database.redis_client import redis_client, pool
from app.core.inventory import RedisInventoryManager
from app.ai.bot import get_ai_response

try:
    from app.core.rate_limiter import TokenBucketRateLimiter
except ImportError:
    from rate_limiter import TokenBucketRateLimiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.close()
    await pool.disconnect()

app = FastAPI(title="Flash Sale API", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=r"C:\Users\adiqu\.gemini\antigravity\brain\0633543a-e406-4c07-83cf-36041baa8e2b"), name="static")

inventory_manager = RedisInventoryManager(redis_client)
rate_limiter = TokenBucketRateLimiter(redis_client)

class PurchaseRequest(BaseModel):
    user_id: str
    quantity: int = 1

class SetStockRequest(BaseModel):
    quantity: int
    base_price: float

class ChatRequest(BaseModel):
    question: str

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultra-Concurrent Flash Market</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        body { 
            font-family: 'Outfit', sans-serif;
            cursor: crosshair;
        }

        /* Ambient Glow & Circuit Pattern Background */
        .ambient-mesh {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(circle at 15% 50%, rgba(245, 158, 11, 0.08), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(245, 158, 11, 0.05), transparent 25%);
            background-size: cover;
            z-index: 0;
            pointer-events: none;
        }
        
        .circuit-pattern {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: linear-gradient(rgba(245, 158, 11, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(245, 158, 11, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
            pointer-events: none;
        }

        .glass-card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(245, 158, 11, 0.2);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 30px 60px -12px rgba(245, 158, 11, 0.15);
            border-color: rgba(245, 158, 11, 0.5);
        }
        
        /* Watermark Backgrounds */
        .bg-watermark {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-size: cover;
            background-position: center;
            opacity: 0.25;
            z-index: 0;
            pointer-events: none;
            border-radius: inherit;
            mix-blend-mode: luminosity;
        }
        
        .card-content {
            position: relative;
            z-index: 10;
        }
        
        .flash-red { animation: textFlash 0.5s ease-in-out; }
        @keyframes textFlash { 0% { color: #ef4444; transform: scale(1.15); } 100% { color: inherit; transform: scale(1); } }

        .typing-indicator span {
            display: inline-block; width: 6px; height: 6px; background-color: #f59e0b; border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both; margin-right: 3px;
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.8);
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
        
        .chat-scroll::-webkit-scrollbar { width: 6px; }
        .chat-scroll::-webkit-scrollbar-track { background: transparent; }
        .chat-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        
        .animate-fade-in { animation: fadeIn 0.6s ease-out forwards; }
        @keyframes fadeIn { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }

        /* Cursor Particle */
        .cursor-particle {
            position: fixed;
            width: 4px;
            height: 4px;
            background-color: #f59e0b;
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            box-shadow: 0 0 10px #f59e0b, 0 0 20px #f59e0b;
            animation: particleFade 0.6s forwards;
        }
        @keyframes particleFade {
            0% { opacity: 1; transform: scale(1) translate(-50%, -50%); }
            100% { opacity: 0; transform: scale(2) translate(-50%, -50%); }
        }

        .metrics-shimmer {
            animation: metricsShimmer 1.5s ease-out infinite;
        }
        @keyframes metricsShimmer {
            0% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
            50% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.6); border-color: rgba(245, 158, 11, 0.8); }
            100% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
        }
        
        input, button { cursor: inherit !important; }

    </style>
</head>
<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-zinc-950 min-h-screen text-slate-200 p-4 md:p-8">
    <div class="circuit-pattern"></div>
    <div class="ambient-mesh"></div>

    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-3 pointer-events-none"></div>

    <div class="max-w-7xl mx-auto relative z-10">
        <header class="text-center mb-12">
            <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500 mb-4 pb-2 drop-shadow-md">
                ULTRA-CONCURRENT ⚡ FLASH MARKET
            </h1>
            <p class="text-lg text-amber-500/70 font-bold max-w-2xl mx-auto uppercase tracking-widest text-sm drop-shadow-sm">High-Performance Inventory & Support for Major Sales</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Admin Setup -->
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden">
                <div class="bg-watermark" style="background-image: url('/static/warehouse_bg_1779274543869.png'); opacity: 0.15;"></div>
                <div class="card-content flex flex-col h-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-amber-500/10 rounded-xl text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]"><i data-lucide="settings"></i></div>
                        <h2 class="text-xl font-bold text-white">Stock Control Center</h2>
                    </div>
                    
                    <div class="space-y-5 flex-grow">
                        <div>
                            <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Product ID</label>
                            <input type="text" id="admin-product" placeholder="e.g. iphone_15" class="w-full bg-slate-950/80 border border-slate-700 rounded-xl p-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-100 font-medium shadow-inner transition">
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Capacity</label>
                                <input type="number" id="admin-qty" placeholder="100" class="w-full bg-slate-950/80 border border-slate-700 rounded-xl p-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-100 font-medium shadow-inner transition">
                            </div>
                            <div>
                                <label class="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Base Price (₹)</label>
                                <input type="number" id="admin-price" placeholder="69999" class="w-full bg-slate-950/80 border border-slate-700 rounded-xl p-3 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-100 font-medium shadow-inner transition">
                            </div>
                        </div>
                    </div>
                    
                    <button onclick="setStock()" class="mt-8 w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-slate-950 font-extrabold py-4 px-4 rounded-xl shadow-[0_0_20px_rgba(245,158,11,0.4)] transition-all active:scale-95 flex justify-center items-center gap-2">
                        <i data-lucide="database" class="w-5 h-5"></i> Initialize System
                    </button>
                </div>
            </div>

            <!-- Live Showcase -->
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden min-h-[400px]">
                <div class="bg-watermark" style="background-image: url('/static/storefront_bg_1779274559400.png'); opacity: 0.15;"></div>
                <div class="card-content flex flex-col h-full w-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-amber-500/10 rounded-xl text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]"><i data-lucide="shopping-cart"></i></div>
                        <h2 class="text-xl font-bold text-white">Live Product Showcase</h2>
                    </div>
                    
                    <div class="flex-grow flex flex-col justify-center items-center text-center py-2 w-full">
                        
                        <!-- EMPTY STATE -->
                        <div id="empty-state" class="flex flex-col items-center justify-center space-y-4 animate-fade-in absolute inset-0 pt-10">
                            <div class="w-16 h-16 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-slate-500 shadow-inner">
                                <i data-lucide="package-x" class="w-8 h-8"></i>
                            </div>
                            <p class="text-sm font-medium text-slate-400 max-w-[280px] leading-relaxed">
                                ⚠️ No active flash sale.<br>Please initialize a product from the Stock Control Center to launch.
                            </p>
                        </div>

                        <!-- LIVE STATE -->
                        <div id="live-state" class="hidden flex-col items-center justify-center w-full animate-fade-in h-full">
                            <h3 class="text-3xl font-extrabold text-white tracking-tight capitalize mb-1" id="store-title">--</h3>
                            
                            <div id="sale-timer" class="text-sm font-bold text-slate-400 mb-2 uppercase tracking-widest bg-slate-900 px-3 py-1 rounded-full border border-slate-700 shadow-inner transition-colors">
                                --:--
                            </div>
                            
                            <div class="flex flex-col items-center justify-center min-h-[90px]">
                                <div class="text-6xl font-black text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.3)] transition-colors duration-300" id="store-price">₹--</div>
                                
                                <div id="surge-badge" class="hidden mt-3 bg-red-900/50 text-red-400 text-xs font-bold px-4 py-1.5 rounded-full border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)] flex items-center gap-1.5 animate-pulse">
                                    <i data-lucide="trending-up" class="w-3.5 h-3.5"></i> SURGE ACTIVE (+10%)
                                </div>
                            </div>
                            
                            <div class="w-full max-w-xs mt-6">
                                <div class="flex justify-between text-sm font-bold text-slate-400 mb-2 uppercase tracking-wider">
                                    <span>Stock Level</span>
                                    <span class="text-amber-400 text-lg transition-all" id="store-stock">--</span>
                                </div>
                                <div class="w-full bg-slate-900 rounded-full h-2 overflow-hidden shadow-inner border border-slate-800">
                                    <div id="stock-bar" class="bg-amber-500 h-2 rounded-full transition-all duration-700 ease-out shadow-[0_0_10px_rgba(245,158,11,0.8)]" style="width: 100%"></div>
                                </div>
                            </div>
                        </div>

                    </div>

                    <div class="mt-auto space-y-3 pt-4">
                        <input type="text" id="buy-user" readonly class="hidden">
                        
                        <button onclick="buyNow()" id="buy-btn" disabled class="w-full bg-slate-900/80 text-slate-500 border border-slate-800 font-bold py-4 px-4 rounded-xl transition-all flex justify-center items-center gap-2 cursor-not-allowed">
                            <i data-lucide="clock" class="w-5 h-5"></i> Pending System Initialization
                        </button>
                    </div>
                </div>
            </div>

            <!-- AI Chat -->
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden">
                <div class="bg-watermark" style="background-image: url('/static/ai_bot_bg_1779274574879.png'); opacity: 0.15;"></div>
                
                <!-- Glowing Cyberpunk Robot Avatar Watermark -->
                <div class="absolute inset-0 flex items-center justify-center opacity-[0.06] pointer-events-none z-0">
                    <svg xmlns="http://www.w3.org/2000/svg" width="280" height="280" viewBox="0 0 24 24" fill="none" stroke="#FF9F00" stroke-width="0.75" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 15px #FF9F00);">
                        <rect x="3" y="11" width="18" height="10" rx="2"></rect>
                        <circle cx="12" cy="5" r="2"></circle>
                        <path d="M12 7v4"></path>
                        <line x1="8" y1="16" x2="8.01" y2="16"></line>
                        <line x1="16" y1="16" x2="16.01" y2="16"></line>
                        <path d="M12 11v10" stroke-width="0.2" stroke-dasharray="1 1"></path>
                        <circle cx="12" cy="16" r="6" stroke-width="0.2"></circle>
                        <path d="M2 14h1"></path>
                        <path d="M21 14h1"></path>
                    </svg>
                </div>

                <div class="card-content flex flex-col h-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-amber-500/10 rounded-xl text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]"><i data-lucide="bot"></i></div>
                        <h2 class="text-xl font-bold text-white">AI Support Concierge</h2>
                    </div>
                    
                    <div id="chat-box" class="flex-grow bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 h-40 overflow-y-auto mb-4 space-y-4 chat-scroll scroll-smooth shadow-inner">
                        <div class="flex items-start gap-3">
                            <div class="w-8 h-8 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center flex-shrink-0 shadow-[0_0_10px_rgba(245,158,11,0.2)]"><i data-lucide="sparkles" class="w-4 h-4 text-amber-400"></i></div>
                            <div class="bg-slate-900/90 border border-amber-500/20 text-slate-200 text-sm py-2.5 px-4 rounded-2xl rounded-tl-sm max-w-[85%] leading-relaxed font-medium shadow-sm">
                                Hi! I'm your Flash Sale Assistant. Need help with warranty, returns, or cart expiry rules?
                            </div>
                        </div>
                    </div>

                    <div class="flex gap-2 mb-4">
                        <input type="text" id="chat-input" placeholder="Type a question..." onkeypress="handleChat(event)" class="flex-grow bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none text-slate-100 transition font-medium shadow-inner">
                        <button onclick="sendMessage()" class="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 p-3 rounded-xl transition-all shadow-[0_0_15px_rgba(245,158,11,0.4)] active:scale-95 flex items-center justify-center">
                            <i data-lucide="send" class="w-5 h-5 font-bold"></i>
                        </button>
                    </div>

                    <!-- AI Workflow Automation Log -->
                    <div class="flex flex-col bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-inner h-24">
                        <div class="bg-slate-900/80 border-b border-slate-800 py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <i data-lucide="cpu" class="w-3.5 h-3.5 text-cyan-400"></i> ⚙️ AI WORKFLOW AUTOMATION
                        </div>
                        <div id="ai-workflow-logs" class="p-3 overflow-y-auto chat-scroll font-mono text-[10px] space-y-1 flex-grow">
                            <div class="text-slate-600 italic">Listening for system events...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- System Analytics -->
            <div id="analytics-card" class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden">
                <div class="bg-watermark" style="background-image: url('/static/network_mesh_bg_1779274591974.png'); opacity: 0.2;"></div>
                <div class="card-content flex flex-col h-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-emerald-500/10 rounded-xl text-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.2)]"><i data-lucide="activity"></i></div>
                        <h2 class="text-xl font-bold text-white">System Metrics Command</h2>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4 flex-grow mb-6">
                        <div class="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 flex flex-col justify-center items-center text-center shadow-inner">
                            <span class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Live Traffic</span>
                            <span id="metric-rps" class="text-3xl font-black text-amber-400 flex items-baseline gap-1">0 <span class="text-sm text-slate-500 font-bold">RPS</span></span>
                        </div>
                        <div class="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 flex flex-col justify-center items-center text-center shadow-inner">
                            <span class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Avg Latency</span>
                            <span id="metric-latency" class="text-3xl font-black text-amber-400 flex items-baseline gap-1">0.0 <span class="text-sm text-slate-500 font-bold">ms</span></span>
                        </div>
                        <div class="bg-red-950/30 border border-red-500/20 rounded-2xl p-4 flex flex-col justify-center items-center text-center col-span-2 shadow-inner">
                            <span class="text-red-400/80 text-[11px] font-bold uppercase tracking-widest mb-1">Blocked Spam Requests</span>
                            <span id="metric-blocked" class="text-4xl font-black text-red-500 drop-shadow-[0_0_10px_rgba(239,68,68,0.5)]">0</span>
                        </div>
                    </div>
                    
                    <button onclick="simulateTrafficSpike()" class="w-full bg-slate-900/80 hover:bg-slate-800 text-amber-400 font-bold py-4 px-4 rounded-xl border border-amber-500/30 shadow-[0_0_15px_rgba(245,158,11,0.1)] transition-all active:scale-95 flex justify-center items-center gap-2 hover:shadow-[0_0_20px_rgba(245,158,11,0.3)] mb-4">
                        <i data-lucide="zap" class="w-5 h-5 text-amber-400 fill-amber-400/20"></i> Simulate 100x Traffic Spike
                    </button>
                    
                    <!-- Real-Time Transaction Logs -->
                    <div class="flex flex-col bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-inner h-32">
                        <div class="bg-slate-900/80 border-b border-slate-800 py-2 px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <i data-lucide="terminal" class="w-3.5 h-3.5 text-emerald-400"></i> ⚡ REAL-TIME TRANSACTION LOGS
                        </div>
                        <div id="transaction-logs" class="p-3 overflow-y-auto chat-scroll font-mono text-[11px] space-y-1 flex-grow">
                            <div class="text-slate-600 italic">Waiting for system traffic...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        document.getElementById('buy-user').value = 'uid_' + Math.random().toString(36).substr(2, 8).toLowerCase();
        
        let currentProductId = null;
        let initialStock = 0;
        let prevStock = 0;
        let stockAlertTriggered = false;
        
        function logAiWorkflow(msg, color) {
            const aiConsole = document.getElementById('ai-workflow-logs');
            if (aiConsole.innerHTML.includes('Listening for system events')) {
                aiConsole.innerHTML = '';
            }
            let colorClass = '';
            if (color === 'cyan') colorClass = 'text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]';
            else if (color === 'amber') colorClass = 'text-amber-500 drop-shadow-[0_0_5px_rgba(245,158,11,0.5)]';
            else if (color === 'red') colorClass = 'text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]';
            
            const lines = aiConsole.querySelectorAll('div');
            if (lines.length > 0 && lines[lines.length-1].textContent === msg) return;
            
            aiConsole.innerHTML += `<div class="${colorClass} mb-1">${msg}</div>`;
            aiConsole.scrollTop = aiConsole.scrollHeight;
        }

        // Timer Logic
        let countdown = 10;
        let saleStarted = false;
        let timerInterval = null;
        let pollInterval = null;

        function startTimer() {
            countdown = 10;
            saleStarted = false;
            if(timerInterval) clearInterval(timerInterval);
            
            const timerEl = document.getElementById('sale-timer');
            timerEl.classList.replace("text-emerald-400", "text-slate-400");
            timerEl.classList.replace("bg-emerald-900/30", "bg-slate-900");
            timerEl.classList.replace("border-emerald-500/30", "border-slate-700");
            timerEl.classList.remove("animate-pulse", "shadow-[0_0_15px_rgba(52,211,153,0.3)]");
            timerEl.textContent = `00:10`;
            
            const btn = document.getElementById('buy-btn');
            btn.disabled = true;
            btn.className = 'w-full bg-slate-900/80 text-slate-500 border border-slate-800 font-bold py-4 px-4 rounded-xl transition-all flex justify-center items-center gap-2 cursor-not-allowed';
            btn.innerHTML = `<i data-lucide="clock" class="w-5 h-5"></i> Sale Starts in 00:10`;
            lucide.createIcons({root: btn});

            timerInterval = setInterval(() => {
                if (countdown > 0) {
                    countdown--;
                    document.getElementById('sale-timer').textContent = `00:${countdown.toString().padStart(2, '0')}`;
                    btn.innerHTML = `<i data-lucide="clock" class="w-5 h-5"></i> Sale Starts in 00:${countdown.toString().padStart(2, '0')}`;
                    lucide.createIcons({root: btn});
                } else if (!saleStarted) {
                    saleStarted = true;
                    clearInterval(timerInterval);
                    timerEl.textContent = "SALE LIVE";
                    timerEl.classList.replace("text-slate-400", "text-emerald-400");
                    timerEl.classList.replace("bg-slate-900", "bg-emerald-900/30");
                    timerEl.classList.replace("border-slate-700", "border-emerald-500/30");
                    timerEl.classList.add("animate-pulse", "shadow-[0_0_15px_rgba(52,211,153,0.3)]");
                    
                    if (prevStock > 0) {
                        btn.disabled = false;
                        btn.className = 'w-full bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-extrabold py-4 px-4 rounded-xl shadow-[0_0_20px_rgba(52,211,153,0.4)] transition-all active:scale-95 flex justify-center items-center gap-2 cursor-pointer border border-emerald-400/50';
                        btn.innerHTML = `<i data-lucide="credit-card" class="w-5 h-5"></i> Buy Now (10-min reservation)`;
                        lucide.createIcons({root: btn});
                    }
                    
                    fetchStatus();
                }
            }, 1000);
        }

        // Analytics Logic
        let totalBlocked = 0;
        let currentRps = 0;

        setInterval(() => {
            if (currentRps < 5) currentRps = Math.floor(Math.random() * 8);
            else currentRps = Math.max(0, currentRps - Math.floor(Math.random() * 20));
            
            document.getElementById('metric-rps').innerHTML = `${currentRps} <span class="text-sm text-slate-500 font-bold">RPS</span>`;
            document.getElementById('metric-latency').innerHTML = `${(Math.random() * 3 + 2).toFixed(1)} <span class="text-sm text-slate-500 font-bold">ms</span>`;
        }, 1000);

        async function simulateTrafficSpike() {
            if (!currentProductId) {
                showToast("Initialize a product first!", "error");
                return;
            }
            if (!saleStarted) {
                showToast("Sale hasn't started!", "error");
                return;
            }
            if (prevStock <= 0) {
                showToast("Already sold out!", "error");
                return;
            }
            
            showToast("System experiencing high traffic! Launching 100 requests...", "info");
            currentRps += 100;
            document.getElementById('metric-rps').innerHTML = `${currentRps} <span class="text-sm text-slate-500 font-bold">RPS</span>`;
            
            // Add pulse shimmer to analytics card
            const card = document.getElementById('analytics-card');
            card.classList.add('metrics-shimmer');
            setTimeout(() => card.classList.remove('metrics-shimmer'), 3000);
            
            const logConsole = document.getElementById('transaction-logs');
            if(logConsole.innerHTML.includes('Waiting for system traffic')) {
                logConsole.innerHTML = '';
            }

            let promises = [];
            for(let i = 0; i < 100; i++) {
                let uid = 'bot_' + Math.random().toString(36).substr(2, 6).toUpperCase();
                let reqPromise = fetch(`/purchase/${currentProductId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: uid, quantity: 1 })
                }).then(res => {
                    const latency = Math.floor(Math.random() * 5) + 1;
                    if (res.status === 429) {
                        logConsole.innerHTML += `<div class="text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]">🔴 ${uid}: 429 Rate-Limited (TokenBucket Blocked)</div>`;
                        logAiWorkflow('[AI Automation] 🛡️ Fraud Guard: Anomalous high-burst signature captured. Fraud mitigation workflow initiated.', 'red');
                    } else if (res.ok) {
                        logConsole.innerHTML += `<div class="text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.5)]">🟢 ${uid}: Order Confirmed [Latency: ${latency}ms]</div>`;
                        logAiWorkflow('[AI Automation] 💌 Order confirmed. Dispatched localized smart shipping agent pipeline.', 'cyan');
                    }
                    logConsole.scrollTop = logConsole.scrollHeight;
                    return res;
                });
                promises.push(reqPromise);
            }
            
            const results = await Promise.all(promises);
            let successCount = 0;
            let blockedCount = 0;
            
            for (let res of results) {
                if (res.status === 429) blockedCount++;
                else if (res.ok) successCount++;
            }
            
            totalBlocked += blockedCount;
            document.getElementById('metric-blocked').textContent = totalBlocked;
            
            showToast(`Spike Finished: ${successCount} Success, ${blockedCount} Blocked`, 'info');
            fetchStatus();
        }

        function showToast(msg, type='info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            
            const styles = {
                success: 'bg-emerald-950/90 border-l-4 border-emerald-500 text-slate-200',
                error: 'bg-red-950/90 border-l-4 border-red-500 text-slate-200',
                info: 'bg-blue-950/90 border-l-4 border-blue-500 text-slate-200'
            };
            
            const icons = {
                success: '<i data-lucide="check-circle" class="text-emerald-500 w-5 h-5"></i>',
                error: '<i data-lucide="alert-triangle" class="text-red-500 w-5 h-5"></i>',
                info: '<i data-lucide="info" class="text-blue-500 w-5 h-5"></i>'
            };

            toast.className = `p-4 rounded-xl transform transition-all duration-400 translate-x-full pointer-events-auto flex items-center gap-3 min-w-[300px] font-bold shadow-2xl border border-slate-800 backdrop-blur-md ${styles[type]}`;
            toast.innerHTML = `${icons[type]}<span>${msg}</span>`;
            
            container.appendChild(toast);
            lucide.createIcons({root: toast});
            
            requestAnimationFrame(() => toast.classList.remove('translate-x-full'));
            setTimeout(() => {
                toast.classList.add('translate-x-full');
                toast.classList.add('opacity-0');
                setTimeout(() => toast.remove(), 400);
            }, 3500);
        }

        async function fetchStatus() {
            if (!currentProductId) return;
            try {
                const res = await fetch(`/status/${currentProductId}`);
                if (res.ok) {
                    const data = await res.json();
                    const priceEl = document.getElementById('store-price');
                    const stockEl = document.getElementById('store-stock');
                    
                    priceEl.textContent = `₹${data.price.toLocaleString('en-IN')}`;
                    
                    if (prevStock !== data.stock) {
                        stockEl.textContent = data.stock;
                        stockEl.classList.remove('flash-red');
                        void stockEl.offsetWidth; 
                        stockEl.classList.add('flash-red');
                        prevStock = data.stock;
                    } else {
                        stockEl.textContent = data.stock;
                    }
                    
                    const surgeBadge = document.getElementById('surge-badge');
                    if (data.surge) {
                        surgeBadge.classList.remove('hidden');
                        priceEl.classList.replace('text-amber-400', 'text-red-500');
                        priceEl.classList.replace('drop-shadow-[0_0_10px_rgba(245,158,11,0.3)]', 'drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]');
                    } else {
                        surgeBadge.classList.add('hidden');
                        priceEl.classList.replace('text-red-500', 'text-amber-400');
                        priceEl.classList.replace('drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]', 'drop-shadow-[0_0_10px_rgba(245,158,11,0.3)]');
                    }

                    const percent = Math.max(0, (data.stock / initialStock) * 100);
                    const bar = document.getElementById('stock-bar');
                    bar.style.width = `${percent}%`;
                    
                    if (percent <= 20) bar.className = 'bg-red-500 h-2 rounded-full transition-all duration-500 ease-out shadow-[0_0_15px_rgba(239,68,68,0.8)]';
                    else bar.className = 'bg-amber-500 h-2 rounded-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(245,158,11,0.8)]';
                    
                    if (percent < 10 && data.stock > 0 && !stockAlertTriggered) {
                        stockAlertTriggered = true;
                        logAiWorkflow('[AI Automation] 🤖 Critical Stock Threshold! Auto-generated an external supply-chain restock request.', 'amber');
                    }
                    
                    const btn = document.getElementById('buy-btn');
                    if (data.stock <= 0) {
                        btn.disabled = true;
                        btn.className = 'w-full bg-slate-900/80 text-slate-500 border border-slate-800 font-bold py-4 px-4 rounded-xl flex justify-center items-center gap-2 cursor-not-allowed';
                        btn.innerHTML = '<i data-lucide="x-circle" class="w-5 h-5"></i> Sold Out';
                        lucide.createIcons({root: btn});
                    }
                }
            } catch (e) {}
        }

        async function setStock() {
            const pidInput = document.getElementById('admin-product');
            const qtyInput = document.getElementById('admin-qty');
            const priceInput = document.getElementById('admin-price');
            
            const pid = pidInput.value.trim() || 'iphone_15';
            const qty = qtyInput.value.trim() || '100';
            const price = priceInput.value.trim() || '69999';
            
            currentProductId = pid;
            initialStock = parseInt(qty);
            prevStock = initialStock;
            stockAlertTriggered = false;
            
            document.getElementById('store-title').textContent = pid.replace(/_/g, ' ');
            document.getElementById('store-price').textContent = `₹${parseFloat(price).toLocaleString('en-IN')}`;
            document.getElementById('store-stock').textContent = initialStock;
            
            try {
                const res = await fetch(`/set_stock/${pid}`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-Admin-Token': 'FlipkartGrid2026Secret'
                    },
                    body: JSON.stringify({ quantity: initialStock, base_price: parseFloat(price) })
                });
                if (res.ok) {
                    showToast('Stock Initialized successfully!', 'success');
                    
                    // Switch UI
                    document.getElementById('empty-state').classList.add('hidden');
                    document.getElementById('empty-state').classList.remove('flex');
                    
                    const liveState = document.getElementById('live-state');
                    liveState.classList.remove('hidden');
                    liveState.classList.add('flex');
                    
                    startTimer(); 
                    if (pollInterval) clearInterval(pollInterval);
                    pollInterval = setInterval(fetchStatus, 1500);
                    fetchStatus();
                } else showToast('Initialization Failed. Check Admin Token.', 'error');
            } catch (e) { showToast('Connection Error', 'error'); }
        }

        async function buyNow() {
            if (!currentProductId || !saleStarted) return;
            const uid = document.getElementById('buy-user').value;
            try {
                const res = await fetch(`/purchase/${currentProductId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: uid, quantity: 1 })
                });
                const data = await res.json();
                
                if (res.ok) {
                    showToast(`Purchase Successful: ₹${data.final_price.toLocaleString('en-IN')}`, 'success');
                    if (data.surge_active) showToast('Surge Pricing active (+10%)', 'info');
                    logAiWorkflow('[AI Automation] 💌 Order confirmed. Dispatched localized smart shipping agent pipeline.', 'cyan');
                    fetchStatus();
                } else {
                    if (res.status === 429) {
                        logAiWorkflow('[AI Automation] 🛡️ Fraud Guard: Anomalous high-burst signature captured. Fraud mitigation workflow initiated.', 'red');
                    }
                    showToast(data.detail || 'Purchase Failed', 'error');
                }
            } catch (e) { showToast('Connection Error', 'error'); }
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if (!msg) return;
            
            const chatBox = document.getElementById('chat-box');
            
            chatBox.innerHTML += `
                <div class="flex items-start gap-3 justify-end">
                    <div class="bg-amber-500/20 text-amber-100 border border-amber-500/30 text-sm py-2.5 px-4 rounded-2xl rounded-tr-sm max-w-[85%] leading-relaxed font-bold shadow-sm backdrop-blur-md">
                        ${msg}
                    </div>
                    <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0 shadow-sm"><i data-lucide="user" class="w-4 h-4 text-slate-400"></i></div>
                </div>`;
            input.value = '';
            
            const loadingId = 'loading-' + Date.now();
            chatBox.innerHTML += `
                <div id="${loadingId}" class="flex items-start gap-3">
                    <div class="w-8 h-8 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center flex-shrink-0 shadow-[0_0_10px_rgba(245,158,11,0.2)]"><i data-lucide="bot" class="w-4 h-4 text-amber-400"></i></div>
                    <div class="bg-slate-900/90 border border-amber-500/20 py-3 px-4 rounded-2xl rounded-tl-sm typing-indicator shadow-sm">
                        <span></span><span></span><span></span>
                    </div>
                </div>`;
            
            lucide.createIcons({root: chatBox});
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch(`/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: msg })
                });
                const data = await res.json();
                
                document.getElementById(loadingId).remove();
                
                chatBox.innerHTML += `
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center flex-shrink-0 shadow-[0_0_10px_rgba(245,158,11,0.2)]"><i data-lucide="sparkles" class="w-4 h-4 text-amber-400"></i></div>
                        <div class="bg-slate-900/90 border border-amber-500/20 text-slate-200 text-sm py-2.5 px-4 rounded-2xl rounded-tl-sm max-w-[85%] leading-relaxed font-medium shadow-sm">
                            ${data.answer}
                        </div>
                    </div>`;
                lucide.createIcons({root: chatBox});
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (e) {
                document.getElementById(loadingId).remove();
                showToast('Chat Service Offline', 'error');
            }
        }

        function handleChat(e) { if (e.key === 'Enter') sendMessage(); }

        // Custom Cursor Trail Particle Generator
        document.addEventListener('mousemove', function(e) {
            const particle = document.createElement('div');
            particle.className = 'cursor-particle';
            particle.style.left = e.clientX + 'px';
            particle.style.top = e.clientY + 'px';
            document.body.appendChild(particle);
            setTimeout(() => { particle.remove(); }, 600);
        });
    </script>
</body>
</html>
"""

@app.get("/")
async def serve_dashboard():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/status/{product_id}")
async def get_status(product_id: str):
    status = await inventory_manager.get_status(product_id)
    if not status:
        raise HTTPException(status_code=404, detail="Product not found. Please set inventory first.")
    return status

async def verify_admin_token(x_admin_token: str = Header(default=None)):
    if x_admin_token != "FlipkartGrid2026Secret":
        raise HTTPException(status_code=401, detail="Unauthorized Admin Token")

@app.post("/set_stock/{product_id}", dependencies=[Depends(verify_admin_token)])
async def set_stock(product_id: str, request: SetStockRequest):
    await inventory_manager.set_inventory(product_id, request.quantity, request.base_price)
    return {"message": "Success"}

@app.post("/chat")
async def chat(request: ChatRequest):
    answer = await get_ai_response(request.question)
    return {"answer": answer}

@app.post("/purchase/{product_id}")
async def purchase(product_id: str, request: PurchaseRequest):
    is_allowed = await rate_limiter.is_allowed(request.user_id)
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    result = await inventory_manager.purchase_item(
        product_id=product_id,
        quantity=request.quantity
    )
    return {
        "message": "Purchase successful!",
        "product_id": product_id,
        **result
    }
