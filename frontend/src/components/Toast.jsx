import { useEffect } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'

const TYPES = {
  success: { bg: 'bg-emerald-50 border-emerald-200', text: 'text-emerald-800', icon: CheckCircle2, iconColor: 'text-emerald-500' },
  error: { bg: 'bg-red-50 border-red-200', text: 'text-red-800', icon: AlertCircle, iconColor: 'text-red-500' },
  info: { bg: 'bg-blue-50 border-blue-200', text: 'text-blue-800', icon: Info, iconColor: 'text-blue-500' },
  warning: { bg: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-800', icon: AlertCircle, iconColor: 'text-yellow-500' },
}

export default function Toast({ type = 'info', message, onClose, duration = 4000 }) {
  useEffect(() => {
    if (!duration || !onClose) return
    const t = setTimeout(onClose, duration)
    return () => clearTimeout(t)
  }, [duration, onClose])
  const cfg = TYPES[type] || TYPES.info
  const Icon = cfg.icon
  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg ${cfg.bg} ${cfg.text} animate-[fadeIn_.2s_ease-out]`}>
      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${cfg.iconColor}`} />
      <p className="text-sm font-medium flex-1">{message}</p>
      {onClose && (
        <button onClick={onClose} className="p-0.5 rounded hover:bg-white/40 transition">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

export function ToastContainer({ toasts }) {
  if (!toasts?.length) return null
  return (
    <div className="fixed top-4 right-4 z-[100] space-y-2 w-96 max-w-[90vw]">
      {toasts.map(t => <Toast key={t.id} {...t} />)}
    </div>
  )
}

export function useToasts() {
  const push = (toasts, setToasts, type, message) => {
    const id = Date.now() + Math.random()
    const onClose = () => setToasts(prev => prev.filter(t => t.id !== id))
    setToasts(prev => [...prev, { id, type, message, onClose }])
  }
  return { push }
}
