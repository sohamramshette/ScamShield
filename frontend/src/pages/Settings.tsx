import { Layout } from "@/components/layout/Layout";
import { User, Bell, Shield, Key } from "lucide-react";

const Settings = () => {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            Settings
          </h1>
          <p className="text-slate-400">
            Manage your account preferences and API integrations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1 space-y-2">
            {[
              { name: "Profile", icon: User, active: true },
              { name: "Security", icon: Shield, active: false },
              { name: "Notifications", icon: Bell, active: false },
              { name: "API Keys", icon: Key, active: false },
            ].map((tab, i) => (
              <button
                key={i}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${tab.active ? "bg-blue-600/10 text-blue-400 font-medium" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.name}
              </button>
            ))}
          </div>

          <div className="md:col-span-3 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-xl font-bold text-white mb-6">
              Profile Information
            </h2>

            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center border-2 border-slate-700">
                  <User className="w-8 h-8 text-slate-400" />
                </div>
                <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700 text-sm">
                  Change Avatar
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Full Name
                  </label>
                  <input
                    type="text"
                    defaultValue="Admin User"
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Email Address
                  </label>
                  <input
                    type="email"
                    defaultValue="admin@scamshield.ai"
                    className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-slate-400 focus:outline-none cursor-not-allowed"
                    disabled
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800 flex justify-end">
                <button className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors shadow-lg shadow-blue-500/20">
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;
