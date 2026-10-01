import { useEffect, useState, type FormEvent } from 'react'
import {
  flashcardsApi,
  type AIJob,
  type Flashcard,
  type FlashcardListResponse,
} from '../api/client'
import { Alert } from './Alert'
import { IconPlay, IconPlus, IconSparkles, IconTarget, IconTrash } from './Icons'
import { StudyModal } from './StudyModal'

interface FlashcardsSectionProps {
  materialId: number
  materialTitle: string
  initialJob: AIJob | null
}

export function FlashcardsSection({
  materialId,
  materialTitle,
  initialJob,
}: FlashcardsSectionProps) {
  const [data, setData] = useState<FlashcardListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Estado do job de IA
  const [job, setJob] = useState<AIJob | null>(initialJob)
  const [generating, setGenerating] = useState(Boolean(initialJob && (initialJob.status === 'pending' || initialJob.status === 'running')))
  const [dismissedJobId, setDismissedJobId] = useState<number | null>(null)

  // Caixa de configuração de foco para IA
  const [showGenerateBox, setShowGenerateBox] = useState(false)
  const [focusInput, setFocusInput] = useState('')

  // Estado do formulário de criação manual
  const [showAddForm, setShowAddForm] = useState(false)
  const [newQuestion, setNewQuestion] = useState('')
  const [newAnswer, setNewAnswer] = useState('')
  const [adding, setAdding] = useState(false)

  // Estado do Modo de Estudo (Modal)
  const [studyOpen, setStudyOpen] = useState(false)
  const [studyCards, setStudyCards] = useState<Flashcard[]>([])

  async function loadCards() {
    try {
      const res = await flashcardsApi.list(materialId)
      setData(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar flashcards.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCards()
  }, [materialId])

  // Polling enquanto houver job pendente ou executando
  useEffect(() => {
    if (!job || (job.status !== 'pending' && job.status !== 'running')) {
      setGenerating(false)
      return
    }
    setGenerating(true)

    const timer = setInterval(async () => {
      try {
        const res = await flashcardsApi.list(materialId)
        setData(res)
      } catch {
        /* ignora falha transitória durante polling */
      }
    }, 2500)

    return () => clearInterval(timer)
  }, [job, materialId])

  async function handleStartGenerate(e?: FormEvent) {
    if (e) e.preventDefault()
    setError(null)
    setGenerating(true)
    setShowGenerateBox(false)
    try {
      const newJob = await flashcardsApi.generate(materialId, focusInput)
      setJob(newJob)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível solicitar os flashcards.')
      setGenerating(false)
    }
  }

  async function handleAddManual(e: FormEvent) {
    e.preventDefault()
    if (!newQuestion.trim() || !newAnswer.trim()) return
    setAdding(true)
    try {
      const created = await flashcardsApi.create(materialId, newQuestion.trim(), newAnswer.trim())
      setData((prev) =>
        prev
          ? {
              ...prev,
              items: [created, ...prev.items],
              total_count: prev.total_count + 1,
              due_count: prev.due_count + 1,
            }
          : { items: [created], total_count: 1, due_count: 1 }
      )
      setNewQuestion('')
      setNewAnswer('')
      setShowAddForm(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar cartão.')
    } finally {
      setAdding(false)
    }
  }

  async function handleDelete(cardId: number) {
    if (!confirm('Excluir este flashcard?')) return
    try {
      await flashcardsApi.remove(cardId)
      setData((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((c) => c.id !== cardId),
              total_count: Math.max(0, prev.total_count - 1),
            }
          : null
      )
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Falha ao excluir.')
    }
  }

  async function startStudy(mode: 'due' | 'all' = 'all') {
    try {
      const cards = await flashcardsApi.study(materialId, mode)
      if (!cards.length) {
        alert('Nenhum cartão disponível para revisão.')
        return
      }
      setStudyCards(cards)
      setStudyOpen(true)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Falha ao iniciar sessão de estudo.')
    }
  }

  function handleCardReviewed(updated: Flashcard) {
    setData((prev) => {
      if (!prev) return null
      return {
        ...prev,
        items: prev.items.map((c) => (c.id === updated.id ? updated : c)),
        due_count: prev.items.reduce(
          (acc, c) => acc + (c.id === updated.id ? (updated.is_due ? 1 : 0) : c.is_due ? 1 : 0),
          0
        ),
      }
    })
  }

  const jobFailed = job && job.status === 'failed' && job.id !== dismissedJobId

  return (
    <div className="flashcards-section">
      <div className="section-header-row">
        <div>
          <h2>Flashcards & Repetição Espaçada</h2>
          <p className="muted">
            Memorize os conceitos-chave com repetição espaçada baseada no algoritmo SM-2.
          </p>
        </div>

        <div className="row" style={{ gap: '0.5rem' }}>
          {data && data.total_count > 0 && (
            <button
              className="btn btn-primary"
              onClick={() => startStudy(data.due_count > 0 ? 'due' : 'all')}
              disabled={generating}
            >
              <IconPlay size={14} /> Praticar agora {data.due_count > 0 && `(${data.due_count} pendentes)`}
            </button>
          )}

          <button
            className="btn btn-outline"
            onClick={() => setShowGenerateBox((v) => !v)}
            disabled={generating}
          >
            {generating ? (
              <>
                <span className="spinner" /> Gerando…
              </>
            ) : (
              <>
                <IconSparkles size={15} />{' '}
                {data && data.total_count > 0 ? 'Gerar com foco' : 'Gerar com IA'}
              </>
            )}
          </button>

          {!showAddForm && (
            <button
              className="btn btn-ghost"
              onClick={() => setShowAddForm(true)}
              disabled={generating}
            >
              <IconPlus size={14} /> Adicionar manual
            </button>
          )}
        </div>
      </div>

      {error && <Alert>{error}</Alert>}

      {/* Caixa expansível para geração com foco direcionado */}
      {showGenerateBox && !generating && (
        <form className="card generate-focus-card" onSubmit={handleStartGenerate}>
          <div className="row" style={{ gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
            <IconTarget size={18} color="var(--primary)" />
            <h3 style={{ margin: 0 }}>Geração direcionada com IA</h3>
          </div>
          <p className="muted" style={{ fontSize: '0.875rem', marginBottom: '0.75rem' }}>
            Você pode especificar um tema, capítulo ou foco de estudo. A IA priorizará os trechos
            mais relevantes deste documento para formular os flashcards.
          </p>

          <label>
            Foco ou tema específico (opcional)
            <input
              type="text"
              placeholder="Ex.: Focar estritamente no modelo OSI e diferenças entre TCP e UDP"
              value={focusInput}
              onChange={(e) => setFocusInput(e.target.value)}
              autoFocus
            />
          </label>

          <div className="row-end" style={{ gap: '0.5rem', marginTop: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowGenerateBox(false)}
            >
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary btn-sm">
              <IconSparkles size={14} /> Iniciar geração
            </button>
          </div>
        </form>
      )}

      {jobFailed && (
        <Alert>
          {job.error || 'A geração de flashcards falhou. Tente novamente.'}{' '}
          <button
            className="link-btn"
            onClick={() => setDismissedJobId(job.id)}
            style={{ fontWeight: 600, marginLeft: '0.5rem' }}
          >
            fechar
          </button>
        </Alert>
      )}

      {generating && (
        <div className="card generating-note">
          <span className="spinner" />
          <div>
            <strong>A IA está formulando seus flashcards de aprendizagem ativa…</strong>
            <p className="muted" style={{ fontSize: '0.85rem' }}>
              {job?.focus
                ? `Priorizando o foco definido: "${job.focus}"`
                : 'Cada cartão é calibrado para o algoritmo SM-2. Pode levar alguns instantes.'}
            </p>
          </div>
        </div>
      )}

      {/* Formulário de adição manual */}
      {showAddForm && (
        <form className="card manual-card-form" onSubmit={handleAddManual}>
          <h3>Novo flashcard manual</h3>
          <label>
            Pergunta (frente do cartão)
            <input
              type="text"
              placeholder="Ex.: Qual é a principal função da clorofila?"
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
              required
              autoFocus
            />
          </label>
          <label>
            Resposta (verso do cartão)
            <textarea
              placeholder="Ex.: Absorver a luz solar nas faixas azul e vermelha para energizar os elétrons da fotossíntese."
              value={newAnswer}
              onChange={(e) => setNewAnswer(e.target.value)}
              rows={2}
              required
            />
          </label>
          <div className="row-end" style={{ gap: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowAddForm(false)}
              disabled={adding}
            >
              Cancelar
            </button>
            <button className="btn btn-primary btn-sm" disabled={adding}>
              {adding ? 'Salvando…' : 'Salvar cartão'}
            </button>
          </div>
        </form>
      )}

      {loading && <p className="muted">Carregando cartões…</p>}

      {/* Listagem de Flashcards */}
      {data && data.items.length > 0 ? (
        <div className="flashcards-grid">
          {data.items.map((card, idx) => (
            <div key={card.id} className="card flashcard-preview-item">
              <div className="flashcard-item-header">
                <span className="card-number">#{idx + 1}</span>
                <div className="row" style={{ gap: '0.5rem', alignItems: 'center' }}>
                  {card.is_due ? (
                    <span className="badge badge-warn">revisar hoje</span>
                  ) : (
                    <span className="badge badge-subtle">
                      em {card.interval_days} {card.interval_days === 1 ? 'dia' : 'dias'}
                    </span>
                  )}
                  <button
                    className="icon-btn-delete"
                    onClick={() => handleDelete(card.id)}
                    title="Excluir cartão"
                  >
                    <IconTrash size={14} />
                  </button>
                </div>
              </div>

              <div className="flashcard-item-question">
                <strong>P:</strong> {card.question}
              </div>
              <div className="flashcard-item-answer muted">
                <strong>R:</strong> {card.answer}
              </div>

              <div className="flashcard-item-footer muted">
                <span>Repetições: {card.repetitions}</span>
                <span>Fator de facilidade: {card.ease_factor}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        !loading &&
        !generating &&
        !showAddForm && (
          <div className="empty-flashcards card">
            <p>Este material ainda não possui flashcards.</p>
            <p className="muted" style={{ marginBottom: '1rem' }}>
              Gere automaticamente com o Gemini ou adicione cartões manuais para iniciar suas revisões.
            </p>
            <button className="btn btn-primary" onClick={() => setShowGenerateBox(true)}>
              <IconSparkles size={15} /> Gerar Flashcards com IA
            </button>
          </div>
        )
      )}

      {/* Modal Interativo de Revisão */}
      {studyOpen && (
        <StudyModal
          cards={studyCards}
          materialTitle={materialTitle}
          onClose={() => {
            setStudyOpen(false)
            loadCards()
          }}
          onCardReviewed={handleCardReviewed}
        />
      )}
    </div>
  )
}
