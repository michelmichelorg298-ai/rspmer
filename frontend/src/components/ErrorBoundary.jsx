import React from 'react'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled React Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-xl max-w-lg w-full text-center space-y-4">
            <div className="w-12 h-12 bg-red-100 text-red-600 rounded-xl flex items-center justify-center mx-auto text-xl font-bold">
              ⚠️
            </div>
            <h2 className="text-xl font-bold text-slate-800">Une erreur inattendue est survenue</h2>
            <p className="text-sm text-slate-500 font-mono bg-slate-100 p-3 rounded-lg text-left overflow-auto max-h-32">
              {this.state.error?.toString() || 'Erreur inconnue'}
            </p>
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null })
                  window.location.href = '/login'
                }}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl text-sm transition shadow"
              >
                Retour à la connexion
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-xl text-sm transition"
              >
                Recharger la page
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
