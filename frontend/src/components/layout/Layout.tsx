import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Globe,
  QrCode,
  CreditCard,
  Mail,
  MessageSquare,
  History,
  Settings,
  LogOut,
  Smartphone,
  Bell,
  Activity,
  ChevronLeft,
  ChevronRight,
  User,
  Clock,
} from "lucide-react";
import { type ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";

const links = [
  { name: "Overview", path: "/dashboard", icon: LayoutDashboard, group: "Core" },
  { name: "Threat Center", path: "/dashboard/threat-center", icon: Activity, group: "Core" },
  { name: "Website", path: "/dashboard/website", icon: Globe, group: "Analyzers" },
  { name: "QR Code", path: "/dashboard/qr", icon: QrCode, group: "Analyzers" },
  { name: "UPI", path: "/dashboard/upi", icon: CreditCard, group: "Analyzers" },
  { name: "Email", path: "/dashboard/email", icon: Mail, group: "Analyzers" },
  { name: "SMS", path: "/dashboard/message", icon: MessageSquare, group: "Analyzers" },
  { name: "APK", path: "/dashboard/apk", icon: Smartphone, group: "Analyzers" },
  { name: "Scan History", path: "/dashboard/history", icon: History, group: "System" },
  { name: "Settings", path: "/dashboard/settings", icon: Settings, group: "System" },
];

export const Layout = ({ children }: { children: ReactNode }) => {
  const location = useLocation();
  const { logout } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [time, setTime] = useState(new Date());
  
  // New states for Profile and Notifications
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await api.get("/history/");
        const recent = (data || []).slice(0, 5).map((scan: any) => ({
          id: scan.id,
          title: `${(scan.scan_type || 'Unknown').toUpperCase()} Scan Completed`,
          description: `Target: ${scan.target_summary || 'Unknown'} - Risk Score: ${scan.risk_score}`,
          time: new Date(scan.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
        }));
        setNotifications(recent);
        setUnreadCount(recent.length);
      } catch (err) {
        console.error("Failed to load notifications", err);
      }
    };
    fetchNotifications();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const timeString = time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' });
  const dateString = time.toLocaleDateString('en-US', { month: 'short', day: '2-digit' });

  return (
    <div className="min-h-screen bg-background flex overflow-hidden text-foreground selection:bg-primary/30">
      
      {/* Sidebar */}
      <motion.aside 
        initial={false}
        animate={{ width: isSidebarCollapsed ? "80px" : "280px" }}
        className="bg-card/40 border-r border-border backdrop-blur-3xl flex flex-col relative z-20 shadow-2xl"
      >
        {/* Toggle Button */}
        <button 
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          className="absolute -right-3 top-8 bg-card border border-border text-muted-foreground hover:text-primary p-1.5 rounded-full z-30 transition-colors shadow-lg"
        >
          {isSidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>

        {/* Brand */}
        <div className="h-20 flex items-center px-6 border-b border-white/5">
          <AnimatePresence>
            {!isSidebarCollapsed && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
              >
                <Link to="/dashboard" className="text-3xl font-black font-mono tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500 whitespace-nowrap hover:opacity-80 transition-opacity">
                  ScamShield
                </Link>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto custom-scrollbar py-6 px-3 flex flex-col gap-2">
          {links.map((link) => {
            const active = location.pathname === link.path || (link.path !== "/dashboard" && location.pathname.startsWith(link.path));
            
            return (
              <Link key={link.path} to={link.path} className="relative group">
                {active && (
                  <motion.div 
                    layoutId="sidebar-active"
                    className="absolute inset-0 bg-primary/10 border border-primary/20 rounded-xl"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <div className={`relative flex items-center px-3 py-3 rounded-xl transition-colors ${active ? "text-primary" : "text-muted-foreground hover:text-foreground hover:bg-white/5"}`}>
                  <link.icon className={`w-5 h-5 flex-shrink-0 ${active ? "text-primary shadow-glow" : ""}`} />
                  <AnimatePresence>
                    {!isSidebarCollapsed && (
                      <motion.span 
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "auto" }}
                        exit={{ opacity: 0, width: 0 }}
                        className="ml-4 font-sans text-sm font-medium whitespace-nowrap overflow-hidden"
                      >
                        {link.name}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>
              </Link>
            );
          })}
        </div>

        {/* User Footer */}
        <div className="p-4 border-t border-white/5">
          <button onClick={logout} className="w-full flex items-center px-3 py-3 text-muted-foreground hover:text-danger hover:bg-danger/10 rounded-xl transition-all group">
            <LogOut className="w-5 h-5 flex-shrink-0 group-hover:shadow-glow-danger" />
            <AnimatePresence>
              {!isSidebarCollapsed && (
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="ml-4 font-sans text-sm font-medium whitespace-nowrap"
                >
                  Terminate Session
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        
        {/* Topbar */}
        <header className="h-20 bg-background/50 backdrop-blur-xl border-b border-border flex items-center justify-between px-8 z-10">
          
          {/* Empty spacer to push right actions to the end, or you can use justify-end */}
          <div className="flex-1" />

          {/* Right Actions */}
          <div className="flex items-center gap-6 ml-8">
            <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-card/50 border border-border rounded-lg">
              <Clock className="w-4 h-4 text-primary" />
              <span className="font-mono text-xs text-muted-foreground">{dateString}</span>
              <span className="font-mono text-sm font-bold text-foreground ml-1">{timeString}</span>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 bg-success/5 border border-success/20 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="font-mono text-xs font-bold text-success uppercase tracking-wider">Sys: Online</span>
            </div>

            <div className="flex items-center gap-3 relative">
              <button 
                onClick={() => {
                  setIsNotificationsOpen(!isNotificationsOpen);
                  if (!isNotificationsOpen) setUnreadCount(0);
                }}
                className="relative p-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-lg transition-colors"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full border border-background" />}
              </button>

              {/* Notifications Dropdown */}
              <AnimatePresence>
                {isNotificationsOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    className="absolute top-full right-12 mt-4 w-80 bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl overflow-hidden z-50"
                  >
                    <div className="p-4 border-b border-border flex justify-between items-center bg-black/20">
                      <h3 className="font-bold text-white text-sm">Notifications</h3>
                      {unreadCount > 0 && <span className="text-[10px] px-2 py-0.5 bg-primary/20 text-primary rounded-full font-mono uppercase">{unreadCount} New</span>}
                    </div>
                    <div className="p-2 max-h-[300px] overflow-y-auto">
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-sm text-slate-500">No recent activity</div>
                      ) : (
                        notifications.map(notif => (
                          <div key={notif.id} className="p-3 hover:bg-white/5 rounded-lg cursor-pointer transition-colors border-l-2 border-primary mb-1 bg-primary/5">
                            <p className="text-sm text-white font-medium">{notif.title}</p>
                            <p className="text-xs text-slate-400 mt-1">{notif.description}</p>
                            <p className="text-[10px] text-primary mt-2 font-mono">{notif.time}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="w-px h-6 bg-border mx-1" />
              <div className="relative">
                <button 
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-2 p-1.5 hover:bg-white/5 rounded-lg transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-white shadow-glow">
                    <User className="w-4 h-4" />
                  </div>
                </button>

                {/* Profile Dropdown */}
                <AnimatePresence>
                  {isProfileOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute top-full right-0 mt-4 w-56 bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl overflow-hidden z-50 p-2"
                    >
                      <Link 
                        to="/dashboard/settings" 
                        onClick={() => setIsProfileOpen(false)}
                        className="flex items-center gap-3 w-full px-3 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                        Account Settings
                      </Link>
                      <div className="h-px bg-border my-1 mx-2" />
                      <button 
                        onClick={() => {
                          setIsProfileOpen(false);
                          logout();
                        }}
                        className="flex items-center gap-3 w-full px-3 py-2.5 text-sm text-danger hover:bg-danger/10 rounded-lg transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Log Out
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto custom-scrollbar relative">
          <AnimatePresence mode="wait">
            <motion.div 
              key={location.pathname}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="p-8 min-h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};
