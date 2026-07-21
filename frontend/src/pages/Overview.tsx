import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { Link } from "react-router-dom";
import { 
  ShieldAlert, Activity, ShieldCheck, 
  Globe, QrCode, CreditCard, Mail, MessageSquare, Smartphone,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import { SystemHealthCard } from "@/components/dashboard/SystemHealthCard";
import { AIInsightCard } from "@/components/dashboard/AIInsightCard";
import { useAuth } from "@/context/AuthContext";

const Overview = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get("/dashboard/stats");
        setData(response);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
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
        </div>
      </Layout>
    );
  }

  const { overview, system_health, ai_insights } = data || {};

  const analyzers = [
    { name: "Website Scanner", path: "/dashboard/website", icon: Globe, desc: "Analyze URLs and domains", color: "text-blue-400", bg: "bg-blue-400/10", border: "border-blue-400/20" },
    { name: "QR Code", path: "/dashboard/qr", icon: QrCode, desc: "Scan QR codes for malicious links", color: "text-purple-400", bg: "bg-purple-400/10", border: "border-purple-400/20" },
    { name: "UPI Analyzer", path: "/dashboard/upi", icon: CreditCard, desc: "Verify UPI IDs and payment links", color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/20" },
    { name: "Email Analyzer", path: "/dashboard/email", icon: Mail, desc: "Check email headers and content", color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-400/20" },
    { name: "SMS Analyzer", path: "/dashboard/message", icon: MessageSquare, desc: "Analyze suspicious text messages", color: "text-pink-400", bg: "bg-pink-400/10", border: "border-pink-400/20" },
    { name: "APK Analyzer", path: "/dashboard/apk", icon: Smartphone, desc: "Decompile and scan Android apps", color: "text-red-400", bg: "bg-red-400/10", border: "border-red-400/20" },
  ];

  const username = user?.email?.split('@')[0] || 'Commander';
  const displayName = username.charAt(0).toUpperCase() + username.slice(1);

  return (
    <Layout>
      <div className="flex flex-col gap-8 pb-12 max-w-[1800px] mx-auto">
        
        {/* Welcome Banner */}
        <div className="relative overflow-hidden rounded-3xl bg-card border border-border p-8 md:p-12">
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
          <div className="relative z-10 max-w-3xl">
            <h1 className="text-4xl md:text-5xl font-heading font-black text-white tracking-tight mb-4">
              Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">{displayName}</span>
            </h1>
            <p className="text-muted-foreground text-lg mb-8">
              Here is your executive summary for today. The AI intelligence grid is actively monitoring threats.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/dashboard/threat-center" className="px-6 py-3 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-xl transition-colors shadow-glow flex items-center gap-2">
                <Activity className="w-5 h-5" /> SOC Dashboard
              </Link>
              <Link to="/dashboard/website" className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold rounded-xl transition-colors flex items-center gap-2">
                <Zap className="w-5 h-5" /> Quick Scan
              </Link>
            </div>
          </div>
        </div>

        {/* Executive Stats & AI */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="signature-panel p-6 flex flex-col justify-center">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-primary/10 rounded-xl text-primary"><Activity className="w-6 h-6" /></div>
                <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-widest">Total Scans Today</h3>
              </div>
              <p className="text-4xl font-heading font-black text-white">{overview?.todays_scans || 0}</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="signature-panel p-6 flex flex-col justify-center">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-danger/10 rounded-xl text-danger"><ShieldAlert className="w-6 h-6" /></div>
                <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-widest">High Risk Threats</h3>
              </div>
              <p className="text-4xl font-heading font-black text-danger">{overview?.high_risk_threats || 0}</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="signature-panel p-6 flex flex-col justify-center">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-success/10 rounded-xl text-success"><ShieldCheck className="w-6 h-6" /></div>
                <h3 className="font-mono text-xs text-muted-foreground uppercase tracking-widest">Safe Assets</h3>
              </div>
              <p className="text-4xl font-heading font-black text-success">{overview?.safe_analyses || 0}</p>
            </motion.div>
          </div>
          
          <div className="lg:col-span-4 h-full">
            <AIInsightCard insights={ai_insights} delay={0.3} />
          </div>
        </div>

        {/* Analyzers Grid */}
        <div>
          <h2 className="text-xl font-heading font-bold text-white mb-6 flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary" /> Analysis Engines
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analyzers.map((tool, idx) => (
              <motion.div key={tool.path} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * idx }}>
                <Link to={tool.path} className="group flex flex-col p-6 signature-panel hover:border-primary/50 transition-all hover:-translate-y-1 hover:shadow-glow h-full cursor-pointer">
                  <div className={`w-12 h-12 rounded-2xl ${tool.bg} ${tool.border} border flex items-center justify-center mb-4 transition-transform group-hover:scale-110`}>
                    <tool.icon className={`w-6 h-6 ${tool.color}`} />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{tool.name}</h3>
                  <p className="text-muted-foreground text-sm font-sans">{tool.desc}</p>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="mt-4">
           <SystemHealthCard system={system_health} performance={null} delay={0.4} />
        </div>

      </div>
    </Layout>
  );
};

export default Overview;
