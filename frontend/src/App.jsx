import { useState, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import { ShieldCheck } from "lucide-react";
import Dashboard from "./components/Dashboard";
import ScanProgress from "./components/ScanProgress";
import SecurityReport from "./components/SecurityReport";
import History from "./components/History";

export default function App() {
  const [view, setView] = useState("dashboard"); // "dashboard" | "progress" | "report"
  const [scanId, setScanId] = useState(null);
  const [scanResult, setScanResult] = useState(null);

  const goHome = useCallback(() => {
    setScanId(null);
    setScanResult(null);
    setView("dashboard");
  }, []);

  const handleScanStart = useCallback((id) => {
    setScanId(id);
    setView("progress");
  }, []);

  const handleScanComplete = useCallback((result) => {
    setScanResult(result);
    setView("report");
  }, []);

  const handleViewReport = useCallback((result) => {
    setScanResult(result);
    setView("report");
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 overflow-x-hidden">
      {/* Ambient glow — static, no JS */}
      <div
        aria-hidden
        className="fixed top-[-25%] left-[-15%] w-[55%] h-[55%] rounded-full pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(37,99,235,0.07) 0%, transparent 70%)" }}
      />
      <div
        aria-hidden
        className="fixed bottom-[-20%] right-[-10%] w-[45%] h-[45%] rounded-full pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%)" }}
      />

      {/* ── Navbar ── */}
      <header className="sticky top-0 z-50 w-full border-b border-white/[0.05] bg-slate-950/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-5 sm:px-8 h-14 flex items-center justify-between">
          <button
            onClick={goHome}
            className="flex items-center gap-2.5 group"
            aria-label="Go to dashboard"
          >
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center shadow-[0_0_14px_rgba(37,99,235,0.4)] group-hover:shadow-[0_0_20px_rgba(37,99,235,0.55)] transition-all">
              <ShieldCheck className="w-4 h-4 text-white" strokeWidth={2.5} />
            </div>
            <span className="text-base font-bold tracking-tight text-white">
              Secure<span className="text-blue-500">Lens</span>
            </span>
          </button>

          {/* Breadcrumb */}
          {view !== "dashboard" && (
            <p className="text-xs text-slate-500 hidden sm:block">
              {view === "progress" ? `Scanning #${scanId}` : `Report #${scanResult?.id}`}
            </p>
          )}

          <div className="text-[10px] text-slate-600 font-mono hidden sm:block">
            v1.0
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="relative z-10 max-w-7xl mx-auto px-5 sm:px-8 py-10">
        <AnimatePresence mode="wait">
          {view === "dashboard" && (
            <Dashboard key="dashboard" onScanStart={handleScanStart} />
          )}
          {view === "progress" && (
            <ScanProgress
              key="progress"
              scanId={scanId}
              onScanComplete={handleScanComplete}
              onBack={goHome}
            />
          )}
          {view === "report" && (
            <SecurityReport key="report" scanData={scanResult} onBack={goHome} />
          )}
        </AnimatePresence>

        {/* History — only on dashboard */}
        {view === "dashboard" && (
          <div className="mt-20 pt-12 border-t border-slate-800/50">
            <History onViewReport={handleViewReport} />
          </div>
        )}
      </main>
    </div>
  );
}
