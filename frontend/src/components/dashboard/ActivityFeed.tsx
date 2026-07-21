import { motion } from "framer-motion";

export const ActivityFeed = ({ activities, delay = 0 }: any) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay }}
      className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm flex flex-col h-full"
    >
      <h2 className="text-xl font-bold text-white mb-4">Live Threat Activity</h2>
      <div className="space-y-3 overflow-y-auto flex-1 pr-2 custom-scrollbar">
        {activities?.map((activity: any, i: number) => {
          let riskColor = "text-emerald-400 bg-emerald-400/10 border-emerald-500/20";
          let riskLabel = "Safe";
          if (activity.risk_score >= 40) {
            riskColor = "text-amber-400 bg-amber-400/10 border-amber-500/20";
            riskLabel = "Warning";
          }
          if (activity.risk_score >= 70) {
            riskColor = "text-red-400 bg-red-400/10 border-red-500/20";
            riskLabel = "Critical";
          }

          const date = new Date(activity.created_at);
          const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          return (
            <div
              key={i}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-950/50 border border-slate-800 hover:border-slate-700 transition-colors"
            >
              <div className="min-w-0 flex-1 mr-4">
                <p className="font-medium text-white mb-0.5 truncate" title={activity.target}>
                  {activity.target}
                </p>
                <div className="flex gap-2 text-xs text-slate-400">
                  <span className="uppercase">{activity.type}</span>
                  <span>&bull;</span>
                  <span>{timeString}</span>
                  <span>&bull;</span>
                  <span>Conf: {activity.confidence}%</span>
                </div>
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-medium border ${riskColor}`}>
                {riskLabel}
              </div>
            </div>
          );
        })}
        {(!activities || activities.length === 0) && (
          <div className="text-center text-slate-500 py-8">No recent activity</div>
        )}
      </div>
    </motion.div>
  );
};
