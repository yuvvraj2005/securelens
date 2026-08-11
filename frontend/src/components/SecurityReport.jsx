import { motion } from "framer-motion";
import {
  ArrowLeft, Download, Clock, Hash,
  Lock, Server, Network, AlertTriangle,
  ShieldCheck, ShieldAlert, Activity, Bug, Globe
} from "lucide-react";
import {
  RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer
} from "recharts";
import { api } from "../services/api";
import SectionCard from "./ui/SectionCard";
import { gradeBadge, riskBadge, severityBadge, severityBar, scoreColor, gradeColor } from "../utils/colors";

/* ─── Helpers ─────────────────────────────────────────── */

function InfoRow({ label, value }) {
  return (
    <div>
      <p className="text-[11px] text-slate-500 uppercase tracking-widest font-semibold mb-1">{label}</p>
      <p className="text-slate-200 text-sm break-all">{value || <span className="italic text-slate-600">Unknown</span>}</p>
    </div>
  );
}

function MonoRow({ label, value }) {
  return (
    <div>
      <p className="text-[11px] text-slate-500 uppercase tracking-widest font-semibold mb-1">{label}</p>
      <p className="font-mono text-sm bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200">
        {value || <span className="italic text-slate-600">Not detected</span>}
      </p>
    </div>
  );
}

function EmptyState({ icon: Icon, message }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center text-slate-500">
      <Icon className="w-8 h-8 mb-3 opacity-40" />
      <p className="text-sm">{message}</p>
    </div>
  );
}

function CountBadge({ count }) {
  return (
    <span className="text-xs bg-slate-800 border border-slate-700 text-slate-400 px-2.5 py-0.5 rounded-full font-mono">
      {count}
    </span>
  );
}

/* ─── Score Gauge ───────────────────────────────────────── */

