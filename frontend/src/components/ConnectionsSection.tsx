import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  connectionsApi,
  type GlobalGraphResponse,
  type MaterialConnectionsResponse,
} from '../api/client'
import { Alert } from './Alert'
import { GraphCanvas, type GraphEdgeData, type GraphNodeData } from './GraphCanvas'
import { IconConnections, IconLink, IconPlus, IconTrash } from './Icons'

interface ConnectionsSectionProps {
  materialId: number
  materialTitle?: string
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

export function ConnectionsSection({ materialId, materialTitle = 'Material Atual' }: ConnectionsSectionProps) {
  const [data, setData] = useState<MaterialConnectionsResponse | null>(null)
  const [globalGraph, setGlobalGraph] = useState<GlobalGraphResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isGlobalView, setIsGlobalView] = useState(false)
  const [viewMode, setViewMode] = useState<'graph' | 'list'>('graph')

  // Formulário de nova conexão
  const [showForm, setShowForm] = useState(false)
  const [targetId, setTargetId] = useState<number | ''>('')
  const [relType, setRelType] = useState('prerequisite')
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)

  async function load() {
    try {
      const [res, graphRes] = await Promise.all([
        connectionsApi.get(materialId),
        connectionsApi.getGraph().catch(() => null),
      ])
      setData(res)
      if (graphRes) setGlobalGraph(graphRes)

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

  // Prepara os dados para o Grafo Visual
  let graphNodes: GraphNodeData[] = []
  let graphEdges: GraphEdgeData[] = []

  if (isGlobalView && globalGraph) {
    // Modo Global: Todos os materiais e todas as conexões
    graphNodes = globalGraph.nodes.map((n) => ({
      id: n.id,
      title: n.title,
      filename: n.filename,
      charCount: n.char_count,
      flashcardCount: n.flashcard_count,
      hasSummary: n.has_summary,
      isCenter: n.id === materialId,
    }))

    graphEdges = globalGraph.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      relationType: e.relation_type,
      note: e.note,
    }))
  } else if (data) {
    // Modo Local: Este material no centro + seus vínculos e materiais do acervo
    const nodeMap = new Map<number, GraphNodeData>()

    // Nó central
    nodeMap.set(materialId, {
      id: materialId,
      title: materialTitle,
      isCenter: true,
    })

    // Conexões de saída
    data.outgoing.forEach((c) => {
      nodeMap.set(c.target_material_id, {
        id: c.target_material_id,
        title: c.target_material_title,
        filename: c.target_material_filename,
        relationType: c.relation_type,
        note: c.note,
      })
      graphEdges.push({
        id: c.id,
        source: materialId,
        target: c.target_material_id,
        relationType: c.relation_type,
        note: c.note,
      })
    })

    // Backlinks (Conexões de entrada)
    data.incoming.forEach((b) => {
      nodeMap.set(b.source_material_id, {
        id: b.source_material_id,
        title: b.source_material_title,
        filename: b.source_material_filename,
        relationType: b.relation_type,
        note: b.note,
        isBacklink: true,
      })
      graphEdges.push({
        id: b.id,
        source: b.source_material_id,
        target: materialId,
        relationType: b.relation_type,
        note: b.note,
      })
    })

    // Outros materiais disponíveis no acervo como satélites
    data.available_targets.forEach((t) => {
      if (!nodeMap.has(t.id)) {
        nodeMap.set(t.id, {
          id: t.id,
          title: t.title,
          filename: t.filename,
        })
      }
    })

    graphNodes = Array.from(nodeMap.values())
  }

  const hasOutgoing = Boolean(data && data.outgoing.length > 0)
  const hasIncoming = Boolean(data && data.incoming.length > 0)
  const totalConns = (data?.outgoing.length || 0) + (data?.incoming.length || 0)

  return (
    <div className="connections-section">
      {/* Cabeçalho da Seção */}
      <div className="section-header-row" style={{ marginBottom: '1.2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <IconConnections size={22} color="var(--primary)" />
            <h2 style={{ margin: 0 }}>Grafo de Conhecimento e Conexões</h2>
          </div>
          <p className="muted" style={{ margin: '4px 0 0 0', fontSize: '0.9rem' }}>
            Mapa visual associativo estilo Obsidian: explore correlações, pré-requisitos e desdobramentos dos seus estudos.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Seletor de visualização (Grafo vs Lista) */}
          <div className="view-mode-toggle" style={{ display: 'flex', background: 'var(--surface-muted)', borderRadius: '8px', padding: '3px', border: '1px solid var(--border)' }}>
            <button
              type="button"
              onClick={() => setViewMode('graph')}
              style={{
                background: viewMode === 'graph' ? 'var(--surface)' : 'transparent',
                color: viewMode === 'graph' ? 'var(--text)' : 'var(--text-muted)',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 12px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: viewMode === 'graph' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              }}
            >
              Grafo Visual
            </button>
            <button
              type="button"
              onClick={() => setViewMode('list')}
              style={{
                background: viewMode === 'list' ? 'var(--surface)' : 'transparent',
                color: viewMode === 'list' ? 'var(--text)' : 'var(--text-muted)',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 12px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: viewMode === 'list' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              }}
            >
              Lista ({totalConns})
            </button>
          </div>

          {data && data.available_targets.length > 0 && !showForm && (
            <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}>
              <IconPlus size={15} /> Nova conexão
            </button>
          )}
        </div>
      </div>

      {error && <Alert>{error}</Alert>}

      {/* Formulário de Criação de Conexão */}
      {showForm && data && (
        <form className="card manual-card-form" onSubmit={handleAdd} style={{ marginBottom: '1.25rem' }}>
          <div className="row" style={{ gap: '0.5rem', alignItems: 'center' }}>
            <IconConnections size={18} color="var(--primary)" />
            <h3 style={{ margin: 0 }}>Vincular outro material</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginTop: '0.5rem' }}>
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

          <label style={{ marginTop: '0.5rem' }}>
            Nota de conexão (opcional)
            <input
              type="text"
              placeholder="Ex.: Necessário dominar este conceito antes do tópico de segurança avançada"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </label>

          <div className="row-end" style={{ gap: '0.5rem', marginTop: '0.75rem' }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowForm(false)}
              disabled={saving}
            >
              Cancelar
            </button>
            <button className="btn btn-primary btn-sm" disabled={saving}>
              {saving ? 'Conectando…' : 'Salvar conexão no grafo'}
            </button>
          </div>
        </form>
      )}

      {loading && <p className="muted">Carregando grafo de conexões…</p>}

      {/* Renderização do Grafo Visual Estilo Obsidian */}
      {!loading && viewMode === 'graph' && (
        <div style={{ marginBottom: '1.5rem' }}>
          <GraphCanvas
            currentMaterialId={materialId}
            currentMaterialTitle={materialTitle}
            nodes={graphNodes}
            edges={graphEdges}
            onAddConnectionClick={() => setShowForm(true)}
            isGlobalView={isGlobalView}
            onToggleViewMode={() => setIsGlobalView((prev) => !prev)}
          />
        </div>
      )}

      {/* Renderização da Lista de Detalhes (quando no modo Lista ou abaixo do Grafo) */}
      {!loading && (viewMode === 'list' || totalConns > 0) && (
        <div style={{ marginTop: viewMode === 'graph' ? '1rem' : '0' }}>
          {viewMode === 'graph' && totalConns > 0 && (
            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              Vínculos Registrados ({totalConns})
            </h3>
          )}

          {/* Conexões de Saída */}
          {hasOutgoing && (
            <div className="connections-group" style={{ marginBottom: '1.25rem' }}>
              <h4 className="connections-subtitle" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <IconLink size={14} /> Materiais vinculados a partir deste
              </h4>
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

          {/* Backlinks */}
          {hasIncoming && (
            <div className="connections-group">
              <h4 className="connections-subtitle" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <IconConnections size={14} /> Backlinks (Materiais que referenciam este)
              </h4>
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
      )}
    </div>
  )
}
