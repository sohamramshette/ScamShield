import { Link, useLocation } from "react-router-dom";
import {
  Shield,
  LayoutDashboard,
  Globe,
  QrCode,
  CreditCard,
  History,
  Settings,
  LogOut,
} from "lucide-react";
import { type ReactNode } from "react";

export const Layout = ({ children }: { children: ReactNode }) => {
  const location = useLocation();

  const links = [
    { name: "Threat Center", path: "/dashboard", icon: LayoutDashboard },
    { name: "Website Scanner", path: "/dashboard/website", icon: Globe },
    { name: "QR Scanner", path: "/dashboard/qr", icon: QrCode },
    { name: "UPI Analyzer", path: "/dashboard/upi", icon: CreditCard },
    { name: "Scan History", path: "/dashboard/history", icon: History },
    { name: "Settings", path: "/dashboard/settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 border-r border-slate-800 flex flex-col backdrop-blur-xl">
        <div className="p-6 flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold text-white tracking-tight">
            ScamShield AI
          </span>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {links.map((link) => {
            const active =
              location.pathname === link.path ||
              (link.path !== "/dashboard" &&
                location.pathname.startsWith(link.path));
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${active ? "bg-blue-600/10 text-blue-400 border border-blue-500/20" : "text-slate-400 hover:bg-slate-800/50 hover:text-white"}`}
              >
                <link.icon
                  className={`w-5 h-5 ${active ? "text-blue-400" : ""}`}
                />
                <span className="font-medium">{link.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <Link
            to="/"
            className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Logout</span>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-[120px] pointer-events-none" />
        <div className="p-8 relative z-10">{children}</div>
      </main>
    </div>
  );
};
