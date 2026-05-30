import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion';
import { 
  Server, ShieldAlert, Cpu, Activity, Clock, ShoppingCart, TrendingUp, 
  Database, LayoutGrid, Zap, CheckCircle2, AlertTriangle, Info, Bot, 
  TerminalSquare, ShieldCheck, Network, Users, Layers, CreditCard, BarChart2,
  X, Sparkles, User, Package, Hexagon
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

// Rolling Number Component
const RollingNumber = ({ value }) => {
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { stiffness: 100, damping: 20 });
  const ref = useRef(null);
  
  useEffect(() => {
    motionValue.set(value);
  }, [value, motionValue]);
  
  useEffect(() => {
    return springValue.on("change", (latest) => {
      if (ref.current) ref.current.textContent = Math.floor(latest);
    });
  }, [springValue]);
  
  return <motion.span ref={ref}>{value}</motion.span>;
};

// Variants for Framer Motion
const staggerContainer = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.2 } }
};

const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  show: { opacity: 1, y: 0, transition: { type: "spring", bounce: 0.3, duration: 0.8 } }
};

const glassHover = {
  rest: { scale: 1, boxShadow: "0 25px 50px -12px rgba(0,0,0,0.5)", borderColor: "rgba(39, 39, 42, 0.6)" },
  hover: { scale: 1.02, boxShadow: "0 30px 60px -12px rgba(124, 58, 237, 0.25)", borderColor: "rgba(124, 58, 237, 0.5)", transition: { type: "spring", stiffness: 400, damping: 25 } }
};

// Premium Glassmorphism Utility
const glassCardClass = "backdrop-blur-md bg-zinc-900/40 border border-zinc-800/60 rounded-3xl relative overflow-hidden transition-all duration-300";

