import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { ShieldAlert, Activity, RefreshCw, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import { ThreatChart } from "@/components/dashboard/ThreatChart";
import { ThreatFeed } from "@/components/dashboard/ThreatFeed";
import { SystemHealthCard } from "@/components/dashboard/SystemHealthCard";
import { AIInsightCard } from "@/components/dashboard/AIInsightCard";

const ThreatCenter = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const fetchDashboard = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const response = await api.get("/dashboard/stats");
      setData(response);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to load SOC dashboard");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(() => fetchDashboard(true), 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh] flex-col gap-6">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 border-[3px] border-border rounded-full" />
            <div className="absolute inset-0 border-[3px] border-primary rounded-full border-t-transparent animate-spin" />
            <ShieldAlert className="absolute inset-0 m-auto w-8 h-8 text-primary animate-pulse" />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-heading font-bold text-white tracking-tight">Initializing Workstation</h2>
            <p className="text-muted-foreground font-mono text-xs uppercase tracking-widest mt-2">Connecting to Intelligence Grid...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error && !data) {
    return (
      <Layout>
        <div className="p-8 m-8 bg-danger/5 border border-danger/20 text-danger rounded-2xl flex flex-col items-center justify-center min-h-[40vh]">
          <ShieldAlert className="w-16 h-16 mb-4 opacity-50" />
          <h2 className="text-xl font-heading font-bold mb-2">Connection Lost</h2>
          <p className="text-sm font-sans opacity-80">{error}</p>
        </div>
      </Layout>
    );
  }

  const { overview, risk_distribution, scan_trend, threat_feed, system_health, ai_insights } = data;

  return (
    <Layout>
      <div className="flex flex-col gap-8 pb-12 max-w-[1800px] mx-auto">
        
        {/* Header Area */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 relative">
          <div className="absolute -top-10 -left-10 w-96 h-96 bg-primary/20 blur-[150px] rounded-full pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
              <span className="px-2 py-0.5 bg-primary/10 border border-primary/20 text-primary text-[10px] font-mono font-bold uppercase tracking-widest rounded">SOC Alpha</span>
              <span className="px-2 py-0.5 bg-success/10 border border-success/20 text-success text-[10px] font-mono font-bold uppercase tracking-widest rounded flex items-center gap-1">
                <div className="w-1.5 h-1.5 bg-success rounded-full animate-pulse" /> Live
              </span>
            </div>
            <h1 className="text-5xl font-heading font-black text-white tracking-tighter">
              SOC Operations <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Center</span>
            </h1>
            <p className="text-muted-foreground font-sans mt-2 text-lg">Real-time Threat Intelligence</p>
          </div>

          <div className="relative z-10 flex items-center gap-4 bg-card/50 border border-border p-2 rounded-2xl backdrop-blur-md">
            <button 
              onClick={() => fetchDashboard(true)}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 text-primary ${refreshing ? "animate-spin" : ""}`} />
              <span className="font-sans font-medium text-sm text-foreground">Sync Grid</span>
            </button>
          </div>
        </div>

        {/* Asymmetric Layout - Top Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main KPI Hero - Spans 8 cols */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-8 signature-panel p-8 md:p-10 flex flex-col justify-between relative"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-danger/10 blur-[100px] rounded-full pointer-events-none" />
            
            <div className="flex justify-between items-start mb-12 relative z-10">
              <div>
                <h3 className="text-sm font-mono font-bold text-muted-foreground uppercase tracking-widest mb-1">Total Threats Intercepted</h3>
                <div className="flex items-baseline gap-3">
                  <span className="text-7xl font-heading font-black text-white">{overview?.high_risk_threats + overview?.safe_analyses}</span>
                  <span className="text-success text-sm font-mono font-bold flex items-center"><TrendingUp className="w-4 h-4 mr-1"/> +12.4%</span>
                </div>
              </div>
              <div className="w-16 h-16 rounded-2xl bg-danger/10 border border-danger/20 flex items-center justify-center shadow-glow-danger">
                <ShieldAlert className="w-8 h-8 text-danger" />
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 relative z-10">
              <div className="border-l border-white/10 pl-4">
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">Critical Risks</p>
                <p className="text-2xl font-bold text-danger">{overview?.high_risk_threats}</p>
              </div>
              <div className="border-l border-white/10 pl-4">
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">Safe Assets</p>
                <p className="text-2xl font-bold text-success">{overview?.safe_analyses}</p>
              </div>
              <div className="border-l border-white/10 pl-4">
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">AI Confidence</p>
                <p className="text-2xl font-bold text-primary">{overview?.average_confidence}%</p>
              </div>
              <div className="border-l border-white/10 pl-4">
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">Avg Latency</p>
                <p className="text-2xl font-bold text-secondary">{overview?.average_scan_time}</p>
              </div>
            </div>
          </motion.div>

          {/* AI Insights - Spans 4 cols */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-4 h-full"
          >
            <AIInsightCard insights={ai_insights} delay={0} />
          </motion.div>
        </div>

        {/* Asymmetric Layout - Middle Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Threat Feed - Spans 4 cols */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-5 h-[600px] signature-panel overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-border flex justify-between items-center bg-black/20">
              <h3 className="text-sm font-mono font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <Activity className="w-4 h-4 text-primary" /> Live Intercepts
              </h3>
              <span className="px-2 py-0.5 bg-danger/10 text-danger text-[10px] font-mono font-bold rounded animate-pulse">Monitoring</span>
            </div>
            <div className="flex-1 overflow-hidden relative">
              <ThreatFeed activities={threat_feed} delay={0} />
            </div>
          </motion.div>

          {/* Charts Area - Spans 7 cols */}
          <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="signature-panel p-6 h-72"
            >
              <ThreatChart title="Threat Distribution" data={risk_distribution} type="donut" delay={0} colors={['#ef4444', '#f59e0b', '#10b981']} />
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
              className="signature-panel p-6 h-72"
            >
              <ThreatChart title="Global Scan Volume (7D)" data={scan_trend} type="area" delay={0} />
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="md:col-span-2 signature-panel p-6 flex flex-col justify-center"
            >
               <SystemHealthCard system={system_health} performance={null} delay={0} />
            </motion.div>
          </div>

        </div>
      </div>
    </Layout>
  );
};

export default ThreatCenter;
