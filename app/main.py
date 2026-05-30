import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        body { 
            font-family: 'Outfit', sans-serif;
            cursor: crosshair;
            scroll-behavior: smooth;
        }

        /* Hide Vercel Toolbar Widget */
        vercel-live-feedback, 
        vercel-toolbar, 
        #vercel-toolbar {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Ambient Glow & Circuit Pattern Background */
        .ambient-mesh {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(circle at 15% 50%, rgba(245, 158, 11, 0.08), transparent 30%),
                radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.05), transparent 30%),
                radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.06), transparent 30%);
            background-size: cover;
            z-index: 0;
            pointer-events: none;
            animation: ambientGlowPulse 8s ease-in-out infinite alternate;
        }
        @keyframes ambientGlowPulse {
            0% { opacity: 0.7; transform: scale(1); }
            100% { opacity: 1; transform: scale(1.05); }
        }
        
        .circuit-pattern {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: linear-gradient(rgba(245, 158, 11, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(245, 158, 11, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
            pointer-events: none;
            animation: panGrid 60s linear infinite;
        }
        @keyframes panGrid {
            0% { background-position: 0 0; }
            100% { background-position: 100% 100%; }
        }
        
        .floating-particles {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: 0;
            pointer-events: none;
            background-image: radial-gradient(rgba(56, 189, 248, 0.4) 1px, transparent 1px), radial-gradient(rgba(139, 92, 246, 0.3) 1px, transparent 1px);
            background-size: 80px 80px, 120px 120px;
            background-position: 0 0, 40px 40px;
            animation: floatParticles 20s linear infinite;
        }
        @keyframes floatParticles {
            0% { transform: translateY(0px) rotate(0deg); opacity: 0.3; }
            50% { opacity: 0.6; }
            100% { transform: translateY(-80px) rotate(1deg); opacity: 0.3; }
        }

        .glass-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.75), rgba(2, 6, 23, 0.85));
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(245, 158, 11, 0.15);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.05);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .glass-card:hover {
            transform: translateY(-4px) scale(1.005);
            box-shadow: 0 35px 60px -15px rgba(245, 158, 11, 0.12), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            border-color: rgba(245, 158, 11, 0.4);
        }
        
        .bg-watermark {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-size: cover;
            background-position: center;
            opacity: 0.15;
            z-index: 0;
            pointer-events: none;
            border-radius: inherit;
            mix-blend-mode: luminosity;
            transition: opacity 0.5s ease;
        }
        .glass-card:hover .bg-watermark {
            opacity: 0.25;
        }
        
        .card-content {
            position: relative;
            z-index: 10;
        }
        
        .flash-red { animation: textFlash 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
        @keyframes textFlash { 0% { color: #ef4444; transform: scale(1.2); } 100% { color: inherit; transform: scale(1); } }

        .typing-indicator span {
            display: inline-block; width: 6px; height: 6px; background-color: #f59e0b; border-radius: 50%;
            animation: bounce 1.4s infinite cubic-bezier(0.4, 0, 0.2, 1) both; margin-right: 3px;
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.8);
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
        
        .chat-scroll::-webkit-scrollbar { width: 4px; }
        .chat-scroll::-webkit-scrollbar-track { background: transparent; }
        .chat-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        
        .animate-fade-in { opacity: 0; animation: fadeInSpring 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes fadeInSpring { 0% { opacity: 0; transform: translateY(20px) scale(0.98); } 100% { opacity: 1; transform: translateY(0) scale(1); } }

        .slide-in-toast { animation: toastSlide 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
        @keyframes toastSlide { 0% { opacity: 0; transform: translateX(100%) scale(0.9); } 100% { opacity: 1; transform: translateX(0) scale(1); } }
        
        .slide-out-toast { animation: toastSlideOut 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes toastSlideOut { 0% { opacity: 1; transform: translateX(0) scale(1); } 100% { opacity: 0; transform: translateX(100%) scale(0.9); } }

        .log-slide-in { animation: logSlide 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        @keyframes logSlide { 0% { opacity: 0; transform: translateX(-10px); } 100% { opacity: 1; transform: translateX(0); } }

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
            animation: particleFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes particleFade {
            0% { opacity: 1; transform: scale(1) translate(-50%, -50%); }
            100% { opacity: 0; transform: scale(2.5) translate(-50%, -50%); }
        }

        .metrics-shimmer {
            animation: metricsShimmer 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }
        @keyframes metricsShimmer {
            0% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
            50% { box-shadow: 0 0 40px rgba(245, 158, 11, 0.6); border-color: rgba(245, 158, 11, 0.8); transform: scale(1.02); }
            100% { box-shadow: 0 0 10px rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }
        }
        
        input, button { cursor: inherit !important; }

        /* Architecture Modal Styles */
        #arch-modal {
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            background: rgba(2, 6, 23, 0.92);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1);
            z-index: 1000;
        }
        #arch-modal.active {
            opacity: 1;
            pointer-events: auto;
        }
        #arch-content {
            transform: scale(0.92) translateY(30px);
            opacity: 0;
            transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(2, 6, 23, 0.98));
            border: 1px solid rgba(139, 92, 246, 0.4);
            box-shadow: 0 0 60px rgba(139, 92, 246, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        #arch-modal.active #arch-content {
            transform: scale(1) translateY(0);
            opacity: 1;
        }
        
        .arch-node {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(56, 189, 248, 0.25);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
        }
        .arch-node:hover {
            transform: translateY(-8px) scale(1.04);
            border-color: rgba(139, 92, 246, 0.8);
            box-shadow: 0 20px 40px -10px rgba(139, 92, 246, 0.6), 0 0 25px rgba(56, 189, 248, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            z-index: 10;
        }
        
        .ai-pulse {
            animation: aiPulseAnim 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
        }
        @keyframes aiPulseAnim {
            0% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); }
            100% { box-shadow: 0 0 45px rgba(239, 68, 68, 0.8); border-color: rgba(239, 68, 68, 1); transform: scale(1.02); }
        }
        
        .connector-down {
            position: relative;
            width: 2px;
            height: 35px;
            background: linear-gradient(to bottom, rgba(56, 189, 248, 0.6), rgba(139, 92, 246, 0.6));
            margin: 0 auto;
            overflow: hidden;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
        }
        .particle-down {
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 4px;
            height: 16px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 0 20px 4px #38bdf8, 0 0 30px 4px #8b5cf6;
            animation: flowDown 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }
        .particle-down:nth-child(2) { animation-delay: 0.6s; }
        
        @keyframes flowDown {
            0% { top: -20px; opacity: 0; }
            15% { opacity: 1; }
            85% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
        }

        /* Auto-Scaling Engine Animations */
        .server-node {
            transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            animation: nodeSpawn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        @keyframes nodeSpawn {
            0% { opacity: 0; transform: scale(0.3) translateY(30px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        .server-healthy {
            box-shadow: 0 0 15px rgba(52, 211, 153, 0.4);
            border-color: rgba(52, 211, 153, 0.8);
        }
        .server-warning {
            box-shadow: 0 0 25px rgba(245, 158, 11, 0.6);
            border-color: rgba(245, 158, 11, 0.9);
            animation: warnPulse 1s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
        }
        .server-error {
            box-shadow: 0 0 35px rgba(239, 68, 68, 0.9);
            border-color: rgba(239, 68, 68, 1);
            animation: errorShake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) infinite;
        }
        @keyframes warnPulse {
            0% { box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); transform: scale(1); }
            100% { box-shadow: 0 0 40px rgba(245, 158, 11, 0.9); transform: scale(1.05); }
        }
        @keyframes errorShake {
            0%, 100% { transform: translateX(0); }
            20% { transform: translateX(-3px) rotate(-2deg); }
            40% { transform: translateX(3px) rotate(2deg); }
            60% { transform: translateX(-3px) rotate(-2deg); }
            80% { transform: translateX(3px) rotate(2deg); }
        }
        .incident-glow-red {
            animation: incidentGlowRed 2.5s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes incidentGlowRed {
            0% { box-shadow: inset 0 0 120px rgba(239, 68, 68, 0.4); border-color: rgba(239, 68, 68, 0.9); transform: scale(1.01); }
            100% { box-shadow: inset 0 0 0 rgba(239, 68, 68, 0); border-color: rgba(245, 158, 11, 0.2); transform: scale(1); }
        }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-950 via-slate-900 to-zinc-950 min-h-screen text-slate-200 p-4 md:p-8">
    <div class="circuit-pattern"></div>
    <div class="ambient-mesh"></div>
    <div class="floating-particles"></div>

    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-3 pointer-events-none"></div>

    <div class="max-w-7xl mx-auto relative z-10">
        <header class="text-center mb-12">
            <h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500 mb-4 pb-2 drop-shadow-md">
                ULTRA-CONCURRENT ⚡ FLASH MARKET
            </h1>
            <p class="text-lg text-amber-500/70 font-bold max-w-2xl mx-auto uppercase tracking-widest text-sm drop-shadow-sm">High-Performance Inventory & Support for Major Sales</p>
            
            <div class="mt-5 flex items-center justify-center gap-2.5 max-w-2xl mx-auto animate-fade-in opacity-0" style="animation-delay: 0.2s; animation-fill-mode: forwards;">
                <div class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
                </div>
                <p class="text-xs font-bold tracking-[0.15em] uppercase text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]">
                    Built to simulate Flipkart/Amazon-scale flash-sale infrastructure under extreme concurrent load.
                </p>
            </div>
            
            <button onclick="openArchModal()" class="mt-6 mx-auto bg-slate-900/80 hover:bg-slate-800 border border-purple-500/40 text-purple-300 font-bold py-3 px-8 rounded-full shadow-[0_0_20px_rgba(139,92,246,0.2)] transition-all flex items-center gap-2 hover:shadow-[0_0_35px_rgba(139,92,246,0.5)] hover:-translate-y-1 hover:border-purple-400">
                <i data-lucide="satellite-dish" class="w-5 h-5"></i> View System Architecture
            </button>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Admin Setup -->
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden animate-fade-in opacity-0" style="animation-delay: 0.1s;">
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
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden min-h-[400px] animate-fade-in opacity-0" style="animation-delay: 0.2s;">
                <div class="bg-watermark" style="background-image: url('/static/storefront_bg_1779274559400.png'); opacity: 0.15;"></div>
                <div class="card-content flex flex-col h-full w-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-amber-500/10 rounded-xl text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)]"><i data-lucide="shopping-cart"></i></div>
                        <h2 class="text-xl font-bold text-white flex items-center gap-2">
                            Live Product Showcase
                            <span class="relative flex h-2 w-2 ml-1"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span>
                        </h2>
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
            <div class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden animate-fade-in opacity-0" style="animation-delay: 0.3s;">
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
            <div id="analytics-card" class="glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden animate-fade-in opacity-0" style="animation-delay: 0.4s;">
                <div class="bg-watermark" style="background-image: url('/static/network_mesh_bg_1779274591974.png'); opacity: 0.2;"></div>
                <div class="card-content flex flex-col h-full">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-700/50 pb-4">
                        <div class="p-2 bg-emerald-500/10 rounded-xl text-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.2)]"><i data-lucide="activity"></i></div>
                        <h2 class="text-xl font-bold text-white flex items-center gap-2">
                            System Metrics Command
                            <span class="relative flex h-2 w-2 ml-1"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span>
                        </h2>
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

        <!-- 🧠 AUTO-SCALING & SELF-HEALING ENGINE -->
        <div id="engine-card" class="glass-card rounded-3xl p-6 md:p-8 mt-8 flex flex-col relative overflow-hidden transition-all duration-700 animate-fade-in opacity-0" style="animation-delay: 0.5s;">
            <div class="bg-watermark" style="background-image: url('/static/datacenter_bg_1779274591974.png'); opacity: 0.15;"></div>
            
            <div class="flex items-center justify-between mb-8 border-b border-slate-700/50 pb-4 relative z-10">
                <div class="flex items-center gap-4">
                    <div class="p-3 bg-purple-500/20 rounded-2xl text-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.3)] animate-pulse">
                        <i data-lucide="cpu" class="w-8 h-8"></i>
                    </div>
                    <div>
                        <h2 class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 tracking-tight flex items-center gap-2">
                            AUTO-SCALING & SELF-HEALING ENGINE
                            <span class="relative flex h-2.5 w-2.5 ml-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span></span>
                        </h2>
                        <p class="text-xs text-purple-300/70 font-bold uppercase tracking-widest mt-1">Live Autonomous Infrastructure Control</p>
                    </div>
                </div>
                <div class="hidden md:flex items-center gap-2 px-4 py-2 bg-emerald-950/50 border border-emerald-500/30 rounded-full shadow-[0_0_15px_rgba(52,211,153,0.2)]">
                    <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span class="text-emerald-400 text-xs font-bold uppercase tracking-wider">System Healthy</span>
                </div>
            </div>

            <!-- Metrics Row -->
            <div class="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8 relative z-10">
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Active Servers</div>
                    <div id="metric-servers" class="text-2xl font-black text-cyan-400">3</div>
                </div>
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Queue Workers</div>
                    <div id="metric-workers" class="text-2xl font-black text-blue-400">5</div>
                </div>
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">CPU Usage</div>
                    <div id="metric-cpu" class="text-2xl font-black text-emerald-400">12%</div>
                </div>
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Memory</div>
                    <div id="metric-memory" class="text-2xl font-black text-emerald-400">28%</div>
                </div>
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Throughput</div>
                    <div id="metric-engine-rps" class="text-2xl font-black text-amber-400">0 RPS</div>
                </div>
                <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-center">
                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Error Rate</div>
                    <div id="metric-error" class="text-2xl font-black text-emerald-400">0.0%</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 relative z-10">
                <!-- Live Graph -->
                <div class="bg-slate-950/90 border border-slate-800 rounded-2xl p-5 shadow-inner flex flex-col">
                    <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex justify-between items-center">
                        <span><i data-lucide="trending-up" class="inline w-4 h-4 text-cyan-400 mr-1"></i> Traffic vs Scaling Graph</span>
                        <span id="scaling-status" class="text-emerald-400">Baseline</span>
                    </div>
                    <div class="flex-grow w-full h-48 relative">
                        <canvas id="scalingChart"></canvas>
                    </div>
                </div>

                <!-- Dynamic Server Nodes -->
                <div class="bg-slate-950/90 border border-slate-800 rounded-2xl p-5 shadow-inner flex flex-col">
                    <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex justify-between items-center">
                        <span><i data-lucide="server" class="inline w-4 h-4 text-purple-400 mr-1"></i> Live Infrastructure Cluster</span>
                        <span id="cluster-status" class="text-emerald-400">Optimized</span>
                    </div>
                    <div id="server-cluster" class="flex-grow grid grid-cols-4 sm:grid-cols-6 gap-3 content-start overflow-y-auto chat-scroll h-48 p-2">
                        <!-- Server nodes inserted here via JS -->
                    </div>
                </div>
            </div>

            <!-- Incident Feed -->
            <div class="mt-6 bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-inner h-32 relative z-10">
                <div class="bg-slate-900/80 border-b border-slate-800 py-2 px-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center justify-between">
                    <span class="flex items-center gap-2"><i data-lucide="shield-check" class="w-4 h-4 text-emerald-400"></i> INCIDENT DETECTION FEED</span>
                    <span class="text-slate-500 animate-pulse">Monitoring...</span>
                </div>
                <div id="incident-feed" class="p-3 overflow-y-auto chat-scroll font-mono text-xs space-y-2 flex-grow h-24">
                    <div class="text-emerald-500/70">🟢 System initialized. Auto-scaling daemon active.</div>
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
        let isSimulating = false;
        let timerInterval = null;
        let pollInterval = null;
        let simulationInterval = null;

        function startTimer() {
            countdown = 10;
            saleStarted = false;
            if(timerInterval) clearInterval(timerInterval);
            
            const timerEl = document.getElementById('sale-timer');
            const btn = document.getElementById('buy-btn');
            
            // Immediate jump to SALE LIVE as requested for instant mock interaction
            saleStarted = true;
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

        function simulateTrafficSpike() {
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
            if (isSimulating) return;
            
            isSimulating = true;
            showToast("Massive traffic spike incoming! Scaling systems...", "info");
            
            // Add pulse shimmer to analytics card
            const card = document.getElementById('analytics-card');
            card.classList.add('metrics-shimmer');
            
            const logConsole = document.getElementById('transaction-logs');
            if(logConsole.innerHTML.includes('Waiting for system traffic')) {
                logConsole.innerHTML = '';
            }

            simulationInterval = setInterval(() => {
                if (prevStock <= 0) {
                    clearInterval(simulationInterval);
                    isSimulating = false;
                    currentRps = 0;
                    document.getElementById('metric-rps').innerHTML = `${currentRps} <span class="text-sm text-slate-500 font-bold">RPS</span>`;
                    card.classList.remove('metrics-shimmer');
                    
                    const btn = document.getElementById('buy-btn');
                    btn.disabled = true;
                    btn.className = 'w-full bg-slate-900/80 text-slate-500 border border-slate-800 font-bold py-4 px-4 rounded-xl flex justify-center items-center gap-2 cursor-not-allowed';
                    btn.innerHTML = '<i data-lucide="x-circle" class="w-5 h-5"></i> Sold Out';
                    lucide.createIcons({root: btn});
                    
                    showToast(`Spike Finished: Stock Sold Out!`, 'info');
                    return;
                }

                // Increment RPS up to ~84 (or higher for the engine simulation)
                currentRps = Math.min(1500, currentRps + Math.floor(Math.random() * 50) + 10);
                document.getElementById('metric-rps').innerHTML = `${Math.min(84, Math.floor(currentRps/15))} <span class="text-sm text-slate-500 font-bold">RPS</span>`;
                
                // Decrement stock
                const drop = Math.floor(Math.random() * 3) + 1;
                prevStock = Math.max(0, prevStock - drop);
                document.getElementById('store-stock').textContent = prevStock;
                
                // Update bar width
                const percent = Math.max(0, (prevStock / initialStock) * 100);
                const bar = document.getElementById('stock-bar');
                bar.style.width = `${percent}%`;
                if (percent <= 20) bar.className = 'bg-red-500 h-2 rounded-full transition-all duration-500 ease-out shadow-[0_0_15px_rgba(239,68,68,0.8)]';
                
                // Generate Logs
                let uid = 'bot_' + Math.random().toString(36).substr(2, 6).toUpperCase();
                const latency = Math.floor(Math.random() * 5) + 1;
                
                if (Math.random() > 0.6) {
                    // Rate Limited
                    totalBlocked += drop;
                    document.getElementById('metric-blocked').textContent = totalBlocked;
                    logConsole.innerHTML += `<div class="text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)] log-slide-in">🔴 ${uid}: 429 Rate-Limited</div>`;
                } else {
                    // Success
                    logConsole.innerHTML += `<div class="text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.5)] log-slide-in">🟢 ${uid}: Order Confirmed [Latency: ${latency}ms]</div>`;
                }
                logConsole.scrollTop = logConsole.scrollHeight;

            }, 100);
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

            toast.className = `p-4 rounded-xl slide-in-toast pointer-events-auto flex items-center gap-3 min-w-[300px] font-bold shadow-2xl border border-slate-800 backdrop-blur-md ${styles[type]}`;
            toast.innerHTML = `${icons[type]}<span>${msg}</span>`;
            
            container.appendChild(toast);
            lucide.createIcons({root: toast});
            
            setTimeout(() => {
                toast.classList.remove('slide-in-toast');
                toast.classList.add('slide-out-toast');
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
            
            const pid = pidInput.value.trim();
            const qty = qtyInput.value.trim();
            const price = priceInput.value.trim();
            
            if (!pid || !qty || !price) {
                showToast("Please manually fill in all fields (Product ID, Capacity, Price) first!", "error");
                return;
            }
            
            currentProductId = pid;
            initialStock = parseInt(qty);
            prevStock = initialStock;
            stockAlertTriggered = false;
            
            document.getElementById('store-title').textContent = pid.replace(/_/g, ' ');
            document.getElementById('store-price').textContent = `₹${parseFloat(price).toLocaleString('en-IN')}`;
            document.getElementById('store-stock').textContent = initialStock;
            
            showToast('Stock Initialized successfully!', 'success');
            
            // Switch UI
            document.getElementById('empty-state').classList.add('hidden');
            document.getElementById('empty-state').classList.remove('flex');
            
            const liveState = document.getElementById('live-state');
            liveState.classList.remove('hidden');
            liveState.classList.add('flex');
            
            startTimer(); 
            
            // Required mock log
            logIncident(`🟢 Flash sale initialized successfully for ${pid}.`, 'success');
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

        // Architecture Modal Functions
        function openArchModal() {
            document.getElementById('arch-modal').classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Randomize live indicators in modal occasionally
            setInterval(() => {
                document.getElementById('arch-rps').innerText = Math.floor(Math.random() * 100 + 20) + ' RPS';
                document.getElementById('arch-latency').innerText = (Math.random() * 4 + 1).toFixed(1) + 'ms';
                document.getElementById('arch-bots').innerText = Math.floor(Math.random() * 200 + 50);
            }, 2000);
        }

        function closeArchModal() {
            document.getElementById('arch-modal').classList.remove('active');
            document.body.style.overflow = 'auto';
        }

        // ==========================================
        // AUTO-SCALING & SELF-HEALING ENGINE LOGIC
        // ==========================================
        let engineRps = 0;
        let activeServers = 3;
        let activeWorkers = 5;
        let isScaling = false;
        
        // Chart.js Setup
        const ctx = document.getElementById('scalingChart').getContext('2d');
        const trafficGradient = ctx.createLinearGradient(0, 0, 0, 400);
        trafficGradient.addColorStop(0, 'rgba(56, 189, 248, 0.4)');
        trafficGradient.addColorStop(1, 'rgba(56, 189, 248, 0.01)');
        
        const serverGradient = ctx.createLinearGradient(0, 0, 0, 400);
        serverGradient.addColorStop(0, 'rgba(168, 85, 247, 0.3)');
        serverGradient.addColorStop(1, 'rgba(168, 85, 247, 0.0)');

        const scalingChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [
                    {
                        label: 'Traffic (RPS)',
                        data: Array(20).fill(0),
                        borderColor: '#38bdf8',
                        backgroundColor: trafficGradient,
                        borderWidth: 3,
                        tension: 0.45,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Active Servers',
                        data: Array(20).fill(3),
                        borderColor: '#a855f7',
                        backgroundColor: serverGradient,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.2,
                        fill: true,
                        pointRadius: 0,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 600, easing: 'easeOutQuart' },
                elements: {
                    line: { borderJoinStyle: 'round' }
                },
                scales: {
                    x: { display: false },
                    y: { display: true, position: 'left', grid: { color: 'rgba(255,255,255,0.03)' }, min: 0 },
                    y1: { display: true, position: 'right', grid: { drawOnChartArea: false }, min: 0 }
                },
                plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 10, family: 'Outfit' } } } }
            }
        });

        function logIncident(msg, type = 'info') {
            const feed = document.getElementById('incident-feed');
            let color = 'text-slate-400';
            if (type === 'warning') color = 'text-amber-400 font-bold drop-shadow-[0_0_5px_rgba(245,158,11,0.5)]';
            if (type === 'error') color = 'text-red-400 font-bold drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]';
            if (type === 'success') color = 'text-emerald-400 font-bold drop-shadow-[0_0_5px_rgba(52,211,153,0.5)]';
            
            feed.innerHTML += `<div class="${color} log-slide-in mb-1">${msg}</div>`;
            feed.scrollTop = feed.scrollHeight;
        }

        function renderServers(count) {
            const cluster = document.getElementById('server-cluster');
            cluster.innerHTML = '';
            for (let i = 0; i < count; i++) {
                const isHealing = Math.random() > 0.93 && currentRps > 500;
                let stateClass = 'server-healthy bg-emerald-500/10 text-emerald-400';
                
                if (isHealing) {
                    stateClass = 'server-error bg-red-500/20 text-red-400';
                    setTimeout(() => {
                        logIncident(`🛠️ Auto Recovery Triggered on Node-${i+1}`, 'warn');
                        logIncident(`🔄 Restarting unhealthy microservice...`, 'warn');
                        setTimeout(() => logIncident(`✅ System stabilized successfully`, 'success'), 1500);
                    }, 500);
                }

                cluster.innerHTML += `
                    <div class="server-node ${stateClass} border rounded-lg p-2 flex flex-col items-center justify-center relative overflow-hidden backdrop-blur-sm">
                        <i data-lucide="server" class="w-5 h-5 mb-1"></i>
                        <span class="text-[8px] font-bold">NODE-${i+1}</span>
                    </div>
                `;
            }
            lucide.createIcons({root: cluster});
        }

        renderServers(activeServers);

        setInterval(() => {
            engineRps = currentRps;
            document.getElementById('metric-engine-rps').innerText = `${engineRps} RPS`;
            
            let cpu = Math.max(5, Math.min(99, Math.floor((engineRps / 50) * 100) + Math.floor(Math.random() * 10)));
            let mem = Math.max(20, Math.min(95, Math.floor((activeServers / 50) * 100) + Math.floor(Math.random() * 5)));
            let error = engineRps > 1000 ? (Math.random() * 2).toFixed(1) : '0.0';
            
            if (engineRps > 800 && !isScaling) {
                isScaling = true;
                document.getElementById('engine-card').classList.add('incident-glow-red');
                document.getElementById('scaling-status').innerText = 'SCALING ACTIVE';
                document.getElementById('scaling-status').className = 'text-purple-400 animate-pulse';
                
                logIncident(`🚀 Massive traffic detected (>1000 RPS)`, 'warn');
                logIncident(`🚀 Spawning Additional Inventory Nodes...`, 'scale');
                logIncident(`🚀 Scaling API Gateways...`, 'scale');
                
                let scaleInterval = setInterval(() => {
                    activeServers += Math.floor(Math.random() * 5) + 2;
                    activeWorkers += Math.floor(Math.random() * 10) + 5;
                    
                    if (activeServers > 40 || engineRps < 500) {
                        clearInterval(scaleInterval);
                        isScaling = false;
                        document.getElementById('scaling-status').innerText = 'Optimized';
                        document.getElementById('scaling-status').className = 'text-emerald-400';
                        document.getElementById('engine-card').classList.remove('incident-glow-red');
                        logIncident(`🟢 Scaling complete. System capacity maximized.`, 'success');
                    }
                    
                    document.getElementById('metric-servers').innerText = activeServers;
                    document.getElementById('metric-workers').innerText = activeWorkers;
                    renderServers(Math.min(activeServers, 24)); 
                }, 800);
            } else if (engineRps < 200 && activeServers > 5 && !isScaling) {
                activeServers = Math.max(3, activeServers - 2);
                activeWorkers = Math.max(5, activeWorkers - 3);
                document.getElementById('metric-servers').innerText = activeServers;
                document.getElementById('metric-workers').innerText = activeWorkers;
                renderServers(Math.min(activeServers, 24));
            }

            document.getElementById('metric-cpu').innerText = `${cpu}%`;
            document.getElementById('metric-cpu').className = `text-2xl font-black ${cpu > 80 ? 'text-red-400' : 'text-emerald-400'}`;
            document.getElementById('metric-memory').innerText = `${mem}%`;
            document.getElementById('metric-error').innerText = `${error}%`;
            
            scalingChart.data.datasets[0].data.shift();
            scalingChart.data.datasets[0].data.push(engineRps);
            scalingChart.data.datasets[1].data.shift();
            scalingChart.data.datasets[1].data.push(activeServers);
            scalingChart.update();
            
        }, 1000);

    </script>
    
    <!-- Architecture Modal -->
    <div id="arch-modal" class="fixed inset-0 flex items-center justify-center p-4 sm:p-8">
        <div class="absolute inset-0 bg-slate-950/80" onclick="closeArchModal()"></div>
        
        <div id="arch-content" class="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-3xl p-6 sm:p-10 chat-scroll">
            <button onclick="closeArchModal()" class="absolute top-6 right-6 text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-700 p-2 rounded-full transition-all border border-slate-600 hover:border-slate-400 z-50">
                <i data-lucide="x" class="w-6 h-6"></i>
            </button>
            
            <div class="text-center mb-10">
                <h2 class="text-2xl sm:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 tracking-tight flex items-center justify-center gap-3">
                    <i data-lucide="network" class="w-8 h-8 text-cyan-400"></i> Distributed System Architecture
                </h2>
                <p class="text-purple-300/70 text-sm font-bold uppercase tracking-widest mt-2">Production-Grade Infrastructure Pipeline</p>
            </div>
            
            <!-- Flow Diagram -->
            <div class="flex flex-col items-center w-full max-w-2xl mx-auto pb-8">
                
                <!-- 1. Users -->
                <div class="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-blue-500/20 text-blue-400 rounded-xl"><i data-lucide="users" class="w-6 h-6"></i></div>
                        <div class="text-left">
                            <h3 class="font-bold text-white text-lg">Global Traffic</h3>
                            <p class="text-xs text-slate-400">Incoming web requests</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-[10px] font-bold text-slate-500 uppercase">Live Load</div>
                        <div id="arch-rps" class="text-lg font-black text-blue-400">53 RPS</div>
                    </div>
                </div>
                
                <div class="connector-down"><div class="particle-down"></div><div class="particle-down"></div></div>
                
                <!-- 2. Load Balancer -->
                <div class="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl"><i data-lucide="server" class="w-6 h-6"></i></div>
                        <div class="text-left">
                            <h3 class="font-bold text-white text-lg">L7 Load Balancer</h3>
                            <p class="text-xs text-slate-400">Traffic distribution & routing</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-[10px] font-bold text-slate-500 uppercase">Latency</div>
                        <div id="arch-latency" class="text-lg font-black text-cyan-400">2.4ms</div>
                    </div>
                </div>
                
                <div class="connector-down"><div class="particle-down"></div><div class="particle-down"></div></div>
                
                <!-- 3. Rate Limiter -->
                <div class="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="p-3 bg-purple-500/20 text-purple-400 rounded-xl"><i data-lucide="shield-alert" class="w-6 h-6"></i></div>
                        <div class="text-left">
                            <h3 class="font-bold text-white text-lg">Token Bucket Rate Limiter</h3>
                            <p class="text-xs text-slate-400">DDoS & spam protection (Redis)</p>
                        </div>
                    </div>
                </div>
                
                <div class="connector-down"><div class="particle-down"></div><div class="particle-down"></div></div>
                
                <!-- Grid Layer -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
                    
                    <!-- 4. Order Queue -->
                    <div class="arch-node rounded-2xl p-4 flex flex-col justify-center text-center items-center">
                        <div class="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl mb-3"><i data-lucide="layers" class="w-6 h-6"></i></div>
                        <h3 class="font-bold text-white text-base">Order Queue Engine</h3>
                        <p class="text-xs text-slate-400">Async event streaming</p>
                    </div>
                    
                    <!-- 5. Inventory Manager -->
                    <div class="arch-node rounded-2xl p-4 flex flex-col justify-center text-center items-center">
                        <div class="p-3 bg-amber-500/20 text-amber-400 rounded-xl mb-3"><i data-lucide="database-zap" class="w-6 h-6"></i></div>
                        <h3 class="font-bold text-white text-base">Inventory Manager</h3>
                        <p class="text-xs text-slate-400">Atomic Lua scripts</p>
                    </div>
                    
                </div>
                
                <div class="flex w-full justify-around mb-2 mt-2">
                    <div class="connector-down h-10"><div class="particle-down"></div></div>
                    <div class="connector-down h-10"><div class="particle-down"></div></div>
                </div>
                
                <!-- 6. AI Fraud Detection -->
                <div class="arch-node ai-pulse rounded-2xl p-5 w-full sm:w-3/4 flex items-center justify-between mb-2">
                    <div class="flex items-center gap-4">
                        <div class="p-4 bg-red-500/20 text-red-400 rounded-full"><i data-lucide="bot" class="w-7 h-7"></i></div>
                        <div class="text-left">
                            <h3 class="font-bold text-white text-lg">AI Fraud Detection Engine</h3>
                            <p class="text-xs text-slate-400">Anomaly detection & bot filtering</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-[10px] font-bold text-red-300 uppercase">Blocked Bots</div>
                        <div id="arch-bots" class="text-xl font-black text-red-500">91</div>
                    </div>
                </div>
                
                <div class="connector-down"><div class="particle-down"></div><div class="particle-down"></div></div>
                
                <!-- Bottom Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
                    
                    <!-- 7. Payment Gateway -->
                    <div class="arch-node rounded-2xl p-4 flex flex-col justify-center text-center items-center">
                        <div class="p-3 bg-green-500/20 text-green-400 rounded-xl mb-3"><i data-lucide="credit-card" class="w-6 h-6"></i></div>
                        <h3 class="font-bold text-white text-base">Payment Gateway</h3>
                        <p class="text-xs text-slate-400">Secure transactions</p>
                    </div>
                    
                    <!-- 8. Analytics -->
                    <div class="arch-node rounded-2xl p-4 flex flex-col justify-center text-center items-center">
                        <div class="p-3 bg-fuchsia-500/20 text-fuchsia-400 rounded-xl mb-3"><i data-lucide="bar-chart-2" class="w-6 h-6"></i></div>
                        <h3 class="font-bold text-white text-base">Real-Time Logs</h3>
                        <p class="text-xs text-slate-400">Metrics & Tracing</p>
                    </div>
                    
                </div>
                
            </div>
            
        </div>
    </div>
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
