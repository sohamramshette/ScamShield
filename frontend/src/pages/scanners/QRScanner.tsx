import { Layout } from "@/components/layout/Layout";
import { Upload, ScanLine } from "lucide-react";
import { motion } from "framer-motion";

const QRScanner = () => {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            QR Code Scanner
          </h1>
          <p className="text-slate-400">
            Upload or scan a QR code to detect malicious payloads, fake
            payments, or phishing links.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 backdrop-blur-sm flex flex-col items-center justify-center text-center border-dashed"
          >
            <div className="p-4 rounded-full bg-blue-500/10 text-blue-400 mb-4">
              <Upload className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Upload Image</h3>
            <p className="text-slate-400 text-sm mb-6">
              Drag and drop a QR code image here or browse your files.
            </p>
            <button className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors border border-slate-700">
              Browse Files
            </button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 backdrop-blur-sm flex flex-col items-center justify-center text-center"
          >
            <div className="p-4 rounded-full bg-emerald-500/10 text-emerald-400 mb-4">
              <ScanLine className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Use Camera</h3>
            <p className="text-slate-400 text-sm mb-6">
              Scan a QR code directly using your device's camera.
            </p>
            <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-[0_0_15px_rgba(37,99,235,0.3)]">
              Open Camera
            </button>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
};

export default QRScanner;
