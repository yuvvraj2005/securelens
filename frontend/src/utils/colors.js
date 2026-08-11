/** Grade A→F colour tokens */
export function gradeColor(grade) {
  switch (grade) {
    case "A": return "text-emerald-400";
    case "B": return "text-sky-400";
    case "C": return "text-yellow-400";
    case "D": return "text-orange-400";
    default:  return "text-red-400";
  }
}

/** Grade A→F badge (bg + border + text) */
export function gradeBadge(grade) {
  switch (grade) {
    case "A": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/25";
    case "B": return "text-sky-400 bg-sky-500/10 border-sky-500/25";
    case "C": return "text-yellow-400 bg-yellow-500/10 border-yellow-500/25";
    case "D": return "text-orange-400 bg-orange-500/10 border-orange-500/25";
    default:  return "text-red-400 bg-red-500/10 border-red-500/25";
  }
}

/** Risk label colour */
export function riskBadge(risk) {
  switch (risk) {
    case "Low":      return "text-emerald-400 bg-emerald-500/10 border-emerald-500/25";
    case "Medium":   return "text-yellow-400 bg-yellow-500/10 border-yellow-500/25";
    case "High":     return "text-orange-400 bg-orange-500/10 border-orange-500/25";
    case "Critical": return "text-red-400 bg-red-500/10 border-red-500/25";
    default:         return "text-slate-400 bg-slate-500/10 border-slate-500/25";
  }
}

/** Finding severity badge */
export function severityBadge(sev) {
  switch (sev) {
    case "Critical": return "text-red-400 bg-red-500/10 border-red-500/25";
    case "High":     return "text-orange-400 bg-orange-500/10 border-orange-500/25";
    case "Medium":   return "text-yellow-400 bg-yellow-500/10 border-yellow-500/25";
    case "Low":      return "text-sky-400 bg-sky-500/10 border-sky-500/25";
    case "Info":     return "text-slate-400 bg-slate-500/10 border-slate-500/25";
    default:         return "text-slate-400 bg-slate-500/10 border-slate-500/25";
  }
}

/** Finding severity left-bar colour */
export function severityBar(sev) {
  switch (sev) {
    case "Critical": return "bg-red-500";
    case "High":     return "bg-orange-500";
    case "Medium":   return "bg-yellow-500";
    case "Low":      return "bg-sky-500";
    default:         return "bg-slate-500";
  }
}

/** Score → colour */
export function scoreColor(score) {
  if (score >= 80) return "#34d399"; // emerald
  if (score >= 60) return "#facc15"; // yellow
  if (score >= 40) return "#fb923c"; // orange
  return "#f87171";                  // red
}
