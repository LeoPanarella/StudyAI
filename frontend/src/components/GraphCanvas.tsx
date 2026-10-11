// ============================================================================
// StudyAI — Visualização em Grafo de Conhecimento (PCI)
// Autor: Leo Panarella
//
// Componente de grafo interativo inspirado no Obsidian.
// Implementado em HTML5 Canvas nativo com simulação de física de partículas:
// 1. Repulsão entre nós (para evitar sobreposição)
// 2. Força elástica nas conexões (atrai materiais relacionados)
// 3. Gravidade central e fricção (para manter o grafo estável no centro)
// ============================================================================

import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export interface GraphNodeData {
  id: number
  title: string
  filename?: string
  charCount?: number
  flashcardCount?: number
  hasSummary?: boolean
  relationType?: string
  note?: string | null
  isCenter?: boolean
  isBacklink?: boolean
  color?: string
}

export interface GraphEdgeData {
  id: number | string
  source: number
  target: number
  relationType: string
  note?: string | null
}

interface GraphCanvasProps {
  currentMaterialId: number
  currentMaterialTitle: string
  nodes: GraphNodeData[]
  edges: GraphEdgeData[]
  onAddConnectionClick?: () => void
  onDeleteConnectionClick?: (connectionId: number) => void
  isGlobalView?: boolean
  onToggleViewMode?: () => void
}

interface SimNode extends GraphNodeData {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  baseColor: string
}

const RELATION_COLORS: Record<string, { color: string; label: string }> = {
  prerequisite: { color: '#f59e0b', label: 'Pré-requisito' }, // Âmbar / Laranja
  deepening: { color: '#a855f7', label: 'Aprofundamento' }, // Roxo / Violeta
  related: { color: '#38bdf8', label: 'Correlato' }, // Azul celeste
  application: { color: '#10b981', label: 'Aplicação' }, // Verde esmeralda
  center: { color: '#6366f1', label: 'Material Atual' }, // Indigo brilhante
  available: { color: '#64748b', label: 'Outro Material' }, // Ardósia sutil
}

