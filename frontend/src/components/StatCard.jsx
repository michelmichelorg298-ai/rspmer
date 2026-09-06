export default function StatCard({ title, value, icon: Icon, trend, color = 'emerald', subtitle }) {
  const colors = {
    emerald: 'from-emerald-400 to-emerald-600 bg-emerald-100 text-emerald-600',
    blue: 'from-blue-400 to-blue-600 bg-blue-100 text-blue-600',
    orange: 'from-orange-400 to-orange-600 bg-orange-100 text-orange-600',
    purple: 'from-purple-400 to-purple-600 bg-purple-100 text-purple-600',
    rose: 'from-rose-400 to-rose-600 bg-rose-100 text-rose-600',
    red: 'from-red-400 to-red-600 bg-red-100 text-red-600',
  }
  const colorStr = colors[color] || colors.emerald
  const [gradFrom, gradTo, bgIcon, textIcon] = colorStr.split(' ')

  return (
    <div className="card p-5 relative overflow-hidden">
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full bg-gradient-to-br ${gradFrom} ${gradTo} opacity-10`} />
      <div className="flex items-start justify-between relative">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
          {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
          {trend && (
            <div className={`mt-2 text-xs font-medium flex items-center gap-1 ${trend > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              <span>{trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%</span>
              <span className="text-slate-400 font-normal">vs dernier mois</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`w-11 h-11 rounded-xl ${bgIcon} flex items-center justify-center shadow-sm`}>
            <Icon className={`w-5 h-5 ${textIcon}`} />
          </div>
        )}
      </div>
    </div>
  )
}
