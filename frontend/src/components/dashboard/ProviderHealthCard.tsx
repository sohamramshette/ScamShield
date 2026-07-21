import { motion } from "framer-motion";

export const ProviderHealthCard = ({ providers, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.4, delay }}
    className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm flex flex-col h-full"
  >
    <h2 className="text-xl font-bold text-white mb-4">Provider Health</h2>
    <div className="space-y-3 overflow-y-auto flex-1 pr-2 custom-scrollbar">
      {providers.map((p: any, i: number) => {
        let statusColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
        if (p.status === "Degraded" || p.status === "Rate Limited") statusColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";
        if (p.status === "Offline" || p.status === "Disabled") statusColor = "bg-red-500/10 text-red-400 border-red-500/20";

        return (
          <div key={i} className="flex flex-col p-3 rounded-xl bg-slate-950/50 border border-slate-800">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-white">{p.name}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full border ${statusColor}`}>
                {p.status}
              </span>
            </div>
            <div className="flex justify-between text-xs text-slate-400">
              <span>Latency: {p.latency}ms</span>
              <span>Success: {p.success_rate}%</span>
              <span>Cache: {p.cache_hits} hits</span>
            </div>
          </div>
        );
      })}
      {providers.length === 0 && (
        <div className="text-center text-slate-500 py-8">No provider data available</div>
      )}
    </div>
  </motion.div>
);
