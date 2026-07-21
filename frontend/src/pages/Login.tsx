import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { Mail, Lock, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { api, API_URL } from "@/lib/api";

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();
  
  // Issue 3: Redirect authenticated users away from Login page
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        // OAuth2 Password Request Form format requires form-urlencoded data
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        
        const response = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error?.message || data.detail || "Login failed");
        
        // Fetch user details or use email as minimal user object
        // In a full implementation, you'd have a /users/me endpoint
        login(data.access_token, { id: 1, email: email });
      } else {
        const data = await api.post("/auth/register", { email, password });
        // Auto-login after successful registration
        if (data.email) {
            setIsLogin(true);
            setError("Registration successful! Please sign in.");
        }
      }
    } catch (err: any) {
      setError(err.message || "An error occurred during authentication");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 -left-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-1/4 -right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />

      <Link
        to="/"
        className="absolute top-8 left-8 flex items-center gap-2 text-white hover:text-blue-400 transition-colors"
      >
        <span className="text-3xl font-black font-mono tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500">ScamShield</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md bg-slate-900/60 border border-slate-800 p-8 rounded-2xl backdrop-blur-xl shadow-2xl relative z-10"
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="text-slate-400">
            {isLogin
              ? "Sign in to access your threat intelligence dashboard."
              : "Join to start analyzing and detecting threats."}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className={`p-3 text-sm rounded-lg border ${error.includes("successful") ? "bg-green-500/10 border-green-500/20 text-green-400" : "bg-red-500/10 border-red-500/20 text-red-400"}`}>
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl py-3 font-semibold transition-all mt-6 flex items-center justify-center gap-2 group shadow-[0_0_15px_rgba(37,99,235,0.3)]"
          >
            {loading ? "Please wait..." : isLogin ? "Sign In" : "Sign Up"}
            {!loading && <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-sm text-slate-400 hover:text-blue-400 transition-colors"
          >
            {isLogin
              ? "Don't have an account? Sign up"
              : "Already have an account? Sign in"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
