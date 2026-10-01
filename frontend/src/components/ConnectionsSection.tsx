import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  connectionsApi,
  type MaterialConnectionsResponse,
} from '../api/client'
import { Alert } from './Alert'
import { IconConnections, IconLink, IconPlus, IconTrash } from './Icons'

interface ConnectionsSectionProps {
  materialId: number
}

const RELATION_LABELS: Record<string, { label: string; badgeClass: string; desc: string }> = {
  prerequisite: {
    label: 'Pré-requisito',
    badgeClass: 'badge-warn',
    desc: 'Fundamento ou base necessária para entender este material',
  },
  deepening: {
    label: 'Aprofundamento',
    badgeClass: 'badge-indigo',
    desc: 'Tópico avançado ou desdobramento detalhado',
  },
  related: {
    label: 'Correlato',
    badgeClass: 'badge-subtle',
    desc: 'Conteúdo conceitualmente análogo ou interdisciplinar',
  },
  application: {
    label: 'Aplicação',
    badgeClass: 'badge-green',
    desc: 'Estudo de caso ou aplicação prática no mundo real',
  },
}

export function ConnectionsSection({ materialId }: ConnectionsSectionProps) {
  const [data, setData] = useState<MaterialConnectionsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Formulário de nova conexão
  const [showForm, setShowForm] = useState(false)
  const [targetId, setTargetId] = useState<number | ''>('')
  const [relType, setRelType] = useState('prerequisite')
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)

  async function load() {
    try {
      const res = await connectionsApi.get(materialId)
      setData(res)
      if (res.available_targets.length > 0 && targetId === '') {
        setTargetId(res.available_targets[0].id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar conexões.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [materialId])

  async function handleAdd(e: FormEvent) {
    e.preventDefault()
    if (!targetId) return
    setSaving(true)
    setError(null)
    try {
      await connectionsApi.create(materialId, Number(targetId), relType, note)
      setShowForm(false)
      setNote('')
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível criar a conexão.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(connId: number) {
    if (!confirm('Desconectar este material?')) return
    try {
      await connectionsApi.remove(connId)
      await load()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erro ao remover conexão.')
    }
  }

  const hasOutgoing = Boolean(data && data.outgoing.length > 0)
  const hasIncoming = Boolean(data && data.incoming.length > 0)
  const totalConns = (data?.outgoing.length || 0) + (data?.incoming.length || 0)

  return (
    <div className="connections-section">
      <div className="section-header-row">
        <div>
          <h2>Conexões e Grafo de Conhecimento</h2>
          <p className="muted">
            Vincule materiais associativamente no estilo Obsidian (pré-requisitos, aprofundamentos e referências).
          </p>
        </div>

        {data && data.available_targets.length > 0 && !showForm && (
          <button className="btn btn-outline" onClick={() => setShowForm(true)}>
            <IconPlus size={15} /> Nova conexão
          </button>
        )}
      </div>

      {error && <Alert>{error}</Alert>}

      {/* Formulário de Criação de Conexão */}
      {showForm && data && (
        <form className="card manual-card-form" onSubmit={handleAdd}>
          <div className="row" style={{ gap: '0.5rem', alignItems: 'center' }}>
            <IconConnections size={18} color="var(--primary)" />
            <h3 style={{ margin: 0 }}>Vincular outro material</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <label>
              Material a conectar
              <select
                value={targetId}
                onChange={(e) => setTargetId(Number(e.target.value))}
                required
                className="select-input"
              >
                {data.available_targets.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title} ({t.filename})
                  </option>
                ))}
              </select>
            </label>

            <label>
              Tipo de relação
              <select
                value={relType}
                onChange={(e) => setRelType(e.target.value)}
                className="select-input"
              >
                <option value="prerequisite">Pré-requisito (base necessária)</option>
                <option value="deepening">Aprofundamento (conteúdo avançado)</option>
                <option value="related">Conteúdo correlato / análogo</option>
                <option value="application">Aplicação prática / estudo de caso</option>
              </select>
            </label>
          </div>

          <label>
            Nota de conexão (opcional)
            <input
              type="text"
              placeholder="Ex.: Necessário dominar a camada de transporte antes deste tópico de criptografia"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </label>

          <div className="row-end" style={{ gap: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowForm(false)}
              disabled={saving}
            >
              Cancelar
            </button>
            <button className="btn btn-primary btn-sm" disabled={saving}>
              {saving ? 'Conectando…' : 'Salvar conexão'}
            </button>
          </div>
        </form>
      )}

      {loading && <p className="muted">Carregando conexões…</p>}

      {!loading && totalConns === 0 && !showForm && (
        <div className="empty-flashcards card">
          <p>Nenhuma conexão registrada para este material ainda.</p>
          <p className="muted" style={{ marginBottom: '1.25rem' }}>
            {data && data.available_targets.length > 0
              ? 'Conecte este estudo a outros PDFs da sua conta para criar um mapa de aprendizagem contínuo.'
              : 'Envie outros PDFs na aba inicial para poder criar conexões entre eles.'}
          </p>
          {data && data.available_targets.length > 0 && (
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              <IconPlus size={15} /> Conectar ao primeiro material
            </button>
          )}
        </div>
      )}

      {/* Conexões de Saída (Materiais que este material aponta) */}
      {hasOutgoing && (
        <div className="connections-group">
          <h3 className="connections-subtitle">
            <IconLink size={15} /> Materiais vinculados a partir deste
          </h3>
          <div className="connections-grid">
            {data!.outgoing.map((c) => {
              const meta = RELATION_LABELS[c.relation_type] || RELATION_LABELS.related
              return (
                <div key={c.id} className="card connection-item">
                  <div className="connection-item-header">
                    <span className={`badge ${meta.badgeClass}`}>{meta.label}</span>
                    <button
                      className="icon-btn-delete"
                      onClick={() => handleDelete(c.id)}
                      title="Remover conexão"
                    >
                      <IconTrash size={14} />
                    </button>
                  </div>

                  <Link to={`/materiais/${c.target_material_id}`} className="connection-title">
                    {c.target_material_title}
                  </Link>

                  {c.note && <p className="connection-note muted">{c.note}</p>}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Backlinks (Materiais que apontam para este) */}
      {hasIncoming && (
        <div className="connections-group">
          <h3 className="connections-subtitle">
            <IconConnections size={15} /> Backlinks (Materiais que referenciam este)
          </h3>
          <div className="connections-grid">
            {data!.incoming.map((b) => {
              const meta = RELATION_LABELS[b.relation_type] || RELATION_LABELS.related
              return (
                <div key={b.id} className="card connection-item backlink-item">
                  <div className="connection-item-header">
                    <span className={`badge ${meta.badgeClass}`}>{meta.label}</span>
                  </div>

                  <Link to={`/materiais/${b.source_material_id}`} className="connection-title">
                    {b.source_material_title}
                  </Link>

                  {b.note && <p className="connection-note muted">{b.note}</p>}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
