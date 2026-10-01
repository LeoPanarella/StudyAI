import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { formatBytes, formatDate, formatDateTime, materialsApi, type MaterialDetail } from '../api/client'
import { Alert } from '../components/Alert'
import { ConnectionsSection } from '../components/ConnectionsSection'
import { FlashcardsSection } from '../components/FlashcardsSection'
import {
  IconArrowLeft,
  IconConnections,
  IconFlashcards,
  IconSparkles,
  IconSummary,
  IconText,
  IconTrash,
} from '../components/Icons'
import { Markdown } from '../components/Markdown'

export function MaterialDetailPage() {
  const { id } = useParams()
  const materialId = Number(id)
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const [material, setMaterial] = useState<MaterialDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [fullText, setFullText] = useState<string | null>(null)
  const [loadingText, setLoadingText] = useState(false)
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [requesting, setRequesting] = useState(false)
  const [summaryError, setSummaryError] = useState<string | null>(null)
  const [dismissedJobId, setDismissedJobId] = useState<number | null>(null)

  // Aba ativa: 'summary' | 'flashcards' | 'connections' | 'text' (sincronizada com ?aba= na URL)
  const activeTab = searchParams.get('aba') || 'summary'
  const setTab = (tab: string) => setSearchParams({ aba: tab }, { replace: true })

  const reload = useCallback(async () => {
    try {
      const data = await materialsApi.get(materialId)
      setMaterial(data)
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar material.')
      return null
    }
  }, [materialId])

  useEffect(() => {
    reload()
  }, [reload])

  // Polling se o job de resumo estiver ativo
  const generatingSummary =
    material?.summary_job?.status === 'pending' || material?.summary_job?.status === 'running'
  useEffect(() => {
    if (!generatingSummary) return
    const timer = setInterval(reload, 2500)
    return () => clearInterval(timer)
  }, [generatingSummary, reload])

  async function showFullText() {
    setLoadingText(true)
    try {
      const { content_text } = await materialsApi.content(materialId)
      setFullText(content_text)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar texto.')
    } finally {
      setLoadingText(false)
    }
  }

  async function saveTitle() {
    if (!material) return
    const next = titleDraft.trim()
    if (!next || next === material.title) return setEditingTitle(false)
    try {
      setMaterial(await materialsApi.rename(material.id, next))
      setEditingTitle(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao renomear.')
    }
  }

  async function handleGenerateSummary() {
    if (!material) return
    setRequesting(true)
    setSummaryError(null)
    try {
      const job = await materialsApi.generateSummary(material.id)
      setMaterial({ ...material, summary_job: job })
    } catch (err) {
      setSummaryError(err instanceof Error ? err.message : 'Não foi possível iniciar a geração do resumo.')
    } finally {
      setRequesting(false)
    }
  }

  async function handleDelete() {
    if (!material) return
    if (!confirm(`Excluir "${material.title}"? O resumo, flashcards e conexões deste material também serão removidos.`)) return
    setDeleting(true)
    try {
      await materialsApi.remove(material.id)
      navigate('/materiais', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir.')
      setDeleting(false)
    }
  }

  if (error && !material) {
    return (
      <>
        <Link to="/materiais" className="back-link">
          <IconArrowLeft size={16} /> Meus materiais
        </Link>
        <Alert>{error}</Alert>
      </>
    )
  }
  if (!material) return <p className="muted">Carregando…</p>

  const hasText = material.char_count > 0
  const job = material.summary_job
  const jobFailed = job?.status === 'failed' && job.id !== dismissedJobId
  const busy = generatingSummary || requesting
  const textShown = fullText ?? material.content_preview
  const isTruncated = fullText === null && material.char_count > material.content_preview.length

  return (
    <>
      <Link to="/materiais" className="back-link">
        <IconArrowLeft size={16} /> Meus materiais
      </Link>

      <div className="page-header">
        <div className="grow">
          {editingTitle ? (
            <div className="title-edit">
              <input
                value={titleDraft}
                onChange={(e) => setTitleDraft(e.target.value)}
                maxLength={200}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') saveTitle()
                  if (e.key === 'Escape') setEditingTitle(false)
                }}
              />
              <button className="btn btn-primary btn-sm" onClick={saveTitle}>Salvar</button>
              <button className="btn btn-ghost btn-sm" onClick={() => setEditingTitle(false)}>Cancelar</button>
            </div>
          ) : (
            <h1
              className="editable"
              title="Clique para renomear"
              onClick={() => {
                setTitleDraft(material.title)
                setEditingTitle(true)
              }}
            >
              {material.title}
            </h1>
          )}
          <p className="muted">
            {material.filename} · {material.page_count} {material.page_count === 1 ? 'página' : 'páginas'} · {formatBytes(material.file_size)} ·{' '}
            {material.char_count.toLocaleString('pt-BR')} caracteres extraídos · enviado em {formatDate(material.uploaded_at)}
          </p>
        </div>
        <button className="btn btn-danger-ghost btn-sm" onClick={handleDelete} disabled={deleting}>
          <IconTrash size={14} /> {deleting ? 'Excluindo…' : 'Excluir'}
        </button>
      </div>

      {error && <Alert>{error}</Alert>}
      {material.extraction_warning && <Alert kind="warning">{material.extraction_warning}</Alert>}

      {/* Navegação por Abas */}
      <div className="tabs-bar">
        <button
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setTab('summary')}
        >
          <IconSummary size={16} /> Resumo {material.has_summary && <span className="tab-pill">pronto</span>}
        </button>
        <button
          className={`tab-btn ${activeTab === 'flashcards' ? 'active' : ''}`}
          onClick={() => setTab('flashcards')}
        >
          <IconFlashcards size={16} /> Flashcards SM-2{' '}
          {material.flashcard_count > 0 && (
            <span className="tab-pill">{material.flashcard_count}</span>
          )}
        </button>
        <button
          className={`tab-btn ${activeTab === 'connections' ? 'active' : ''}`}
          onClick={() => setTab('connections')}
        >
          <IconConnections size={16} /> Conexões de Estudo
        </button>
        <button
          className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => setTab('text')}
        >
          <IconText size={16} /> Texto extraído
        </button>
      </div>

      {/* Conteúdo da Aba Resumo */}
      {activeTab === 'summary' && (
        <section className="card section">
          <div className="section-header">
            <h2>Resumo com IA</h2>
            {hasText && (
              <button
                className={`btn btn-sm ${material.summary ? 'btn-ghost' : 'btn-primary'}`}
                onClick={handleGenerateSummary}
                disabled={busy}
              >
                {busy ? (
                  <>
                    <span className="spinner" aria-hidden /> Gerando…
                  </>
                ) : material.summary ? (
                  'Regenerar'
                ) : (
                  <>
                    <IconSparkles size={14} /> Gerar resumo com IA
                  </>
                )}
              </button>
            )}
          </div>

          {summaryError && <Alert>{summaryError}</Alert>}

          {jobFailed && (
            <Alert>
              {job.error ?? 'A geração do resumo falhou.'}{' '}
              <button className="link-btn" onClick={() => setDismissedJobId(job.id)}>
                fechar
              </button>
            </Alert>
          )}

          {generatingSummary && (
            <p className="muted generating-note">
              <span className="spinner" aria-hidden /> A IA está lendo o material e escrevendo o resumo. Normalmente leva de 5 a 30
              segundos; em horários de pico pode demorar alguns minutos. Pode sair desta página — o resumo ficará salvo aqui.
            </p>
          )}

          {material.summary ? (
            <>
              <Markdown>{material.summary.text}</Markdown>
              <p className="muted summary-meta">
                Gerado em {formatDateTime(material.summary.generated_at)}
                {material.summary.model ? ` · ${material.summary.model}` : ''}
              </p>
            </>
          ) : (
            !generatingSummary && (
              <p className="muted">
                {hasText
                  ? 'Nenhum resumo ainda. Clique em "Gerar resumo com IA" para criar um resumo estruturado deste material.'
                  : 'Não é possível gerar resumo: este PDF não tem texto extraível.'}
              </p>
            )
          )}
        </section>
      )}

      {/* Conteúdo da Aba Flashcards */}
      {activeTab === 'flashcards' && (
        <FlashcardsSection
          materialId={material.id}
          materialTitle={material.title}
          initialJob={material.flashcards_job}
        />
      )}

      {/* Conteúdo da Aba Conexões de Estudo (Obsidian-style) */}
      {activeTab === 'connections' && (
        <ConnectionsSection materialId={material.id} />
      )}

      {/* Conteúdo da Aba Texto Original */}
      {activeTab === 'text' && (
        <section className="card section">
          <div className="section-header">
            <h2>Texto extraído do documento</h2>
            {hasText && isTruncated && (
              <button className="btn btn-ghost btn-sm" onClick={showFullText} disabled={loadingText}>
                {loadingText ? 'Carregando…' : 'Ver texto completo'}
              </button>
            )}
          </div>
          {hasText ? (
            <pre className="extracted-text">{textShown}{isTruncated ? '\n…' : ''}</pre>
          ) : (
            <p className="muted">Nenhum texto extraível foi encontrado neste PDF.</p>
          )}
        </section>
      )}
    </>
  )
}
