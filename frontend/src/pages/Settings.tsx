import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { User, Bell, Shield, Key } from "lucide-react";

const Settings = () => {
  const [activeTab, setActiveTab] = useState("Profile");
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };
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
              { name: "Profile", icon: User },
              { name: "Security", icon: Shield },
              { name: "Notifications", icon: Bell },
              { name: "API Keys", icon: Key },
            ].map((tab, i) => (
              <button
                key={i}
                onClick={() => setActiveTab(tab.name)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${activeTab === tab.name ? "bg-primary/10 text-primary font-medium border border-primary/20" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.name}
              </button>
            ))}
          </div>

          <div className="md:col-span-3 bg-slate-900/50 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
            {activeTab === "Profile" && (
              <>
                <h2 className="text-xl font-bold text-white mb-6">Profile Information</h2>
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
                      <label className="text-sm font-medium text-slate-300">Full Name</label>
                      <input type="text" defaultValue="Admin User" className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-white focus:outline-none focus:border-primary transition-colors" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-slate-300">Email Address</label>
                      <input type="email" defaultValue="admin@scamshield.ai" className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-slate-400 focus:outline-none cursor-not-allowed" disabled />
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === "Security" && (
              <>
                <h2 className="text-xl font-bold text-white mb-6">Security Settings</h2>
                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Current Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-white focus:outline-none focus:border-primary transition-colors" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-white focus:outline-none focus:border-primary transition-colors" />
                  </div>
                </div>
              </>
            )}

            {activeTab === "Notifications" && (
              <>
                <h2 className="text-xl font-bold text-white mb-6">Notifications</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded-lg border border-slate-800">
                    <div>
                      <h4 className="text-white font-medium">Email Alerts</h4>
                      <p className="text-sm text-slate-400">Receive alerts for critical threats</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-4 h-4 accent-primary" />
                  </div>
                  <div className="flex items-center justify-between p-4 bg-slate-950/50 rounded-lg border border-slate-800">
                    <div>
                      <h4 className="text-white font-medium">Push Notifications</h4>
                      <p className="text-sm text-slate-400">Receive instant push notifications</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-4 h-4 accent-primary" />
                  </div>
                </div>
              </>
            )}

            {activeTab === "API Keys" && (
              <>
                <h2 className="text-xl font-bold text-white mb-6">API Keys</h2>
                <div className="space-y-6">
                  <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg text-primary text-sm font-medium mb-4">
                    These keys allow programmatic access to the ScamShield intelligence API. Keep them secret.
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Production Key</label>
                    <div className="flex gap-3">
                      <input type="password" defaultValue="sk_live_abcdef123456789" className="w-full bg-slate-950/50 border border-slate-700 rounded-lg py-2.5 px-4 text-slate-400 focus:outline-none cursor-not-allowed" disabled />
                      <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700">Regenerate</button>
                    </div>
                  </div>
                </div>
              </>
            )}

            <div className="pt-6 mt-6 border-t border-slate-800 flex justify-end">
              <button 
                onClick={handleSave}
                className="px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-lg font-medium transition-all shadow-lg shadow-primary/20 flex items-center gap-2"
              >
                {isSaved ? "Saved!" : "Save Changes"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings;
