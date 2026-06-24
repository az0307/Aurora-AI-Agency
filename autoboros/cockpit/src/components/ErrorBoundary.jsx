import { Component } from 'react'

// B4.6 — global error boundary. A thrown hook (e.g. missing provider) now
// degrades to a readable panel instead of a white screen of death.
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          minHeight: '100vh', display: 'flex', alignItems: 'center',
          justifyContent: 'center', background: '#0b0d10', color: '#e6e6e6',
          fontFamily: 'system-ui, sans-serif', padding: 24,
        }}>
          <div style={{ maxWidth: 560 }}>
            <h1 style={{ fontSize: 20, marginBottom: 8 }}>Something broke.</h1>
            <p style={{ opacity: 0.7, marginBottom: 16 }}>
              The cockpit hit an unrecoverable error. Details are in the console.
            </p>
            <pre style={{
              background: '#15181d', padding: 12, borderRadius: 8,
              overflow: 'auto', fontSize: 12, color: '#ff8585',
            }}>{String(this.state.error?.message || this.state.error)}</pre>
            <button onClick={() => location.reload()} style={{
              marginTop: 16, padding: '8px 16px', borderRadius: 8,
              border: '1px solid #333', background: '#1f2329', color: '#e6e6e6',
              cursor: 'pointer',
            }}>Reload</button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
