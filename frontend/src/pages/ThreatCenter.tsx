import { ShieldAlert, CheckCircle, Activity, Target } from "lucide-react";
import { motion } from "framer-motion";
import { Layout } from "@/components/layout/Layout";

const StatCard = ({ title, value, icon: Icon, color, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3, delay }}
    className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-sm"
  >
    <div className="flex justify-between items-start mb-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
    <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
    <p className="text-3xl font-bold text-white">{value}</p>
  </motion.div>
);

const ThreatCenter = () => {
  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
          Threat Center
        </h1>
        <p className="text-slate-400">
          Overview of your recent scans and threat intelligence.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard
          title="Today's Scans"
          value="24"
          icon={Activity}
          color="bg-blue-500/10 text-blue-400"
          delay={0.1}
        />
        <StatCard
          title="High Risk Threats"
          value="3"
          icon={ShieldAlert}
          color="bg-red-500/10 text-red-400"
          delay={0.2}
        />
        <StatCard
          title="Safe Analyses"
          value="21"
          icon={CheckCircle}
          color="bg-emerald-500/10 text-emerald-400"
          delay={0.3}
        />
        <StatCard
          title="Threat Indicators"
          value="12"
          icon={Target}
          color="bg-amber-500/10 text-amber-400"
          delay={0.4}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.5 }}
          className="lg:col-span-2 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm"
        >
          <h2 className="text-xl font-bold text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {/* Mock recent activity */}
            {[
              {
                type: "Website",
                target: "login-secure-paypal.com",
                risk: "Critical",
                time: "10 mins ago",
                color: "text-red-400",
              },
              {
                type: "QR Code",
                target: "Payment Gateway",
                risk: "Safe",
                time: "1 hour ago",
                color: "text-emerald-400",
              },
              {
                type: "Website",
                target: "google.com",
                risk: "Safe",
                time: "2 hours ago",
                color: "text-emerald-400",
              },
            ].map((activity, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-4 rounded-xl bg-slate-950/50 border border-slate-800"
              >
                <div>
                  <p className="font-medium text-white mb-1">
                    {activity.target}
                  </p>
                  <p className="text-sm text-slate-400">
                    {activity.type} Scan • {activity.time}
                  </p>
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-xs font-medium border border-current bg-current/10 ${activity.color}`}
                >
                  {activity.risk}
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm"
        >
          <h2 className="text-xl font-bold text-white mb-4">
            Risk Distribution
          </h2>
          <div className="flex flex-col items-center justify-center h-64 border border-dashed border-slate-700 rounded-xl">
            {/* Placeholder for chart */}
            <Activity className="w-12 h-12 text-slate-600 mb-2" />
            <p className="text-slate-500 text-sm">Chart rendering here</p>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default ThreatCenter;
