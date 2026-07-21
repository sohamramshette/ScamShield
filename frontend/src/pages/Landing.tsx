import { Link, Navigate } from "react-router-dom";
import {
  Shield,
  ShieldAlert,
  Zap,
  Lock,
  ScanLine,
  Activity,
} from "lucide-react";
import { motion } from "framer-motion";

import { useAuth } from "@/context/AuthContext";

const Landing = () => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-red-600/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Navbar Placeholder */}
      <nav className="absolute top-0 w-full p-6 flex justify-between items-center z-10 max-w-7xl">
        <div className="flex items-center gap-2 z-10 cursor-pointer">
          <span className="text-3xl font-black font-mono tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500">
            ScamShield
          </span>
        </div>
        <div className="flex gap-4">
          <Link
            to="/login"
            className="px-5 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
          >
            Login
          </Link>
          <Link
            to="/login"
            className="px-5 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)]"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="z-10 flex flex-col items-center text-center max-w-4xl px-4 mt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8"
        >
          <Zap className="w-4 h-4" />
          <span>IBM Granite Powered Intelligence</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-6xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 mb-6"
        >
          Detect. Analyze.
          <br />
          Explain. Protect.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10"
        >
          AI-powered cyber fraud detection platform that analyzes websites, QR
          codes, and suspicious messages before they can harm you.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <Link
            to="/dashboard"
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-semibold text-lg transition-all shadow-[0_0_30px_rgba(37,99,235,0.4)] flex items-center gap-2 justify-center"
          >
            <ScanLine className="w-5 h-5" />
            Start Scanning
          </Link>
          <Link
            to="/dashboard"
            className="px-8 py-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 backdrop-blur-sm text-white rounded-full font-semibold text-lg transition-all flex items-center gap-2 justify-center"
          >
            <Activity className="w-5 h-5" />
            Live Demo
          </Link>
        </motion.div>
      </main>

      {/* Features Grid */}
      <div className="z-10 mt-32 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl px-4 w-full pb-20">
        {[
          {
            title: "Website Scanner",
            desc: "Detects phishing, typosquatting, and malicious domains instantly.",
            icon: ShieldAlert,
            color: "text-red-400",
          },
          {
            title: "Risk Engine",
            desc: "Aggregates intel from VirusTotal, Safe Browsing, and WHOIS.",
            icon: Lock,
            color: "text-blue-400",
          },
          {
            title: "AI Explanations",
            desc: "Human-readable threat breakdowns powered by IBM Granite.",
            icon: Activity,
            color: "text-emerald-400",
          },
        ].map((feat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 backdrop-blur-xl hover:border-slate-700 transition-colors group"
          >
            <div
              className={`p-3 rounded-xl bg-slate-800/50 w-fit mb-4 group-hover:scale-110 transition-transform ${feat.color}`}
            >
              <feat.icon className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {feat.title}
            </h3>
            <p className="text-slate-400">{feat.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Landing;