export function GraphCanvas({
  currentMaterialId,
  currentMaterialTitle: _currentMaterialTitle,
  nodes,
  edges,
  onAddConnectionClick,
  onDeleteConnectionClick: _onDeleteConnectionClick,
  isGlobalView,
  onToggleViewMode,
}: GraphCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const navigate = useNavigate()

  // Estado da câmera (Pan e Zoom)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [showSettings, setShowSettings] = useState(false)
  const [showLabels, setShowLabels] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [hoveredNode, setHoveredNode] = useState<SimNode | null>(null)
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })

  // Referências para a simulação física
  const simNodesRef = useRef<SimNode[]>([])
  const draggedNodeRef = useRef<SimNode | null>(null)
  const isPanningRef = useRef(false)
  const panStartRef = useRef({ x: 0, y: 0 })
  const mousePosRef = useRef({ x: 0, y: 0 })
  const animationFrameIdRef = useRef<number | null>(null)

  // Inicializa ou atualiza os nós da física
  useEffect(() => {
    const width = containerRef.current?.clientWidth || 800
    const height = containerRef.current?.clientHeight || 520
    const centerX = width / 2
    const centerY = height / 2

    const existingMap = new Map(simNodesRef.current.map((n) => [n.id, n]))

    const initialSimNodes: SimNode[] = nodes.map((n, idx) => {
      const existing = existingMap.get(n.id)
      let baseColor = RELATION_COLORS.available.color
      let radius = 12

      if (n.id === currentMaterialId) {
        baseColor = RELATION_COLORS.center.color
        radius = 20
      } else if (n.relationType && RELATION_COLORS[n.relationType]) {
        baseColor = RELATION_COLORS[n.relationType].color
        radius = 14
      }

      if (existing) {
        return {
          ...n,
          x: existing.x,
          y: existing.y,
          vx: existing.vx,
          vy: existing.vy,
          radius,
          baseColor,
        }
      }

      // Distribuição circular suave ao redor do centro
      if (n.id === currentMaterialId) {
        return {
          ...n,
          x: centerX,
          y: centerY,
          vx: 0,
          vy: 0,
          radius,
          baseColor,
        }
      }

      const angle = (idx / Math.max(1, nodes.length - 1)) * Math.PI * 2
      const dist = 140 + (idx % 3) * 45
      return {
        ...n,
        x: centerX + Math.cos(angle) * dist + (Math.random() - 0.5) * 30,
        y: centerY + Math.sin(angle) * dist + (Math.random() - 0.5) * 30,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        radius,
        baseColor,
      }
    })

    simNodesRef.current = initialSimNodes
  }, [nodes, currentMaterialId])

  // Loop de Animação e Física (Force-Directed Graph estilo Obsidian)
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let isRunning = true

    function step() {
      if (!isRunning || !canvas || !ctx) return

      const width = canvas.width
      const height = canvas.height
      const centerX = width / 2
      const centerY = height / 2
      const simNodes = simNodesRef.current

      // 1. Força de Repulsão entre todos os nós (Coulomb)
      const kRepulsion = 3200
      for (let i = 0; i < simNodes.length; i++) {
        for (let j = i + 1; j < simNodes.length; j++) {
          const a = simNodes[i]
          const b = simNodes[j]
          const dx = b.x - a.x
          const dy = b.y - a.y
          const distSq = dx * dx + dy * dy + 100
          const dist = Math.sqrt(distSq)
          const force = kRepulsion / distSq

          const fx = (dx / dist) * force
          const fy = (dy / dist) * force

          if (a !== draggedNodeRef.current) {
            a.vx -= fx
            a.vy -= fy
          }
          if (b !== draggedNodeRef.current) {
            b.vx += fx
            b.vy += fy
          }
        }
      }

      // 2. Força de Atração por Aresta/Conexão (Molas de Hooke)
      const nodeIndexMap = new Map(simNodes.map((n) => [n.id, n]))
      const kSpring = 0.035
      const idealLength = 160

      edges.forEach((edge) => {
        const u = nodeIndexMap.get(edge.source)
        const v = nodeIndexMap.get(edge.target)
        if (!u || !v) return

        const dx = v.x - u.x
        const dy = v.y - u.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const delta = dist - idealLength
        const force = delta * kSpring

        const fx = (dx / dist) * force
        const fy = (dy / dist) * force

        if (u !== draggedNodeRef.current) {
          u.vx += fx
          u.vy += fy
        }
        if (v !== draggedNodeRef.current) {
          v.vx -= fx
          v.vy -= fy
        }
      })

      // 3. Gravidade em direção ao centro do Canvas
      const kGravity = 0.008
      simNodes.forEach((node) => {
        if (node === draggedNodeRef.current) return
        const dx = centerX - node.x
        const dy = centerY - node.y
        node.vx += dx * kGravity
        node.vy += dy * kGravity

        // Amortecimento / Fricção
        node.vx *= 0.84
        node.vy *= 0.84

        // Atualização de posição
        node.x += node.vx
        node.y += node.vy
      })

      // 4. Renderização no Canvas
      ctx.clearRect(0, 0, width, height)

      // Fundo escuro estilo Obsidian
      ctx.fillStyle = '#14161f'
      ctx.fillRect(0, 0, width, height)

      // Grid sutil de pontinhos
      ctx.fillStyle = 'rgba(255, 255, 255, 0.04)'
      const dotSpacing = 36
      for (let x = 0; x < width; x += dotSpacing) {
        for (let y = 0; y < height; y += dotSpacing) {
          ctx.beginPath()
          ctx.arc(x, y, 1, 0, Math.PI * 2)
          ctx.fill()
        }
      }

      // Aplica Pan e Zoom
      ctx.save()
      ctx.translate(width / 2 + pan.x, height / 2 + pan.y)
      ctx.scale(zoom, zoom)
      ctx.translate(-width / 2, -height / 2)

      const activeHover = hoveredNode

      // Desenha as arestas / conexões
      edges.forEach((edge) => {
        const u = nodeIndexMap.get(edge.source)
        const v = nodeIndexMap.get(edge.target)
        if (!u || !v) return

        const isConnectedToHover = activeHover && (u.id === activeHover.id || v.id === activeHover.id)
        const isDimmed = activeHover && !isConnectedToHover

        ctx.beginPath()
        ctx.moveTo(u.x, u.y)
        ctx.lineTo(v.x, v.y)

        let edgeColor = 'rgba(148, 163, 184, 0.3)'
        let lineWidth = 1.6

        if (edge.relationType === 'prerequisite') {
          edgeColor = 'rgba(245, 158, 11, 0.65)'
        } else if (edge.relationType === 'deepening') {
          edgeColor = 'rgba(168, 85, 247, 0.65)'
        } else if (edge.relationType === 'application') {
          edgeColor = 'rgba(16, 185, 129, 0.65)'
        } else if (edge.relationType === 'related') {
          edgeColor = 'rgba(56, 189, 248, 0.65)'
        }

        if (isConnectedToHover) {
          lineWidth = 2.8
          edgeColor = 'rgba(255, 255, 255, 0.9)'
        } else if (isDimmed) {
          edgeColor = 'rgba(148, 163, 184, 0.08)'
        }

        ctx.strokeStyle = edgeColor
        ctx.lineWidth = lineWidth
        ctx.stroke()

        // Seta ou indicador de direção
        const midX = (u.x + v.x) / 2
        const midY = (u.y + v.y) / 2
        ctx.beginPath()
        ctx.arc(midX, midY, 2.5, 0, Math.PI * 2)
        ctx.fillStyle = edgeColor
        ctx.fill()
      })

      // Desenha os nós
      simNodes.forEach((node) => {
        const isCenter = node.id === currentMaterialId
        const isHovered = activeHover && activeHover.id === node.id
        const isNeighbor =
          activeHover &&
          edges.some(
            (e) =>
              (e.source === activeHover.id && e.target === node.id) ||
              (e.target === activeHover.id && e.source === node.id)
          )
        const isDimmed = activeHover && !isHovered && !isNeighbor && node.id !== currentMaterialId

        // Brilho / Aura no nó central ou hover
        if (isCenter || isHovered) {
          const auraRadius = node.radius + (isHovered ? 12 : 8)
          const grad = ctx.createRadialGradient(node.x, node.y, node.radius * 0.5, node.x, node.y, auraRadius)
          grad.addColorStop(0, node.baseColor + '88')
          grad.addColorStop(1, node.baseColor + '00')
          ctx.beginPath()
          ctx.arc(node.x, node.y, auraRadius, 0, Math.PI * 2)
          ctx.fillStyle = grad
          ctx.fill()
        }

        // Círculo do Nó
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2)
        ctx.fillStyle = isDimmed ? '#33415555' : node.baseColor
        ctx.fill()

        ctx.lineWidth = isHovered ? 2.5 : isCenter ? 2.2 : 1.2
        ctx.strokeStyle = isHovered ? '#ffffff' : isDimmed ? '#47556944' : 'rgba(255, 255, 255, 0.85)'
        ctx.stroke()

        // Label / Texto do Nó
        if (showLabels || isHovered || isCenter) {
          const label = node.title.length > 28 ? node.title.slice(0, 26) + '…' : node.title
          ctx.font = isCenter ? '600 12px Inter, sans-serif' : '500 11px Inter, sans-serif'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'top'

          const textY = node.y + node.radius + 6

          // Fundo escuro sutil para legibilidade perfeita do texto
          ctx.fillStyle = 'rgba(15, 23, 42, 0.75)'
          const textWidth = ctx.measureText(label).width
          ctx.fillRect(node.x - textWidth / 2 - 4, textY - 1, textWidth + 8, 16)

          ctx.fillStyle = isDimmed ? '#64748b' : isCenter ? '#e2e8f0' : isHovered ? '#ffffff' : '#cbd5e1'
          ctx.fillText(label, node.x, textY)
        }
      })

      ctx.restore()

      animationFrameIdRef.current = requestAnimationFrame(step)
    }

    animationFrameIdRef.current = requestAnimationFrame(step)

    return () => {
      isRunning = false
      if (animationFrameIdRef.current) {
        cancelAnimationFrame(animationFrameIdRef.current)
      }
    }
  }, [edges, zoom, pan, currentMaterialId, showLabels, hoveredNode])

  // Ajusta o tamanho do Canvas à tela com suporte a DPR Retina
  useEffect(() => {
    function handleResize() {
      const canvas = canvasRef.current
      const container = containerRef.current
      if (!canvas || !container) return
      const rect = container.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [isFullscreen])

  // Converte coordenadas do mouse para coordenadas do espaço do mundo do Canvas
  function getCanvasWorldCoords(clientX: number, clientY: number): { x: number; y: number; screenX: number; screenY: number } {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0, screenX: 0, screenY: 0 }
    const rect = canvas.getBoundingClientRect()
    const screenX = clientX - rect.left
    const screenY = clientY - rect.top

    const width = canvas.width || 800
    const height = canvas.height || 500

    const worldX = (screenX - (width / 2 + pan.x)) / zoom + width / 2
    const worldY = (screenY - (height / 2 + pan.y)) / zoom + height / 2

    return { x: worldX, y: worldY, screenX, screenY }
  }

  // Interações de Mouse e Drag
  function handleMouseDown(e: React.MouseEvent<HTMLCanvasElement>) {
    const { x, y, screenX, screenY } = getCanvasWorldCoords(e.clientX, e.clientY)

    // Verifica se clicou em um nó
    const clickedNode = simNodesRef.current.find((node) => {
      const dx = node.x - x
      const dy = node.y - y
      return Math.sqrt(dx * dx + dy * dy) <= node.radius + 6
    })

    if (clickedNode) {
      draggedNodeRef.current = clickedNode
    } else {
      isPanningRef.current = true
      panStartRef.current = { x: screenX - pan.x, y: screenY - pan.y }
    }
  }

  function handleMouseMove(e: React.MouseEvent<HTMLCanvasElement>) {
    const { x, y, screenX, screenY } = getCanvasWorldCoords(e.clientX, e.clientY)
    mousePosRef.current = { x: screenX, y: screenY }

    if (draggedNodeRef.current) {
      draggedNodeRef.current.x = x
      draggedNodeRef.current.y = y
      draggedNodeRef.current.vx = 0
      draggedNodeRef.current.vy = 0
      return
    }

    if (isPanningRef.current) {
      setPan({
        x: screenX - panStartRef.current.x,
        y: screenY - panStartRef.current.y,
      })
      return
    }

    // Hover detection
    const found = simNodesRef.current.find((node) => {
      const dx = node.x - x
      const dy = node.y - y
      return Math.sqrt(dx * dx + dy * dy) <= node.radius + 6
    })

    if (found !== hoveredNode) {
      setHoveredNode(found || null)
      if (found) {
        setTooltipPos({ x: screenX, y: screenY })
      }
    }
  }

  function handleMouseUp() {
    draggedNodeRef.current = null
    isPanningRef.current = false
  }

  function handleWheel(e: React.WheelEvent<HTMLCanvasElement>) {
    e.preventDefault()
    const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89
    setZoom((prev) => Math.min(2.8, Math.max(0.4, prev * zoomFactor)))
  }

  function handleCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const { x, y } = getCanvasWorldCoords(e.clientX, e.clientY)
    const clicked = simNodesRef.current.find((node) => {
      const dx = node.x - x
      const dy = node.y - y
      return Math.sqrt(dx * dx + dy * dy) <= node.radius + 5
    })

    if (clicked && clicked.id !== currentMaterialId) {
      navigate(`/materiais/${clicked.id}`)
    }
  }

  function handleResetView() {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  return (
    <div
      ref={containerRef}
      className={`obsidian-graph-wrapper ${isFullscreen ? 'graph-fullscreen' : ''}`}
      style={{
        position: 'relative',
        width: '100%',
        height: isFullscreen ? '100vh' : '540px',
        backgroundColor: '#14161f',
        borderRadius: isFullscreen ? '0' : '12px',
        overflow: 'hidden',
        border: '1px solid #2d3748',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.45)',
        userSelect: 'none',
      }}
    >
      {/* Canvas Principal */}
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onClick={handleCanvasClick}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          cursor: draggedNodeRef.current ? 'grabbing' : hoveredNode ? 'pointer' : 'grab',
        }}
      />

      {/* Barra de Título e Controles Superiores */}
      <div
        style={{
          position: 'absolute',
          top: 14,
          left: 16,
          right: 16,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          pointerEvents: 'none',
        }}
      >
        {/* Identificador de Modo de Grafo */}
        <div
          style={{
            pointerEvents: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(8px)',
            padding: '6px 14px',
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            color: '#f8fafc',
            fontSize: '0.85rem',
            fontWeight: 500,
          }}
        >
          <span
            style={{
              width: 9,
              height: 9,
              borderRadius: '50%',
              backgroundColor: isGlobalView ? '#10b981' : '#6366f1',
              boxShadow: `0 0 8px ${isGlobalView ? '#10b981' : '#6366f1'}`,
            }}
          />
          <span>{isGlobalView ? 'Grafo Global de Conhecimento' : 'Grafo Local do Material'}</span>
          {onToggleViewMode && (
            <button
              onClick={onToggleViewMode}
              style={{
                marginLeft: '8px',
                background: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#93c5fd',
                fontSize: '0.75rem',
                padding: '2px 8px',
                borderRadius: '12px',
                cursor: 'pointer',
              }}
            >
              {isGlobalView ? 'Ver apenas este' : 'Ver todo o acervo'}
            </button>
          )}
        </div>

        {/* Barra de Ferramentas Estilo Obsidian (Zoom, Reset, Tela Cheia, Filtros) */}
        <div
          style={{
            pointerEvents: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(8px)',
            padding: '4px 8px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
          }}
        >
          {onAddConnectionClick && (
            <button
              onClick={onAddConnectionClick}
              title="Criar nova conexão entre materiais"
              style={{
                background: '#4f46e5',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 10px',
                fontSize: '0.78rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                cursor: 'pointer',
              }}
            >
              <span>+</span> Conectar
            </button>
          )}

          <button
            onClick={() => setZoom((z) => Math.min(2.8, z * 1.2))}
            title="Aumentar Zoom (+)"
            style={toolbarBtnStyle}
          >
            +
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(0.4, z * 0.8))}
            title="Diminuir Zoom (-)"
            style={toolbarBtnStyle}
          >
            −
          </button>
          <button onClick={handleResetView} title="Centralizar Visualização" style={toolbarBtnStyle}>
            ⟲
          </button>
          <button
            onClick={() => setShowLabels((prev) => !prev)}
            title={showLabels ? 'Ocultar rótulos' : 'Mostrar rótulos'}
            style={{
              ...toolbarBtnStyle,
              color: showLabels ? '#60a5fa' : '#94a3b8',
            }}
          >
            Aa
          </button>
          <button
            onClick={() => setShowSettings((prev) => !prev)}
            title="Filtros e Legenda"
            style={{
              ...toolbarBtnStyle,
              color: showSettings ? '#a855f7' : '#cbd5e1',
            }}
          >
            ⚙
          </button>
          <button
            onClick={() => setIsFullscreen((prev) => !prev)}
            title={isFullscreen ? 'Sair da tela cheia' : 'Tela cheia'}
            style={toolbarBtnStyle}
          >
            {isFullscreen ? '✕' : '⛶'}
          </button>
        </div>
      </div>

      {/* Painel Flutuante de Legenda e Filtros (Estilo Obsidian) */}
      {showSettings && (
        <div
          style={{
            position: 'absolute',
            top: 56,
            right: 16,
            width: '230px',
            background: 'rgba(15, 23, 42, 0.94)',
            backdropFilter: 'blur(12px)',
            borderRadius: '10px',
            padding: '12px 14px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            boxShadow: '0 12px 24px rgba(0, 0, 0, 0.6)',
            color: '#e2e8f0',
            fontSize: '0.8rem',
            zIndex: 10,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: '8px', color: '#f8fafc', fontSize: '0.85rem' }}>
            Legenda do Grafo
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {Object.entries(RELATION_COLORS).map(([key, val]) => (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    backgroundColor: val.color,
                    boxShadow: `0 0 6px ${val.color}`,
                  }}
                />
                <span style={{ color: '#cbd5e1' }}>{val.label}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '10px', borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: '8px' }}>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              💡 Dica: Arraste nós com o mouse para reorganizar. Dê scroll para zoom.
            </span>
          </div>
        </div>
      )}

      {/* Tooltip Flutuante de Hover (Obsidian Card Preview) */}
      {hoveredNode && (
        <div
          style={{
            position: 'absolute',
            left: Math.min(window.innerWidth - 240, tooltipPos.x + 14),
            top: Math.max(10, tooltipPos.y - 45),
            background: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(10px)',
            border: `1px solid ${hoveredNode.baseColor}`,
            boxShadow: `0 8px 24px rgba(0, 0, 0, 0.6), 0 0 12px ${hoveredNode.baseColor}44`,
            borderRadius: '8px',
            padding: '10px 14px',
            pointerEvents: 'none',
            maxWidth: '280px',
            zIndex: 20,
            color: '#f8fafc',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: hoveredNode.baseColor,
              }}
            />
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                color: hoveredNode.baseColor,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}
            >
              {hoveredNode.id === currentMaterialId
                ? 'Material Atual'
                : hoveredNode.relationType
                ? RELATION_COLORS[hoveredNode.relationType]?.label || hoveredNode.relationType
                : 'Material do Acervo'}
            </span>
          </div>

          <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#ffffff', lineHeight: 1.3 }}>
            {hoveredNode.title}
          </div>

          {hoveredNode.note && (
            <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '6px', fontStyle: 'italic' }}>
              "{hoveredNode.note}"
            </div>
          )}

          <div
            style={{
              fontSize: '0.72rem',
              color: '#94a3b8',
              marginTop: '6px',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              paddingTop: '4px',
            }}
          >
            {hoveredNode.id === currentMaterialId ? 'Material central aberto' : '👉 Clique para abrir este material'}
          </div>
        </div>
      )}

      {/* Legenda Resumida no Rodapé */}
      <div
        style={{
          position: 'absolute',
          bottom: 12,
          left: 16,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(6px)',
          padding: '4px 12px',
          borderRadius: '16px',
          fontSize: '0.72rem',
          color: '#94a3b8',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          pointerEvents: 'none',
        }}
      >
        <span>Arraste os nós livremente</span>
        <span>•</span>
        <span>Scroll para Zoom</span>
        <span>•</span>
        <span>Clique no nó para navegar</span>
      </div>
    </div>
  )
}

const toolbarBtnStyle: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  color: '#cbd5e1',
  width: '28px',
  height: '28px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '0.9rem',
  fontWeight: 600,
  transition: 'background 0.15s',
}
