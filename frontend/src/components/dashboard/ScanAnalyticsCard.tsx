import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Target } from "lucide-react";

export const ScanAnalyticsCard = ({ analytics, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm h-full flex flex-col"
    >
      <div className="flex items-center gap-2 mb-6 text-white">
        <BarChart3 className="w-5 h-5 text-emerald-400" />
        <h2 className="text-xl font-bold">Scan Analytics</h2>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1">
        <div className="col-span-2 flex items-center justify-between p-4 rounded-xl bg-slate-950/50 border border-slate-800">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase mb-1">Most Scanned Target</p>
            <p className="text-white font-medium truncate" title={analytics?.most_scanned_domain}>{analytics?.most_scanned_domain || "None"}</p>
          </div>
          <Target className="w-5 h-5 text-slate-500" />
        </div>

        <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-center">
          <p className="text-2xl font-bold text-white mb-1">{analytics?.scans_week}</p>
          <p className="text-xs text-slate-400 font-semibold uppercase">This Week</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-emerald-500/5" />
          <p className="text-2xl font-bold text-emerald-400 mb-1">{analytics?.daily_growth}</p>
          <p className="text-xs text-emerald-500/80 font-semibold uppercase flex items-center justify-center gap-1">
            <TrendingUp className="w-3 h-3" /> Growth
          </p>
        </div>
        
        <div className="col-span-2 flex items-center justify-between mt-2 pt-4 border-t border-slate-800 text-xs">
          <span className="text-slate-400">Most common type:</span>
          <span className="text-white uppercase font-medium bg-slate-800 px-2 py-0.5 rounded">{analytics?.most_common_scan_type}</span>
        </div>
      </div>
    </motion.div>
  );
};
