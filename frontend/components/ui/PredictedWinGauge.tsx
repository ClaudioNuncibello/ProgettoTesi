import React, { useMemo } from "react"

interface PredictedWinGaugeProps {
  value: number           // da 0 (solo casa) a 1 (solo ospiti)
  size?: number           // diametro (default 240)
  strokeWidth?: number    // spessore semicerchio (default 24)
  homeColor?: string      // colore riempimento (Casa)
  awayColor?: string      // colore sfondo (Ospiti)
  needleColor?: string    // colore lancetta
  homeName: string
  awayName: string
  title?: string
}

export default function PredictedWinGauge({
  value,
  size = 240,
  strokeWidth = 24,
  homeColor = "#1E3A8A",
  awayColor = "#2563EB",
  needleColor = "#FFFFFF",
  homeName,
  awayName,
  title = "Predicted Win",
}: PredictedWinGaugeProps) {
  const r = (size - strokeWidth) / 2
  const cx = size / 2
  const cy = size / 2
  const semiCirc = Math.PI * r

  // 1) path per semicerchio superiore
  const pathD = useMemo(
    () => `M ${cx - r},${cy} A ${r},${r} 0 0,1 ${cx + r},${cy}`,
    [cx, cy, r]
  )

  // 2) calcolo angolo e pivot (se servisse in futuro per lancetta)
  const angleDeg = useMemo(() => -90 + value * 180, [value])
  const angleRad = (angleDeg * Math.PI) / 180
  const pivotX = cx + r * Math.cos(angleRad)
  const pivotY = cy + r * Math.sin(angleRad)

  // (triangolo punta non usato in questa versione)

  return (
    <div
      className="relative flex flex-col items-center p-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl shadow-lg"
      style={{ width: size + 32 }}
    >
      {/* Titolo */}
      <h3 className="text-center text-lg font-semibold text-white mb-4">
        {title}
      </h3>

      {/* SVG gauge */}
      <svg
        width={size}
        height={size / 2 + strokeWidth + 40}
        viewBox={`0 0 ${size} ${size / 2 + strokeWidth + 40}`}
        className="block"
      >
        {/* Semicerchio sfondo */}
        <path
          d={pathD}
          fill="none"
          stroke={awayColor}
          strokeWidth={strokeWidth}
          strokeLinecap="butt"
        />

        {/* Semicerchio “riempito” */}
        <path
          d={pathD}
          fill="none"
          stroke={homeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="butt"
          strokeDasharray={`${value * semiCirc} ${semiCirc}`}
        />
      </svg>

      {/* Badge percentuali e nomi, centrati */}
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 translate-y-8 flex gap-4">
        {/* Casa */}
        <div
          className="flex flex-col items-center px-4 py-2 rounded-lg shadow-lg"
          style={{ backgroundColor: homeColor }}
        >
          <span className="text-white font-semibold text-base">
            {(value * 100).toFixed(1)}%
          </span>
          <span className="text-white text-xs">{homeName}</span>
        </div>
        {/* Ospiti */}
        <div
          className="flex flex-col items-center px-4 py-2 rounded-lg shadow-lg"
          style={{ backgroundColor: awayColor }}
        >
          <span className="text-white font-semibold text-base">
            {((1 - value) * 100).toFixed(1)}%
          </span>
          <span className="text-white text-xs">{awayName}</span>
        </div>
      </div>
    </div>
  )
}
