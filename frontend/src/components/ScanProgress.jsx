import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Server, Shield, Globe, AlertTriangle, ArrowLeft } from "lucide-react";
import { api } from "../services/api";

const POLL_INTERVAL_MS = 3000;
const TIMEOUT_MS = 10 * 60 * 1000; // 10-minute hard timeout

const STEPS = [
  { icon: Globe,    label: "Resolving target & checking headers",         phase: "pending"  },
  { icon: Shield,   label: "SSL/TLS certificate inspection",              phase: "pending"  },
  { icon: Server,   label: "Technology fingerprinting",                   phase: "running"  },
  { icon: Activity, label: "Nmap port scan (may take 2–4 min)",           phase: "running"  },
  { icon: Activity, label: "Nikto vulnerability scan (may take 3–5 min)", phase: "running"  },
];

function StepRow({ icon: Icon, label, active, done }) {
  return (
    <div className={`flex items-center gap-3 py-2.5 px-3 rounded-lg transition-colors ${active ? "bg-blue-500/8" : ""}`}>
      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${done ? "bg-emerald-400" : active ? "bg-blue-400 animate-pulse" : "bg-slate-700"}`} />
      <Icon className={`w-4 h-4 flex-shrink-0 ${done ? "text-emerald-400" : active ? "text-blue-400" : "text-slate-600"}`} />
      <span className={`text-sm flex-1 ${done ? "text-slate-400 line-through" : active ? "text-slate-200" : "text-slate-600"}`}>
        {label}
      </span>
      {active && (
        <span className="text-[10px] font-bold uppercase tracking-widest text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full">
          Active
        </span>
      )}
      {done && (
        <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400">Done</span>
      )}
    </div>
  );
}

export default function ScanProgress({ scanId, onScanComplete, onBack }) {
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef(Date.now());
  const timeoutRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    // Elapsed-seconds ticker
    timerRef.current = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
    }, 1000);

    // Hard timeout
    timeoutRef.current = setTimeout(() => {
      if (!isMounted) return;
      setStatus("timeout");
      setError("Scan timed out after 10 minutes. Nmap or Nikto may be unreachable on this target.");
    }, TIMEOUT_MS);

    // Recursive poll
    let pollTimer;
    const poll = async () => {
      try {
        const data = await api.getScanStatus(scanId);
        if (!isMounted) return;

        if (data.status === "completed") {
          clearTimeout(timeoutRef.current);
          clearInterval(timerRef.current);
          onScanComplete(data);
          return;
        }
        if (data.status === "failed") {
          clearTimeout(timeoutRef.current);
          clearInterval(timerRef.current);
          setStatus("failed");
          setError("The scan failed on the server. Please try again.");
          return;
        }
        setStatus(data.status); // pending | running
        pollTimer = setTimeout(poll, POLL_INTERVAL_MS);
      } catch (err) {
        if (!isMounted) return;
        clearTimeout(timeoutRef.current);
        clearInterval(timerRef.current);
        setStatus("error");
        setError(err.message || "Cannot reach backend. Please check that the server is running.");
      }
    };

    poll();

    return () => {
      isMounted = false;
      clearTimeout(pollTimer);
      clearTimeout(timeoutRef.current);
      clearInterval(timerRef.current);
    };
  }, [scanId, onScanComplete]);

  const isError = ["error", "failed", "timeout"].includes(status);

  const pendingDone = status !== "pending";
  const runningDone = false; // steps never "done" until completed

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  return (
    <motion.div
      key="progress"
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center min-h-[60vh] w-full max-w-xl mx-auto"
    >
      <div className="w-full bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">

        {isError ? (
          /* ─── Error state ─── */
          <div className="p-10 flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-6">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">
              {status === "timeout" ? "Scan Timed Out" : "Scan Failed"}
            </h2>
            <p className="text-slate-400 text-sm max-w-xs leading-relaxed mb-8">{error}</p>
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-colors text-sm"
            >
              <ArrowLeft className="w-4 h-4" /> Back to Dashboard
            </button>
          </div>
        ) : (
          /* ─── Progress state ─── */
          <>
            {/* Top bar */}
            <div className="bg-slate-950/60 px-6 py-5 flex items-center justify-between border-b border-slate-800">
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-0.5">Scan in progress</p>
                <p className="text-white font-mono text-sm">
                  ID <span className="text-blue-400">#{scanId}</span>
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mb-0.5">Elapsed</p>
                <p className="font-mono text-slate-300">{fmt(elapsed)}</p>
              </div>
            </div>

            {/* Spinner */}
            <div className="flex justify-center py-10 relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-28 h-28 rounded-full bg-blue-500/10 blur-2xl" />
              </div>
              <div className="relative w-20 h-20">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 rounded-full border-[2px] border-transparent border-t-blue-500 border-r-blue-500/40"
                />
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-3 rounded-full border-[2px] border-transparent border-b-slate-600 border-l-slate-600/40"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Activity className="w-7 h-7 text-blue-400" strokeWidth={1.5} />
                </div>
              </div>
            </div>

            {/* Status label */}
            <p className="text-center text-slate-300 font-medium mb-6 px-4">
              {status === "pending" ? "Initializing scan engine…" : "Running security checks…"}
            </p>

            {/* Steps */}
            <div className="px-5 pb-6 space-y-1">
              {STEPS.map((step, i) => (
                <StepRow
                  key={i}
                  icon={step.icon}
                  label={step.label}
                  done={step.phase === "pending" && pendingDone}
                  active={
                    step.phase === "pending"
                      ? status === "pending"
                      : status === "running"
                  }
                />
              ))}
            </div>

            {/* Footer note */}
            <div className="border-t border-slate-800 px-6 py-4 bg-slate-950/30">
              <p className="text-xs text-slate-500 text-center">
                Nmap & Nikto scans can take <strong className="text-slate-400">3–8 minutes</strong> depending on the target. Please don&apos;t close this tab.
              </p>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
}
