import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, Globe, AlertCircle, ArrowRight, CheckSquare, Square } from "lucide-react";
import { api } from "../services/api";

export default function Dashboard({ onScanStart }) {
  const [url, setUrl] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScan = async (e) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;

    // Basic URL sanity check
    try {
      new URL(trimmed.startsWith("http") ? trimmed : `https://${trimmed}`);
    } catch {
      setError("Please enter a valid URL (e.g. https://example.com)");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await api.startScan(trimmed, authorized);
      onScanStart(data.scan_id);
    } catch (err) {
      setError(err.message || "Failed to start scan. Please try again.");
      setLoading(false);
    }
  };

  return (
    <motion.div
      key="dashboard-hero"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="flex flex-col items-center w-full max-w-3xl mx-auto mt-16 pb-4"
    >
      {/* Logo mark */}
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center shadow-[0_0_60px_rgba(59,130,246,0.18)]">
          <ShieldCheck className="w-10 h-10 text-blue-400" strokeWidth={1.5} />
        </div>
        <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-slate-950 animate-pulse" />
      </div>

      <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-white mb-4 text-center">
        Secure<span className="text-blue-500">Lens</span>
      </h1>
      <p className="text-slate-400 text-lg text-center max-w-xl mb-12 leading-relaxed">
        Professional-grade website security auditing — headers, SSL, open ports, and vulnerability scanning in one report.
      </p>

      {/* Scan form */}
      <form
        onSubmit={handleScan}
        className="w-full bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-8 shadow-2xl"
      >
        {/* URL input */}
        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
          Target URL
        </label>
        <div className="relative flex items-center">
          <Globe className="absolute left-4 w-5 h-5 text-slate-500 pointer-events-none" />
          <input
            type="text"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(null); }}
            placeholder="https://example.com"
            disabled={loading}
            className="w-full bg-slate-950 text-white border border-slate-700 rounded-xl pl-12 pr-4 py-4 text-base placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all disabled:opacity-50"
          />
        </div>

        {/* Auth checkbox */}
        <button
          type="button"
          onClick={() => setAuthorized((v) => !v)}
          disabled={loading}
          className="mt-5 flex items-center gap-3 w-full text-left group disabled:opacity-50"
        >
          {authorized
            ? <CheckSquare className="w-5 h-5 text-blue-400 flex-shrink-0" />
            : <Square className="w-5 h-5 text-slate-500 flex-shrink-0 group-hover:text-slate-400 transition-colors" />
          }
          <span className="text-sm text-slate-300 select-none">
            I confirm I have <span className="text-slate-100 font-medium">authorization</span> to scan this target
          </span>
        </button>

        {/* Error banner */}
        <AnimatePresence>
          {error && (
            <motion.div
              key="err"
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: "auto", marginTop: 16 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="flex items-start gap-3 bg-red-500/8 border border-red-500/20 rounded-xl px-4 py-3 text-sm text-red-400"
            >
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="mt-6 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl transition-all shadow-[0_0_24px_rgba(37,99,235,0.25)] hover:shadow-[0_0_36px_rgba(37,99,235,0.4)] group"
        >
          {loading ? (
            <>
              <span className="w-5 h-5 border-2 border-white/25 border-t-white rounded-full animate-spin" />
              Initializing Scan…
            </>
          ) : (
            <>
              Launch Security Scan
              <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
            </>
          )}
        </button>
      </form>

      {/* Stats row */}
      <div className="mt-10 grid grid-cols-3 gap-4 w-full">
        {[
          { label: "Headers Analysis",    desc: "CSP, HSTS, XSS protection" },
          { label: "SSL/TLS Inspection",  desc: "Certificate & cipher checks" },
          { label: "Port & Vuln Scan",    desc: "Nmap + Nikto + Nessus" },
        ].map(({ label, desc }) => (
          <div key={label} className="bg-slate-900/40 border border-slate-800/70 rounded-xl p-4">
            <p className="text-slate-200 text-sm font-semibold mb-1">{label}</p>
            <p className="text-slate-500 text-xs">{desc}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
