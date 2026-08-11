import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, ExternalLink, RefreshCw, AlertCircle, ShieldOff } from "lucide-react";
import { api } from "../services/api";
import { gradeBadge, riskBadge } from "../utils/colors";

const STATUS_LABEL = {
  completed: { text: "Completed", cls: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
  running:   { text: "Running",   cls: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
  pending:   { text: "Pending",   cls: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20" },
  failed:    { text: "Failed",    cls: "text-red-400 bg-red-500/10 border-red-500/20" },
};

function StatusPill({ status }) {
  const cfg = STATUS_LABEL[status] ?? { text: status, cls: "text-slate-400 bg-slate-700 border-slate-600" };
  return (
    <span className={`text-[10px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full border ${cfg.cls}`}>
      {cfg.text}
    </span>
  );
}

export default function History({ onViewReport }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingId, setLoadingId] = useState(null);
  const isMounted = useRef(true);

  const fetchScans = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getScans();
      if (isMounted.current) {
        // Newest first
        setScans([...data].sort((a, b) => b.id - a.id));
      }
    } catch (err) {
      if (isMounted.current) setError(err.message || "Failed to load scan history.");
    } finally {
      if (isMounted.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    fetchScans();
    return () => { isMounted.current = false; };
  }, [fetchScans]);

  const handleRowClick = async (scan) => {
    if (scan.status !== "completed") return;
    setLoadingId(scan.id);
    try {
      const data = await api.getScanStatus(scan.id);
      onViewReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto pb-16">
      {/* Section header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2.5">
          <Clock className="w-5 h-5 text-slate-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">Recent Scans</h2>
          {!loading && !error && (
            <span className="text-xs text-slate-500 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-full font-mono">
              {scans.length}
            </span>
          )}
        </div>
        <button
          onClick={fetchScans}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex items-center justify-center gap-3 py-16 text-slate-500"
            >
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span className="text-sm">Loading scan history…</span>
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16 gap-3 text-slate-500"
            >
              <AlertCircle className="w-8 h-8 text-red-400/50" />
              <p className="text-sm text-red-400">{error}</p>
              <button onClick={fetchScans} className="text-xs text-slate-400 hover:text-white underline transition-colors">
                Try again
              </button>
            </motion.div>
          ) : scans.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16 gap-3 text-slate-500"
            >
              <ShieldOff className="w-10 h-10 opacity-30" />
              <p className="text-sm">No scans yet. Run your first scan above.</p>
            </motion.div>
          ) : (
            <motion.div key="table" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-950/50 border-b border-slate-800 text-[11px] uppercase tracking-widest text-slate-500">
                    <th className="px-5 py-3.5 font-semibold">Target</th>
                    <th className="px-5 py-3.5 font-semibold text-center">Status</th>
                    <th className="px-5 py-3.5 font-semibold text-center">Score</th>
                    <th className="px-5 py-3.5 font-semibold text-center">Grade</th>
                    <th className="px-5 py-3.5 font-semibold text-center">Risk</th>
                    <th className="px-5 py-3.5 font-semibold">Scanned</th>
                    <th className="px-5 py-3.5 font-semibold text-right" />
                  </tr>
                </thead>
                <tbody>
                  {scans.map((scan) => {
                    const clickable = scan.status === "completed";
                    const busy = loadingId === scan.id;
                    return (
                      <tr
                        key={scan.id}
                        onClick={() => clickable && handleRowClick(scan)}
                        className={`border-b border-slate-800/40 transition-colors ${
                          clickable
                            ? "cursor-pointer hover:bg-slate-800/40 group"
                            : "opacity-55"
                        }`}
                      >
                        <td className="px-5 py-4">
                          <p className="text-slate-200 font-medium text-sm truncate max-w-[240px]">{scan.target}</p>
                          <p className="text-slate-600 text-xs font-mono mt-0.5">#{scan.id}</p>
                        </td>
                        <td className="px-5 py-4 text-center">
                          <StatusPill status={scan.status} />
                        </td>
                        <td className="px-5 py-4 text-center font-bold text-white font-mono">
                          {scan.score ?? "—"}
                        </td>
                        <td className="px-5 py-4 text-center">
                          {scan.grade ? (
                            <span className={`text-xs px-2.5 py-0.5 rounded font-bold border ${gradeBadge(scan.grade)}`}>
                              {scan.grade}
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-5 py-4 text-center">
                          {scan.risk_level ? (
                            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${riskBadge(scan.risk_level)}`}>
                              {scan.risk_level}
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-5 py-4 text-slate-500 text-xs">
                          {scan.created_at
                            ? new Date(scan.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
                            : "—"
                          }
                        </td>
                        <td className="px-5 py-4 text-right">
                          {clickable && (
                            busy
                              ? <RefreshCw className="w-4 h-4 text-slate-400 animate-spin inline" />
                              : <ExternalLink className="w-4 h-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity inline" />
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
