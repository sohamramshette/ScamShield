import React, { Suspense, lazy } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// Eager load critical routes
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";

import { AuthProvider, useAuth } from "@/context/AuthContext";

// Lazy load dashboard routes
const ThreatCenter = lazy(() => import("@/pages/ThreatCenter"));
const WebsiteScanner = lazy(() => import("@/pages/scanners/WebsiteScanner"));
const QRScanner = lazy(() => import("@/pages/scanners/QRScanner"));
const UPIAnalyzer = lazy(() => import("@/pages/scanners/UPIAnalyzer"));
const ScanHistory = lazy(() => import("@/pages/ScanHistory"));
const Settings = lazy(() => import("@/pages/Settings"));

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <PageLoader />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  
  return <>{children}</>;
};

// Fallback loader component
const PageLoader = () => (
  <div className="flex h-[50vh] w-full items-center justify-center">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
  </div>
);

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />

              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <ThreatCenter />
                  </PrivateRoute>
                }
              />
              <Route
                path="/dashboard/website"
                element={
                  <PrivateRoute>
                    <WebsiteScanner />
                  </PrivateRoute>
                }
              />
              <Route
                path="/dashboard/qr"
                element={
                  <PrivateRoute>
                    <QRScanner />
                  </PrivateRoute>
                }
              />
              <Route
                path="/dashboard/upi"
                element={
                  <PrivateRoute>
                    <UPIAnalyzer />
                  </PrivateRoute>
                }
              />
              <Route
                path="/dashboard/history"
                element={
                  <PrivateRoute>
                    <ScanHistory />
                  </PrivateRoute>
                }
              />
              <Route
                path="/dashboard/settings"
                element={
                  <PrivateRoute>
                    <Settings />
                  </PrivateRoute>
                }
              />
              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