function ScoreGauge({ score, grade }) {
  const color = scoreColor(score);
  const data = [{ value: score, fill: color }];

  return (
    <div className="relative w-40 h-40 mx-auto">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          innerRadius="72%"
          outerRadius="100%"
          startAngle={210}
          endAngle={-30}
          data={data}
          barSize={10}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            background={{ fill: "#1e293b" }}
            dataKey="value"
            angleAxisId={0}
            cornerRadius={6}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      {/* Centre labels */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-black text-white leading-none">{score}</span>
        <span className={`text-lg font-bold mt-0.5 ${gradeColor(grade)}`}>{grade}</span>
      </div>
    </div>
  );
}

/* ─── Section: Header Findings ──────────────────────────── */

function FindingsSection({ findings }) {
  if (!findings?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center bg-emerald-500/5 rounded-xl border border-emerald-500/10">
        <ShieldCheck className="w-10 h-10 text-emerald-400 mb-3" />
        <p className="text-emerald-400 font-medium">No header findings</p>
        <p className="text-slate-500 text-xs mt-1">Headers look well-configured.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {findings.map((f, i) => (
        <div
          key={i}
          className="relative bg-slate-950/80 rounded-xl border border-slate-800 pl-1 overflow-hidden hover:border-slate-700 transition-colors"
        >
          <div className={`absolute top-0 left-0 w-1 h-full rounded-full ${severityBar(f.severity)}`} />
          <div className="px-4 py-4">
            <div className="flex items-start justify-between gap-4 mb-1.5">
              <h4 className="text-slate-200 font-semibold text-sm">{f.title || f.header}</h4>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold border flex-shrink-0 ${severityBadge(f.severity)}`}>
                {f.severity}
              </span>
            </div>
            {f.description && (
              <p className="text-slate-500 text-xs leading-relaxed">{f.description}</p>
            )}
            {f.recommendation && (
              <p className="text-sky-500/80 text-xs mt-1.5 leading-relaxed">
                <span className="font-semibold text-sky-500">Fix: </span>{f.recommendation}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Section: Open Ports ───────────────────────────────── */

function PortsSection({ nmap }) {
  const ports = nmap?.open_ports ?? [];
  const nmapError = nmap?.error || nmap?.timeout;

  if (nmapError) {
    return (
      <div className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/15 rounded-xl p-4 text-sm text-yellow-400">
        <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
        {typeof nmapError === "string" ? nmapError : "Nmap scan encountered an error or timed out."}
      </div>
    );
  }
  if (!ports.length) return <EmptyState icon={Network} message="No open ports detected." />;

  return (
    <div className="space-y-2">
      {ports.map((p, i) => (
        <div key={i} className="flex items-center justify-between bg-slate-950/80 px-4 py-3 rounded-xl border border-slate-800/60">
          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-teal-400 text-sm w-14">{p.port}</span>
            <span className="text-slate-300 text-sm font-medium">{p.service}</span>
          </div>
          <span className="text-slate-500 text-xs font-mono">{p.version || "—"}</span>
        </div>
      ))}
    </div>
  );
}

/* ─── Section: Nikto ────────────────────────────────────── */

function NiktoSection({ nikto }) {
  if (!nikto || Object.keys(nikto).length === 0) {
    return <EmptyState icon={Bug} message="Nikto results unavailable." />;
  }

  const error = nikto?.error || nikto?.timeout;
  if (error) {
    return (
      <div className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/15 rounded-xl p-4 text-sm text-yellow-400">
        <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
        {typeof error === "string" ? error : "Nikto scan encountered an error or timed out."}
      </div>
    );
  }

  const findings = nikto?.findings ?? nikto?.vulnerabilities ?? [];
  if (!findings.length) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center bg-emerald-500/5 rounded-xl border border-emerald-500/10">
        <ShieldCheck className="w-10 h-10 text-emerald-400 mb-3" />
        <p className="text-emerald-400 font-medium">No Nikto findings</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {findings.map((item, i) => {
        const msg = typeof item === "string" ? item : (item.description || item.message || JSON.stringify(item));
        return (
          <div key={i} className="flex items-start gap-3 bg-slate-950/80 border border-slate-800/60 rounded-xl px-4 py-3">
            <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
            <p className="text-slate-300 text-xs leading-relaxed">{msg}</p>
          </div>
        );
      })}
    </div>
  );
}

/* ─── Section: Nessus ───────────────────────────────────── */

function NessusSection({ nessus }) {
  if (!nessus || Object.keys(nessus).length === 0) {
    return (
      <div className="flex items-center gap-3 bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3">
        <Activity className="w-4 h-4 text-slate-500" />
        <p className="text-slate-500 text-sm">Nessus integration not configured.</p>
      </div>
    );
  }

  const status = nessus?.status ?? "unknown";
  const statusColor =
    status === "completed" ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" :
    status === "running"   ? "text-blue-400 bg-blue-500/10 border-blue-500/20" :
    status === "failed"    ? "text-red-400 bg-red-500/10 border-red-500/20" :
                             "text-slate-400 bg-slate-500/10 border-slate-500/20";

  const findings = nessus?.findings ?? nessus?.vulnerabilities ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className={`text-xs font-bold px-3 py-1 rounded-full border ${statusColor}`}>
          {status.toUpperCase()}
        </span>
        {nessus?.scan_id && (
          <span className="text-xs text-slate-500 font-mono">Scan #{nessus.scan_id}</span>
        )}
      </div>

      {findings.length > 0 && (
        <div className="space-y-2">
          {findings.map((item, i) => {
            const msg = typeof item === "string" ? item : (item.description || item.plugin_name || JSON.stringify(item));
            const sev = item?.severity ?? item?.risk_factor ?? "Info";
            return (
              <div key={i} className="flex items-start gap-3 bg-slate-950/80 border border-slate-800/60 rounded-xl px-4 py-3">
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold border flex-shrink-0 mt-0.5 ${severityBadge(sev)}`}>
                  {sev}
                </span>
                <p className="text-slate-300 text-xs leading-relaxed">{msg}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ─── Main component ────────────────────────────────────── */

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
};

export default function SecurityReport({ scanData, onBack }) {
  if (!scanData?.report) return null;

  const { id, target, completed_at, report } = scanData;
  const { score: scoreObj, headers, ssl, technology, nmap, nikto, nessus } = report;
  const { overall_score, grade, risk_level } = scoreObj ?? {};

  const handleExport = (fmt) => {
    window.open(api.exportUrl(id, fmt), "_blank");
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="visible"
      className="w-full max-w-6xl mx-auto pb-24"
    >
      {/* ── Top bar ── */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Back to Dashboard
        </button>

        {/* Export buttons */}
        <div className="flex gap-2">
          {["json", "html", "pdf"].map((fmt) => (
            <button
              key={fmt}
              onClick={() => handleExport(fmt)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold border transition-all ${
                fmt === "pdf"
                  ? "bg-blue-600 hover:bg-blue-500 text-white border-blue-500/50 shadow-[0_0_16px_rgba(37,99,235,0.2)]"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700"
              }`}
            >
              <Download className="w-3.5 h-3.5" />
              {fmt.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* ── Hero card ── */}
      <motion.div
        variants={{ hidden: { y: 20, opacity: 0 }, visible: { y: 0, opacity: 1 } }}
        className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 sm:p-8 mb-6 shadow-2xl relative overflow-hidden"
      >
        {/* Watermark */}
        <div className="absolute top-0 right-0 p-6 opacity-[0.03] pointer-events-none select-none">
          <ShieldAlert className="w-64 h-64" />
        </div>

        <div className="flex flex-col sm:flex-row gap-8 items-center sm:items-start relative z-10">
          {/* Score gauge */}
          <div className="flex-shrink-0">
            <ScoreGauge score={overall_score} grade={grade} />
            <div className="mt-3 flex justify-center">
              <span className={`text-xs font-bold px-3 py-1 rounded-full border ${riskBadge(risk_level)}`}>
                {risk_level} Risk
              </span>
            </div>
          </div>

          {/* Meta */}
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 truncate">{target}</h1>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-sm text-slate-400 mb-6">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {completed_at ? new Date(completed_at).toLocaleString() : "—"}
              </span>
              <span className="flex items-center gap-1.5">
                <Hash className="w-3.5 h-3.5" />
                Scan #{id}
              </span>
            </div>

            {/* Score breakdown row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Score</p>
                <p className="text-2xl font-black text-white">{overall_score ?? "—"}<span className="text-slate-500 text-base font-medium">/100</span></p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Grade</p>
                <p className={`text-2xl font-black ${gradeColor(grade)}`}>{grade ?? "—"}</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3 col-span-2 sm:col-span-1">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold mb-1">Header Score</p>
                <p className="text-2xl font-black text-white">{headers?.score ?? "—"}<span className="text-slate-500 text-base font-medium">/100</span></p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ── Grid: SSL + Tech ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        <SectionCard
          icon={Lock}
          iconBg="bg-sky-500/10 text-sky-400"
          title="SSL / TLS Certificate"
        >
          {ssl && Object.keys(ssl).length > 0 ? (
            <div className="space-y-4">
              <InfoRow label="Issuer"           value={ssl.issuer} />
              <InfoRow label="Subject"          value={ssl.subject} />
              <div className="grid grid-cols-2 gap-4">
                <InfoRow label="Expires"        value={ssl.expires_on} />
                <InfoRow label="Days remaining" value={ssl.days_remaining != null ? `${ssl.days_remaining} days` : null} />
              </div>
              {ssl.protocol && <InfoRow label="Protocol" value={ssl.protocol} />}
            </div>
          ) : (
            <EmptyState icon={Lock} message="SSL information unavailable." />
          )}
        </SectionCard>

        <SectionCard
          icon={Server}
          iconBg="bg-violet-500/10 text-violet-400"
          title="Technology Stack"
        >
          {technology && Object.keys(technology).length > 0 ? (
            <div className="space-y-3">
              <MonoRow label="Web Server"         value={technology.server} />
              <MonoRow label="Framework / CMS"    value={technology.framework} />
              <MonoRow label="CDN / WAF"          value={technology.cdn} />
              {technology.language && <MonoRow label="Language" value={technology.language} />}
            </div>
          ) : (
            <EmptyState icon={Globe} message="Technology fingerprinting returned no data." />
          )}
        </SectionCard>
      </div>

      {/* ── Security Findings (full width) ── */}
      <SectionCard
        icon={AlertTriangle}
        iconBg="bg-orange-500/10 text-orange-400"
        title="Header Security Findings"
        badge={<CountBadge count={headers?.findings?.length ?? 0} />}
        className="mb-5"
      >
        <FindingsSection findings={headers?.findings} />
      </SectionCard>

      {/* ── Grid: Ports + Nikto ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <SectionCard
          icon={Network}
          iconBg="bg-teal-500/10 text-teal-400"
          title="Open Ports (Nmap)"
          badge={<CountBadge count={nmap?.open_ports?.length ?? 0} />}
        >
          <PortsSection nmap={nmap} />
        </SectionCard>

        <SectionCard
          icon={Bug}
          iconBg="bg-orange-500/10 text-orange-400"
          title="Web Vulnerabilities (Nikto)"
          badge={<CountBadge count={(nikto?.findings ?? nikto?.vulnerabilities ?? []).length} />}
        >
          <NiktoSection nikto={nikto} />
        </SectionCard>
      </div>

      {/* ── Nessus ── */}
      <SectionCard
        icon={Activity}
        iconBg="bg-blue-500/10 text-blue-400"
        title="Nessus Vulnerability Assessment"
      >
        <NessusSection nessus={nessus} />
      </SectionCard>
    </motion.div>
  );
}
