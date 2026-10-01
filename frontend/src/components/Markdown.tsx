import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/** Renderiza Markdown gerado pela IA. Sem HTML bruto (padrão do react-markdown), logo seguro contra XSS. */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  )
}
