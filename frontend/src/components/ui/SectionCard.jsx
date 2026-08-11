import { motion } from "framer-motion";

/** A uniform animated card used throughout the report. */
export default function SectionCard({ icon: Icon, iconBg, title, badge, children, className = "" }) {
  return (
    <motion.div
      variants={{ hidden: { y: 20, opacity: 0 }, visible: { y: 0, opacity: 1 } }}
      className={`bg-slate-900/60 border border-slate-800/80 rounded-2xl shadow-lg flex flex-col ${className}`}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800/80">
        <div className={`p-2 rounded-lg ${iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
        <h2 className="text-base font-semibold text-slate-100 tracking-tight flex-1">{title}</h2>
        {badge}
      </div>

      {/* Body */}
      <div className="p-6 flex-1">{children}</div>
    </motion.div>
  );
}
