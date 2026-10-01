import { useEffect, useState } from 'react'
import { flashcardsApi, type Flashcard } from '../api/client'
import { IconClose, IconRotate, IconTrophy } from './Icons'

interface StudyModalProps {
  cards: Flashcard[]
  materialTitle: string
  onClose: () => void
  onCardReviewed: (updatedCard: Flashcard) => void
}

export function StudyModal({ cards, materialTitle, onClose, onCardReviewed }: StudyModalProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [stats, setStats] = useState({ errei: 0, dificil: 0, bom: 0, facil: 0 })
  const [finished, setFinished] = useState(false)

  const currentCard = cards[currentIndex]
  const progressPercent = Math.round((currentIndex / cards.length) * 100)

  // Suporte a teclado: Espaço para virar, 1/2/3/4 para avaliar, Esc para fechar
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        onClose()
        return
      }
      if (finished) return

      if (e.key === ' ' || e.code === 'Space') {
        e.preventDefault()
        setIsFlipped((prev) => !prev)
      } else if (isFlipped && !submitting) {
        if (e.key === '1') handleRating(0)
        else if (e.key === '2') handleRating(1)
        else if (e.key === '3') handleRating(2)
        else if (e.key === '4') handleRating(3)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFlipped, submitting, finished, currentIndex])

  async function handleRating(rating: number) {
    if (!currentCard || submitting) return
    setSubmitting(true)
    try {
      const updated = await flashcardsApi.review(currentCard.id, rating)
      onCardReviewed(updated)

      setStats((prev) => ({
        ...prev,
        errei: prev.errei + (rating === 0 ? 1 : 0),
        dificil: prev.dificil + (rating === 1 ? 1 : 0),
        bom: prev.bom + (rating === 2 ? 1 : 0),
        facil: prev.facil + (rating === 3 ? 1 : 0),
      }))

      if (currentIndex + 1 < cards.length) {
        setIsFlipped(false)
        setCurrentIndex((i) => i + 1)
      } else {
        setFinished(true)
      }
    } catch (err) {
      console.error('Erro ao salvar revisão:', err)
    } finally {
      setSubmitting(false)
    }
  }

  function restart() {
    setCurrentIndex(0)
    setIsFlipped(false)
    setFinished(false)
    setStats({ errei: 0, dificil: 0, bom: 0, facil: 0 })
  }

  return (
    <div className="study-modal-overlay" onClick={onClose}>
      <div className="study-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Topbar do modo de estudo */}
        <div className="study-modal-header">
          <div>
            <h3>Modo de Revisão</h3>
            <span className="muted">{materialTitle}</span>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onClose} title="Fechar (Esc)">
            <IconClose size={15} /> Fechar
          </button>
        </div>

        {!finished && currentCard ? (
          <>
            {/* Barra de progresso */}
            <div className="study-progress-wrap">
              <div className="study-progress-bar" style={{ width: `${progressPercent}%` }} />
            </div>
            <div className="study-meta-row">
              <span className="muted">
                Cartão {currentIndex + 1} de {cards.length}
              </span>
              <span className="muted" style={{ fontSize: '0.8rem' }}>
                Atalhos: Espaço (virar) · 1 a 4 (avaliar)
              </span>
            </div>

            {/* Cartão com efeito de virar 3D */}
            <div
              className={`flip-card ${isFlipped ? 'flipped' : ''}`}
              onClick={() => setIsFlipped((prev) => !prev)}
            >
              <div className="flip-card-inner">
                {/* Frente: Pergunta */}
                <div className="flip-card-front">
                  <div className="card-side-tag">Pergunta</div>
                  <div className="card-content-text">{currentCard.question}</div>
                  <div className="flip-hint muted">Clique ou pressione Espaço para ver a resposta</div>
                </div>

                {/* Verso: Estilo Anki (Pergunta + Divisor + Resposta) */}
                <div className="flip-card-back">
                  <div className="card-side-tag tag-answer">Resposta</div>
                  <div className="card-question-preview muted">{currentCard.question}</div>
                  <hr className="anki-divider" />
                  <div className="card-content-text anki-answer-text">{currentCard.answer}</div>
                </div>
              </div>
            </div>

            {/* Botões de avaliação SM-2 */}
            <div className="rating-actions">
              {isFlipped ? (
                <>
                  <button
                    className="btn btn-rating btn-rating-again"
                    onClick={() => handleRating(0)}
                    disabled={submitting}
                  >
                    <strong>1. Errei</strong>
                    <span className="rating-interval">1 dia</span>
                  </button>
                  <button
                    className="btn btn-rating btn-rating-hard"
                    onClick={() => handleRating(1)}
                    disabled={submitting}
                  >
                    <strong>2. Difícil</strong>
                    <span className="rating-interval">2 dias</span>
                  </button>
                  <button
                    className="btn btn-rating btn-rating-good"
                    onClick={() => handleRating(2)}
                    disabled={submitting}
                  >
                    <strong>3. Bom</strong>
                    <span className="rating-interval">3 dias</span>
                  </button>
                  <button
                    className="btn btn-rating btn-rating-easy"
                    onClick={() => handleRating(3)}
                    disabled={submitting}
                  >
                    <strong>4. Fácil</strong>
                    <span className="rating-interval">4+ dias</span>
                  </button>
                </>
              ) : (
                <button
                  className="btn btn-primary btn-block btn-reveal"
                  onClick={() => setIsFlipped(true)}
                >
                  Mostrar Resposta (Espaço)
                </button>
              )}
            </div>
          </>
        ) : (
          /* Tela de conclusão da sessão */
          <div className="study-finished-card">
            <div className="study-finished-icon" style={{ color: 'var(--primary)' }}>
              <IconTrophy size={48} />
            </div>
            <h2>Sessão de estudo concluída!</h2>
            <p className="muted">
              Você revisou {cards.length} {cards.length === 1 ? 'cartão' : 'cartões'} com o algoritmo de repetição espaçada.
            </p>

            <div className="study-stats-grid">
              <div className="stat-box">
                <span className="stat-num color-again">{stats.errei}</span>
                <span className="stat-label">Errei</span>
              </div>
              <div className="stat-box">
                <span className="stat-num color-hard">{stats.dificil}</span>
                <span className="stat-label">Difícil</span>
              </div>
              <div className="stat-box">
                <span className="stat-num color-good">{stats.bom}</span>
                <span className="stat-label">Bom</span>
              </div>
              <div className="stat-box">
                <span className="stat-num color-easy">{stats.facil}</span>
                <span className="stat-label">Fácil</span>
              </div>
            </div>

            <div className="row" style={{ justifyContent: 'center', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button className="btn btn-ghost" onClick={restart}>
                <IconRotate size={15} /> Revisar novamente
              </button>
              <button className="btn btn-primary" onClick={onClose}>
                Concluir e voltar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
