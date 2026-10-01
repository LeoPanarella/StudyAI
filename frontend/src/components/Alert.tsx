export function Alert({ kind = 'error', children }: { kind?: 'error' | 'warning' | 'info'; children: React.ReactNode }) {
  return (
    <div className={`alert alert-${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  )
}
