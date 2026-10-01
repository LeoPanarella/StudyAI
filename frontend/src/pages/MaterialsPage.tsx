import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { formatBytes, formatDate, materialsApi, type Material } from '../api/client'
import { Alert } from '../components/Alert'
import { IconCheck, IconFlashcards, IconPlus } from '../components/Icons'

export function MaterialsPage() {
  const navigate = useNavigate()
  const [materials, setMaterials] = useState<Material[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  // estado do painel de upload
  const [showUpload, setShowUpload] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function load() {
    try {
      setMaterials(await materialsApi.list())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar materiais.')
    }
  }

  useEffect(() => {
    load()
  }, [])

  function handleFileChange(f: File | null) {
    setFile(f)
    setUploadError(null)
    if (f && !title) setTitle(f.name.replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ').trim())
  }

  async function handleUpload(e: FormEvent) {
    e.preventDefault()
    if (!file) return setUploadError('Selecione um arquivo PDF.')
    setUploading(true)
    setUploadError(null)
    try {
      const created = await materialsApi.upload(file, title)
      navigate(`/materiais/${created.id}`)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Falha no upload.')
    } finally {
      setUploading(false)
    }
  }

  function cancelUpload() {
    setShowUpload(false)
    setFile(null)
    setTitle('')
    setUploadError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <>
      <div className="page-header">
        <div>
          <span className="section-pill">Acervo Acadêmico</span>
          <h1>Meus materiais</h1>
          <p className="muted">Envie PDFs de apostilas, artigos ou anotações para estudar com IA e repetição espaçada.</p>
        </div>
        {!showUpload && (
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            <IconPlus size={15} /> Enviar PDF
          </button>
        )}
      </div>

      {showUpload && (
        <form className="card upload-card" onSubmit={handleUpload}>
          <h2>Novo material</h2>
          {uploadError && <Alert>{uploadError}</Alert>}
          <label className="file-drop">
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              disabled={uploading}
            />
            {file ? (
              <span>
                <strong>{file.name}</strong> <span className="muted">({formatBytes(file.size)})</span>
              </span>
            ) : (
              <span className="muted">Clique para escolher um arquivo PDF (até 25 MB)</span>
            )}
          </label>
          <label>
            Título
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ex.: Biologia — Fotossíntese" maxLength={200} disabled={uploading} />
          </label>
          <div className="row-end">
            <button type="button" className="btn btn-ghost" onClick={cancelUpload} disabled={uploading}>
              Cancelar
            </button>
            <button className="btn btn-primary" disabled={uploading || !file}>
              {uploading ? 'Enviando e extraindo texto…' : 'Enviar'}
            </button>
          </div>
        </form>
      )}

      {error && <Alert>{error}</Alert>}

      {materials === null && !error && <p className="muted">Carregando…</p>}

      {materials && materials.length === 0 && !showUpload && (
        <div className="empty">
          <p>Você ainda não enviou nenhum material.</p>
          <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
            Enviar meu primeiro PDF
          </button>
        </div>
      )}

      {materials && materials.length > 0 && (
        <ul className="material-list">
          {materials.map((m) => (
            <li key={m.id}>
              <Link to={`/materiais/${m.id}`} className="card material-item">
                <div className="material-icon" aria-hidden="true">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                    <polyline points="14 2 14 8 20 8" />
                    <path d="M9 13h6" />
                    <path d="M9 17h3" />
                  </svg>
                </div>
                <div className="material-info">
                  <h3>{m.title}</h3>
                  <p className="muted">
                    {m.filename} · {m.page_count} {m.page_count === 1 ? 'página' : 'páginas'} · {formatBytes(m.file_size)} · enviado em{' '}
                    {formatDate(m.uploaded_at)}
                  </p>
                </div>
                <div className="material-badges">
                  {m.char_count === 0 && <span className="badge badge-warn">sem texto</span>}
                  {m.has_summary && (
                    <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                      <IconCheck size={11} /> resumo
                    </span>
                  )}
                  {m.flashcard_count > 0 && (
                    <span className="badge badge-indigo" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                      <IconFlashcards size={11} /> {m.flashcard_count} flashcards
                    </span>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