export default function App() {
  const [productId, setProductId] = useState('');
  const [capacity, setCapacity] = useState('');
  const [basePrice, setBasePrice] = useState('');
  
  const [isInitialized, setIsInitialized] = useState(false);
  const [saleStarted, setSaleStarted] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  
  const [stock, setStock] = useState(0);
  const [initialStock, setInitialStock] = useState(0);
  
  const [trafficRps, setTrafficRps] = useState(0);
  const [blockedSpam, setBlockedSpam] = useState(0);
  const [avgLatency, setAvgLatency] = useState(1.5);
  
  const [activeServers, setActiveServers] = useState(3);
  const [activeWorkers, setActiveWorkers] = useState(5);
  const [cpuUsage, setCpuUsage] = useState(5);
  const [memUsage, setMemUsage] = useState(20);
  const [errorRate, setErrorRate] = useState("0.0");
  
  const [logs, setLogs] = useState([]);
  const [incidents, setIncidents] = useState([{ id: Date.now(), msg: '🟢 System online. Awaiting configuration.', type: 'info' }]);
  
  const [chartData, setChartData] = useState({ traffic: Array(20).fill(0), servers: Array(20).fill(3) });
  const [showArchModal, setShowArchModal] = useState(false);

  const logsEndRef = useRef(null);
  const incidentEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  useEffect(() => {
    incidentEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [incidents]);

  const addIncident = (msg, type = 'info') => {
    setIncidents(prev => [...prev.slice(-49), { id: Date.now() + Math.random(), msg, type }]);
  };

  const handleInitialize = () => {
    if (!productId || !capacity || !basePrice) {
      addIncident("⚠️ Please fill in all product configuration fields.", "warn");
      return;
    }
    const parsedCap = parseInt(capacity) || 100;
    setInitialStock(parsedCap);
    setStock(parsedCap);
    setIsInitialized(true);
    setSaleStarted(true); // Jump straight to LIVE
    addIncident(`🟢 Flash sale initialized successfully for ${productId}.`, 'success');
  };

  const handleSimulate = () => {
    if (!isInitialized || stock <= 0 || isSimulating) return;
    setIsSimulating(true);
    addIncident("🚀 Massive traffic spike incoming! Scaling systems...", "info");
    addIncident("🚀 Spawning Additional Inventory Nodes...", "scale");
    
    let currentStock = stock;
    let currentTraffic = 0;
    let currentServers = activeServers;
    let currentBlocked = blockedSpam;

    const interval = setInterval(() => {
      if (currentStock <= 0) {
        clearInterval(interval);
        setIsSimulating(false);
        setTrafficRps(0);
        setAvgLatency(1.5);
        addIncident(`🟢 Spike Finished: Stock Sold Out! System capacity maximized.`, 'success');
        return;
      }

      // Scaling logic
      currentTraffic = Math.min(1500, currentTraffic + Math.floor(Math.random() * 50) + 10);
      setTrafficRps(Math.min(84, Math.floor(currentTraffic / 15)));
      setAvgLatency(Math.random() * 2 + 1.5);
      
      if (currentTraffic > 800 && currentServers < 24) {
        currentServers += Math.floor(Math.random() * 3) + 1;
        setActiveServers(Math.min(24, currentServers));
        setActiveWorkers(prev => prev + 2);
      }

      setCpuUsage(Math.min(99, Math.floor((currentTraffic / 1500) * 100) + Math.floor(Math.random() * 10)));
      setMemUsage(Math.min(95, Math.floor((currentServers / 24) * 100) + Math.floor(Math.random() * 5)));
      setErrorRate((Math.random() * 1.5).toFixed(1));

      // Stock Drop
      const drop = Math.floor(Math.random() * 3) + 1;
      currentStock = Math.max(0, currentStock - drop);
      setStock(currentStock);

      // Logs
      const uid = 'bot_' + Math.random().toString(36).substr(2, 6).toUpperCase();
      const latency = Math.floor(Math.random() * 5) + 1;
      
      if (Math.random() > 0.6) {
        currentBlocked += drop;
        setBlockedSpam(currentBlocked);
        setLogs(prev => [...prev.slice(-49), { id: Date.now() + Math.random(), text: `🔴 ${uid}: 429 Rate-Limited`, type: 'error' }]);
      } else {
        setLogs(prev => [...prev.slice(-49), { id: Date.now() + Math.random(), text: `🟢 ${uid}: Order Confirmed [Latency: ${latency}ms]`, type: 'success' }]);
      }

      // Chart Update
      setChartData(prev => {
        const newTraffic = [...prev.traffic.slice(1), currentTraffic];
        const newServers = [...prev.servers.slice(1), currentServers];
        return { traffic: newTraffic, servers: newServers };
      });

    }, 100);
  };

  const renderServerNodes = () => {
    return Array.from({ length: 24 }).map((_, i) => {
      const isActive = i < activeServers;
      const isHealing = Math.random() > 0.95 && isSimulating && isActive;
      
      return (
        <motion.div 
          key={i}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ 
            opacity: isActive ? 1 : 0.2, 
            scale: isActive ? 1 : 0.9,
            transition: { delay: isSimulating && isActive ? i * 0.05 : 0 }
          }}
          className={`border rounded-xl p-2 flex flex-col items-center justify-center relative overflow-hidden backdrop-blur-sm transition-colors duration-300 ${
            !isActive ? 'bg-zinc-900/20 border-zinc-800 text-zinc-700' :
            isHealing ? 'bg-red-500/10 text-red-400 border-red-500/40 animate-pulse' : 
            'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
          }`}
        >
          {isActive && <div className="absolute inset-0 bg-cyan-400/5 animate-pulse rounded-xl"></div>}
          <Server className="w-5 h-5 mb-1" />
          <span className="text-[8px] font-bold">NODE-{i+1}</span>
        </motion.div>
      );
    });
  };

  return (
    <div className="min-h-screen relative overflow-hidden text-zinc-200">
      <div className="ambient-mesh"></div>
      <div className="circuit-pattern"></div>
      <div className="scanline"></div>
      
      <motion.div 
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="relative z-10 max-w-7xl mx-auto px-4 py-8"
      >
        {/* Header */}
        <motion.header variants={fadeUp} className={`${glassCardClass} p-6 shadow-2xl mb-8 flex justify-between items-center`}>
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-violet-500 blur-xl opacity-40 rounded-full animate-pulse"></div>
              <div className="bg-gradient-to-br from-violet-500 to-fuchsia-600 p-3 rounded-2xl relative">
                <Zap className="w-8 h-8 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-cyan-400">
                ULTRA-CONCURRENT ⚡ FLASH MARKET
              </h1>
              <p className="text-zinc-400 text-sm font-semibold tracking-widest uppercase mt-1">Enterprise Distributed Infrastructure Command Center</p>
            </div>
          </div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowArchModal(true)}
            className="flex items-center gap-2 bg-zinc-800/80 hover:bg-zinc-700 border border-zinc-600 text-zinc-300 px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-[0_0_15px_rgba(124,58,237,0.15)]"
          >
            <Network className="w-4 h-4" /> View Architecture
          </motion.button>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column */}
          <motion.div variants={fadeUp} className="lg:col-span-4 space-y-8">
            
            <motion.div variants={glassHover} initial="rest" whileHover="hover" className={`${glassCardClass} p-6 group`}>
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <Database className="w-6 h-6 text-violet-400" />
                <h2 className="text-xl font-bold">Stock Control Center</h2>
              </div>
              <div className="space-y-4 relative z-10">
                <div>
                  <label className="text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2 block">Product ID</label>
                  <input type="text" value={productId} onChange={e => setProductId(e.target.value)} className="w-full bg-zinc-950/80 border border-zinc-700 rounded-xl px-4 py-3 text-sm focus:border-violet-400 focus:ring-1 focus:ring-violet-400 outline-none transition-all" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2 block">Capacity</label>
                    <input type="number" value={capacity} onChange={e => setCapacity(e.target.value)} className="w-full bg-zinc-950/80 border border-zinc-700 rounded-xl px-4 py-3 text-sm focus:border-violet-400 outline-none transition-all" />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-400 font-bold uppercase tracking-wider mb-2 block">Base Price (₹)</label>
                    <input type="number" value={basePrice} onChange={e => setBasePrice(e.target.value)} className="w-full bg-zinc-950/80 border border-zinc-700 rounded-xl px-4 py-3 text-sm focus:border-violet-400 outline-none transition-all" />
                  </div>
                </div>
                <motion.button 
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={handleInitialize}
                  className="w-full mt-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold py-3.5 px-4 rounded-xl shadow-[0_0_20px_rgba(124,58,237,0.3)] transition-all flex justify-center items-center gap-2"
                >
                  <Server className="w-5 h-5" /> Initialize System
                </motion.button>
              </div>
            </motion.div>

            <motion.div variants={glassHover} initial="rest" whileHover="hover" className={`${glassCardClass} p-6 group`}>
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity"><TerminalSquare className="w-24 h-24 text-cyan-400" /></div>
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <TerminalSquare className="w-6 h-6 text-cyan-400" />
                <h2 className="text-xl font-bold">Chaos Engineering</h2>
              </div>
              <p className="text-zinc-400 text-sm mb-6 relative z-10 leading-relaxed">
                Trigger a massive distributed bot-net load test to verify auto-scaling capabilities.
              </p>
              <motion.button 
                whileHover={isInitialized && !isSimulating && stock > 0 ? { scale: 1.02, boxShadow: "0 0 30px rgba(6,182,212,0.4)" } : {}}
                whileTap={isInitialized && !isSimulating && stock > 0 ? { scale: 0.98 } : {}}
                onClick={handleSimulate}
                disabled={!isInitialized || isSimulating || stock <= 0}
                className={`w-full font-bold py-3.5 px-4 rounded-xl flex justify-center items-center gap-2 relative z-10 transition-all duration-300 ${
                  isInitialized && stock > 0 && !isSimulating
                    ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white border border-cyan-400/50 shadow-lg"
                    : "bg-zinc-900/80 text-zinc-500 border border-zinc-800 cursor-not-allowed"
                }`}
              >
                <TrendingUp className="w-5 h-5" /> Simulate 100x Traffic Spike
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Right Column */}
          <motion.div variants={fadeUp} className="lg:col-span-8 space-y-8 flex flex-col">
            
            {/* Showcase */}
            <motion.div variants={glassHover} initial="rest" whileHover="hover" className={`${glassCardClass} p-8 min-h-[220px] flex items-center group`}>
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent"></div>
              {!isInitialized ? (
                <div className="w-full text-center text-zinc-600 font-medium animate-pulse flex flex-col items-center">
                  <AlertTriangle className="w-10 h-10 mb-3 opacity-50" />
                  ⚠️ No active flash sale. Waiting for initialization...
                </div>
              ) : (
                <div className="w-full relative z-10 flex flex-col md:flex-row gap-8 items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-violet-500/20 text-violet-400 border border-violet-500/30 px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase flex items-center gap-2 shadow-[0_0_10px_rgba(124,58,237,0.2)]">
                        <span className="w-2 h-2 rounded-full bg-violet-400 animate-ping"></span> Live Product Showcase
                      </span>
                    </div>
                    <h2 className="text-4xl font-black text-white tracking-tight uppercase mt-4 mb-2">{productId.replace(/_/g, ' ')}</h2>
                    <div className="text-3xl font-bold text-violet-400 drop-shadow-[0_0_10px_rgba(124,58,237,0.3)]">₹{parseFloat(basePrice).toLocaleString('en-IN')}</div>
                  </div>
                  
                  <div className="bg-zinc-950/60 backdrop-blur-md border border-zinc-700 p-6 rounded-2xl w-full md:w-64 shadow-xl relative overflow-hidden">
                    <div className="flex justify-between items-end mb-2 relative z-10">
                      <div className="text-xs text-zinc-400 font-bold uppercase tracking-wider">Stock Level</div>
                      <div className={`text-3xl font-black transition-colors duration-300 ${stock < 20 ? 'text-red-500' : 'text-cyan-400'}`}>
                        <RollingNumber value={stock} />
                      </div>
                    </div>
                    <div className="w-full bg-zinc-800 rounded-full h-2.5 mb-4 overflow-hidden border border-zinc-700 relative z-10">
                      <div 
                        className="h-2.5 rounded-full transition-all duration-1000 ease-in-out bg-gradient-to-r from-violet-600 to-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.6)]"
                        style={{ width: `${Math.max(0, (stock / initialStock) * 100)}%` }}
                      ></div>
                    </div>
                    
                    <AnimatePresence mode="wait">
                      {stock <= 0 ? (
                        <motion.button 
                          key="soldout"
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className="w-full bg-zinc-900/80 text-zinc-500 border border-zinc-800 font-bold py-3 px-4 rounded-xl flex justify-center items-center gap-2 cursor-not-allowed"
                        >
                          <X className="w-5 h-5"/> Sold Out
                        </motion.button>
                      ) : (
                        <motion.button 
                          key="buynow"
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className="w-full font-bold py-3 px-4 rounded-xl flex justify-center items-center gap-2 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all"
                        >
                          <ShoppingCart className="w-5 h-5"/> Buy Now
                        </motion.button>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
              )}
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 flex-grow">
              {/* Analytics */}
              <motion.div variants={glassHover} initial="rest" whileHover="hover" className={`${glassCardClass} p-6 flex flex-col ${isSimulating ? 'border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.1)]' : ''}`}>
                <div className="flex items-center gap-3 mb-6 relative z-10">
                  <Activity className="w-6 h-6 text-cyan-400" />
                  <h2 className="text-xl font-bold">System Telemetry</h2>
                </div>
                <div className="grid grid-cols-2 gap-4 flex-grow relative z-10">
                  <div className="bg-zinc-950/60 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-center">
                    <div className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider mb-1">Live Traffic</div>
                    <div className="text-3xl font-black text-cyan-400"><RollingNumber value={trafficRps} /> <span className="text-sm">RPS</span></div>
                  </div>
                  <div className="bg-zinc-950/60 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-center">
                    <div className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider mb-1">Avg Latency</div>
                    <div className="text-3xl font-black text-blue-400">{avgLatency.toFixed(1)} <span className="text-sm">ms</span></div>
                  </div>
                  <div className="bg-zinc-950/60 border border-zinc-800 rounded-2xl p-4 flex flex-col justify-center col-span-2">
                    <div className="text-[10px] text-red-400/80 font-bold uppercase tracking-wider mb-1 flex items-center gap-1"><ShieldAlert className="w-3 h-3"/> Blocked Spam Requests</div>
                    <div className="text-4xl font-black text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.6)]"><RollingNumber value={blockedSpam} /></div>
                  </div>
                </div>
              </motion.div>

              {/* Logs */}
              <motion.div variants={glassHover} initial="rest" whileHover="hover" className={`${glassCardClass} p-0 flex flex-col border-zinc-800`}>
                <div className="bg-zinc-900/90 border-b border-zinc-800 px-6 py-4 flex items-center justify-between relative z-10">
                  <h2 className="text-sm font-bold uppercase tracking-widest text-zinc-300 flex items-center gap-2">
                    <TerminalSquare className="w-4 h-4 text-emerald-400" /> Real-Time Logs
                  </h2>
                  <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[9px] font-bold uppercase animate-pulse">Live Stream</span>
                </div>
                <div className="p-4 bg-[#050507] flex-grow overflow-y-auto chat-scroll font-mono text-xs space-y-2 relative h-48">
                  <div className="scanline"></div>
                  {logs.length === 0 ? (
                    <div className="text-zinc-600 flex h-full items-center justify-center">Waiting for system traffic...</div>
                  ) : (
                    <AnimatePresence initial={false}>
                      {logs.map((log) => (
                        <motion.div 
                          key={log.id}
                          initial={{ opacity: 0, y: 15 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={log.type === 'error' ? 'text-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]' : 'text-emerald-400 drop-shadow-[0_0_5px_rgba(16,185,129,0.5)]'}
                        >
                          {log.text}
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  )}
                  <div ref={logsEndRef} />
                </div>
              </motion.div>
            </div>
            
            {/* Auto-Scaling Engine */}
            <motion.div variants={fadeUp} className={`${glassCardClass} p-8 transition-all duration-700 ${isSimulating ? 'border-violet-500/40 shadow-[0_0_40px_rgba(124,58,237,0.15)]' : ''}`}>
              <div className="absolute inset-0 bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 opacity-90"></div>
              
              <div className="relative z-10">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                  <div>
                    <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-500 tracking-tight flex items-center gap-3">
                      <Cpu className="w-8 h-8 text-cyan-400" /> Auto-Scaling Engine
                    </h2>
                    <p className="text-zinc-400 text-sm mt-1 font-medium">Enterprise infrastructure orchestrator actively managing load</p>
                  </div>
                  <div className="mt-4 md:mt-0 flex gap-4">
                    <div className="bg-zinc-950/80 border border-zinc-800 rounded-xl p-3 text-center min-w-[80px]">
                      <div className="text-[10px] text-zinc-400 font-bold uppercase mb-1">Servers</div>
                      <div className="text-2xl font-black text-violet-400"><RollingNumber value={activeServers} /></div>
                    </div>
                    <div className="bg-zinc-950/80 border border-zinc-800 rounded-xl p-3 text-center min-w-[80px]">
                      <div className="text-[10px] text-zinc-400 font-bold uppercase mb-1">CPU %</div>
                      <div className={`text-2xl font-black transition-colors duration-700 ${cpuUsage >= 99 ? 'text-red-500 animate-pulse' : 'text-emerald-400'}`}>
                        <RollingNumber value={cpuUsage} />%
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative z-10">
                  {/* Chart */}
                  <div className="bg-zinc-950/90 border border-zinc-800 rounded-2xl p-5 shadow-inner flex flex-col h-56">
                    <div className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-4 flex justify-between items-center">
                      <span><TrendingUp className="inline w-4 h-4 text-cyan-400 mr-1" /> Traffic vs Scaling</span>
                      <span className={isSimulating ? "text-violet-400 animate-pulse" : "text-emerald-400"}>
                        {isSimulating ? "SCALING ACTIVE" : "Optimized"}
                      </span>
                    </div>
                    <div className="flex-grow w-full relative">
                      <Line 
                        data={{
                          labels: Array(20).fill(''),
                          datasets: [
                            { label: 'Traffic (RPS)', data: chartData.traffic, borderColor: '#06b6d4', backgroundColor: 'rgba(6, 182, 212, 0.1)', fill: true, tension: 0.4, yAxisID: 'y' },
                            { label: 'Servers', data: chartData.servers, borderColor: '#7c3aed', borderDash: [5, 5], tension: 0.1, yAxisID: 'y1' }
                          ]
                        }}
                        options={{ responsive: true, maintainAspectRatio: false, animation: { duration: 0 }, scales: { x: { display: false }, y: { display: false, position: 'left', min: 0 }, y1: { display: false, position: 'right', min: 0, grid: { drawOnChartArea: false } } }, plugins: { legend: { display: false } } }}
                      />
                    </div>
                  </div>

                  {/* Infrastructure Cluster */}
                  <div className="bg-zinc-950/90 border border-zinc-800 rounded-2xl p-5 shadow-inner flex flex-col h-56 relative overflow-hidden">
                    <div className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-4 flex justify-between items-center relative z-10">
                      <span><Server className="inline w-4 h-4 text-violet-400 mr-1" /> Active Infrastructure Cluster</span>
                    </div>
                    <div className="flex-grow grid grid-cols-4 sm:grid-cols-6 gap-3 content-start overflow-y-auto chat-scroll p-1 relative z-10">
                      {renderServerNodes()}
                    </div>
                  </div>
                </div>

                {/* Incident Feed */}
                <div className="mt-6 bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden shadow-inner h-32 flex flex-col">
                  <div className="bg-zinc-900/80 border-b border-zinc-800 py-2 px-4 text-[10px] font-bold text-zinc-400 uppercase tracking-widest flex items-center justify-between">
                    <span className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-emerald-400" /> INCIDENT DETECTION FEED</span>
                    <span className="text-zinc-500 animate-pulse">Monitoring...</span>
                  </div>
                  <div className="p-3 overflow-y-auto chat-scroll font-mono text-xs space-y-2 flex-grow">
                    <AnimatePresence initial={false}>
                      {incidents.map(inc => {
                        let color = 'text-zinc-400';
                        if (inc.type === 'success') color = 'text-emerald-400';
                        if (inc.type === 'warn') color = 'text-amber-400';
                        if (inc.type === 'scale') color = 'text-violet-400';
                        return (
                          <motion.div key={inc.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className={`${color} mb-1`}>
                            {inc.msg}
                          </motion.div>
                        );
                      })}
                    </AnimatePresence>
                    <div ref={incidentEndRef} />
                  </div>
                </div>
              </div>
            </motion.div>

          </motion.div>
        </div>
      </motion.div>

      {/* Architecture Modal */}
      <AnimatePresence>
        {showArchModal && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 flex items-center justify-center p-4 sm:p-8 z-50 bg-[#050507]/90 backdrop-blur-xl"
            onClick={() => setShowArchModal(false)}
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20, opacity: 0 }} 
              animate={{ scale: 1, y: 0, opacity: 1 }} 
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300, duration: 0.5 }}
              className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-3xl p-6 sm:p-10 chat-scroll border border-violet-500/40 shadow-[0_0_50px_rgba(124,58,237,0.15)]"
              style={{ background: "linear-gradient(145deg, rgba(24, 24, 27, 0.95), rgba(9, 9, 11, 0.98))" }}
              onClick={e => e.stopPropagation()}
            >
              <button onClick={() => setShowArchModal(false)} className="absolute top-6 right-6 text-zinc-400 hover:text-white bg-zinc-800/50 hover:bg-zinc-700 p-2 rounded-full transition-all border border-zinc-600 z-50">
                <X className="w-6 h-6" />
              </button>
              
              <div className="text-center mb-10 relative z-10">
                <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-500 tracking-tight flex items-center justify-center gap-3">
                  <Network className="w-8 h-8 text-cyan-400" /> Distributed Architecture
                </h2>
                <p className="text-zinc-400 text-sm mt-2 font-medium tracking-wide">Live Telemetry Flow Visualization</p>
              </div>
              
              <div className="flex flex-col items-center w-full max-w-2xl mx-auto pb-8">
                
                {/* Node 1: Users */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl border border-blue-500/30"><Users className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Global Traffic</h3>
                      <p className="text-xs text-zinc-400">Incoming Requests</p>
                    </div>
                  </div>
                </motion.div>
                
                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 2: Load Balancer */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/30"><Layers className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Load Balancer</h3>
                      <p className="text-xs text-zinc-400">Traffic Distribution</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-bold text-zinc-500 uppercase">Live Load</div>
                    <div className="text-lg font-black text-cyan-400">{trafficRps || 53} RPS</div>
                  </div>
                </motion.div>
                
                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 3: Rate Limiter */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-red-500/20 text-red-400 rounded-xl border border-red-500/30"><ShieldAlert className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Token Bucket Rate Limiter</h3>
                      <p className="text-xs text-zinc-400">DDoS & Bot Mitigation</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-bold text-zinc-500 uppercase flex items-center gap-1 justify-end"><Bot className="w-3 h-3 text-red-500"/> Blocked</div>
                    <div className="text-lg font-black text-red-500">{blockedSpam || 91}</div>
                  </div>
                </motion.div>
                
                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 4: Queue Engine */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/30"><Package className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Order Queue Engine</h3>
                      <p className="text-xs text-zinc-400">Async Message Broker</p>
                    </div>
                  </div>
                </motion.div>

                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 5: Inventory Manager */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-violet-500/20 text-violet-400 rounded-xl border border-violet-500/30"><Zap className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Concurrent Inventory</h3>
                      <p className="text-xs text-zinc-400">Atomic State Deductions</p>
                    </div>
                  </div>
                </motion.div>

                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 6: AI Fraud Detection */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="arch-node ai-pulse rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between border-fuchsia-500/50 shadow-[0_0_20px_rgba(217,70,239,0.2)]">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-fuchsia-500/20 text-fuchsia-400 rounded-xl border border-fuchsia-500/30"><Hexagon className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">AI Fraud Engine</h3>
                      <p className="text-xs text-zinc-400">Real-time Risk Scoring</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-bold text-zinc-500 uppercase flex items-center gap-1 justify-end"><Activity className="w-3 h-3 text-fuchsia-400"/> Latency</div>
                    <div className="text-lg font-black text-fuchsia-400">{avgLatency ? avgLatency.toFixed(1) : "2.4"} ms</div>
                  </div>
                </motion.div>

                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 7: Payment Gateway */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/30"><CreditCard className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Payment Gateway</h3>
                      <p className="text-xs text-zinc-400">Secure Transactions</p>
                    </div>
                  </div>
                </motion.div>

                <div className="connector-down"><div className="particle-down"></div><div className="particle-down" style={{ animationDelay: '0.75s' }}></div></div>

                {/* Node 8: Analytics */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }} className="arch-node rounded-2xl p-4 w-full sm:w-3/4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl border border-blue-500/30"><BarChart2 className="w-6 h-6" /></div>
                    <div className="text-left">
                      <h3 className="font-bold text-white text-lg">Real-Time Analytics</h3>
                      <p className="text-xs text-zinc-400">Live Dashboard & Logs</p>
                    </div>
                  </div>
                </motion.div>

              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
