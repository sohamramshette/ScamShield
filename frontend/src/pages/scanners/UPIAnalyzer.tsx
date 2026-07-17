import { Layout } from "@/components/layout/Layout";
import { CreditCard, Search } from "lucide-react";
import { motion } from "framer-motion";

const UPIAnalyzer = () => {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            UPI Analyzer
          </h1>
          <p className="text-slate-400">
            Analyze UPI IDs to detect fraudulent merchants, known scammers, and
            suspicious reputation.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-sm mb-8"
        >
          <div className="flex gap-4">
            <div className="relative flex-1">
              <CreditCard className="absolute left-4 top-4 w-5 h-5 text-slate-500" />
              <input
                type="text"
                placeholder="merchant@bank"
                className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-lg"
              />
            </div>
            <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2">
              <Search className="w-5 h-5" />
              Analyze ID
            </button>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default UPIAnalyzer;
