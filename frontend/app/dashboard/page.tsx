"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { Star, RefreshCw } from "lucide-react"

const API_KEY = "2SRC4Sh4lkukveijWwruFw"
const MATCHES_URL = "https://volleyball.sportdevs.com/matches?status_type=eq.live"
const DETAIL_URL = (matchId: number) => `http://localhost:8000/match/${matchId}`

// --- Tipo per i soli match SportDevs (colonna di sinistra) ---
interface SportDevMatch {
  id: number
  name: string
  tournament_name : string
  start_time: string
}

// --- Unica interfaccia per i dettagli (colonna di destra) ---
interface DetailedMatch {
  match_id: number
  home_team_id: number
  away_team_id: number
  home_score_total: number
  away_score_total: number
  home_sets_won: number
  away_sets_won: number
  score_diff: number
  set_diff: number
  home_current_score: string
  away_current_score: string
  set_info: string
  game_duration: string
  match_status: string
  home_win_rate_last5: number
  away_win_rate_last5: number
  head_to_head_win_rate_home: number
  predicted_win: number
}

// --- Dati di fallback per la colonna di sinistra ---
const testSportDevMatches: SportDevMatch[] = [
  { id: 100006, name: "Italy vs France", start_time: "2025-06-03T15:30:00Z", tournament_name:"VNL woman"},
  { id: 100002, name: "Brazil vs Argentina", start_time: "2025-06-03T16:00:00Z", tournament_name:"VNL woman" },
  { id: 100003, name: "USA vs Poland", start_time: "2025-06-03T16:30:00Z", tournament_name:"VNL woman" },
]

export default function Dashboard() {
  // Stato per la colonna sinistra
  const [matches, setMatches] = useState<SportDevMatch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Stato per la colonna di destra
  const [favoriteMatches, setFavoriteMatches] = useState<number[]>([])
  const [animatingMatch, setAnimatingMatch] = useState<number | null>(null)
  const [detailedMatches, setDetailedMatches] = useState<Record<number, DetailedMatch>>({})
  const scrollRef = useRef<HTMLDivElement>(null)

  // --- Fetch fallback per la lista SportDevs (colonna sinistra) ---
  async function fetchMatchesDev() {
    setError(null)
    setLoading(true)
    try {
      await new Promise((r) => setTimeout(r, 500))
      setMatches(testSportDevMatches)
    } catch {
      setMatches(testSportDevMatches)
    } finally {
      setLoading(false)
    }
  }

  // --- Fetch “Prod” per la lista SportDevs (colonna di sinistra) ---
  async function fetchMatchesProd() {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(MATCHES_URL, {
        headers: { Authorization: `Bearer ${API_KEY}` },
      })
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data: any[] = await res.json()
      const minimal: SportDevMatch[] = data.map((m) => ({
        id: m.id,
        name: m.name,
        start_time: m.start_time,
        tournament_name : m.tournament_name,
      }))
      setMatches(minimal)
    } catch (err) {
      console.error("Errore fetch SportDevs:", err)
      setError("Errore nella richiesta API SportDevs")
    } finally {
      setLoading(false)
    }
  }

  // ==== SCEGLI QUALE USARE per la colonna sinistra ====
  //const fetchMatches = fetchMatchesDev
  const fetchMatches = fetchMatchesProd

  // --- Fetch “Prod” per i dettagli (colonna di destra) ---
  async function fetchMatchDetails(matchId: number) {
    try {
      const res = await fetch(DETAIL_URL(matchId))
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data: DetailedMatch = await res.json()
      setDetailedMatches((prev) => ({
        ...prev,
        [matchId]: data,
      }))
    } catch {
      // Gestione errori silenziosa per dettagli
    }
  }

  useEffect(() => {
    fetchMatches()
  }, [])

  useEffect(() => {
    const intervall = setInterval(() => {
      Object.keys(detailedMatches).forEach((key) => {
        fetchMatchDetails(Number(key))
      })
    }, 10000)
    return () => clearInterval(intervall)
  }, [detailedMatches])

  // Formatta data/ora in italiano per data inizio
  const formatMatchDate = (dateString?: string) =>
    dateString
      ? new Date(dateString).toLocaleString("it-IT", {
          day: "numeric",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })
      : "Data non disponibile"

  const getMatchStatus = () => "IN CORSO"
  const getStatusColor = () => "text-volleyball-orange"

  const toggleFavorite = (id: number) => {
    const isAdding = !favoriteMatches.includes(id)
    if (isAdding) {
      setAnimatingMatch(id)
      fetchMatchDetails(id)
      setTimeout(() => setAnimatingMatch(null), 800)
    }
    setFavoriteMatches((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  const sortedMatches = [...matches].sort((a, b) => {
    const aFav = favoriteMatches.includes(a.id)
    const bFav = favoriteMatches.includes(b.id)
    if (aFav && !bFav) return -1
    if (!aFav && bFav) return 1
    return 0
  })

  const selected = matches.filter((m) => favoriteMatches.includes(m.id))

  useEffect(() => {
    if (animatingMatch && scrollRef.current) {
      scrollRef.current.scrollTop = 0
    }
  }, [animatingMatch])

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Navbar fissa */}
      <nav className="flex-shrink-0 sticky top-0 z-50 w-full backdrop-blur-lg bg-background/80 border-b border-border shadow-sm">
        <div className="flex items-center justify-between w-full px-6 py-4">
          <Link href="/" className="text-xl font-heading font-bold text-primary">
            VolleyApi
          </Link>
          <div className="flex space-x-6">
            <Link href="/" className="nav-link">
              Home
            </Link>
            <Link href="https://github.com/ClaudioNuncibello/ProgettoTesi" className="nav-link">
              GitHub
            </Link>
            <Link href="/dashboard" className="nav-link active">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Contenuto principale con layout a due colonne */}
      <main className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Colonna sinistra */}
        <div className="md:w-1/4 h-full flex flex-col border-r border-border bg-card">
          <div className="flex-shrink-0 p-4 sticky top-0 bg-card z-10 border-b border-border flex justify-between items-center">
            <h2 className="text-xl font-heading font-bold text-foreground">Match disponibili</h2>
            <button
              onClick={fetchMatches}
              className="p-2 rounded-full hover:bg-primary/10 text-primary transition-colors"
              aria-label="Aggiorna match"
              disabled={loading}
            >
              <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2">
            {loading ? (
              <div className="py-4 px-2 animate-pulse space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-12 bg-muted rounded-lg" />
                ))}
              </div>
            ) : error ? (
              <div className="p-4 text-center text-red-500 font-medium">{error}</div>
            ) : matches.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">Nessuna partita in corso</div>
            ) : (
              sortedMatches.map((match) => (
                <div
                  key={match.id}
                  className={`
                    flex items-center justify-between rounded-lg border border-border p-3
                    hover:bg-primary/5 transition-all duration-500
                    ${animatingMatch === match.id ? "animate-favorite-added" : ""}
                    ${favoriteMatches.includes(match.id) ? "bg-primary/5 border-primary/20" : ""}
                  `}
                >
                  <div className="flex items-center">
                    <button
                      onClick={() => toggleFavorite(match.id)}
                      aria-label={
                        favoriteMatches.includes(match.id)
                          ? `Rimuovi ${match.name} dai preferiti`
                          : `Aggiungi ${match.name} ai preferiti`
                      }
                      className="mr-3 focus:outline-none"
                    >
                      <Star
                        className={`
                          h-5 w-5 ${
                            favoriteMatches.includes(match.id)
                              ? "fill-volleyball-orange text-volleyball-orange"
                              : "text-muted-foreground"
                          } transition-colors
                        `}
                      />
                    </button>
                    <div>
                      <p className="text-sm font-medium">{match.name}</p>
                      <p className="text-xs flex items-center gap-1.5">
                        <span className={`font-medium ${getStatusColor()}`}>{getMatchStatus()}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">
                          {formatMatchDate(match.start_time)}
                        </span>
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Colonna di destra */}
        <div className="md:w-3/4 h-full flex flex-col bg-background">
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 h-full">
              {selected.length > 0 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-heading font-bold text-foreground mb-4">
                    I tuoi match preferiti
                  </h2>

                  {selected.map((match) => {
                    const detailed = detailedMatches[match.id]
                    const [homeName = "Casa", awayName = "Ospiti"] = match.name.split(" vs ")

                    // Calcolo setArr, gridColsClass, scores e currentSetIndex
                    const setsArr = detailed?.set_info.split(" | ") || []
                    const totalSets = setsArr.length
                    const gridColsMap: Record<number, string> = {
                      2: "grid-cols-2",
                      3: "grid-cols-3",
                      4: "grid-cols-4",
                      5: "grid-cols-5",
                      6: "grid-cols-6",
                    }
                    const colsKey = totalSets + 1 // 1 colonna “Squadra” + totalSets per i set
                    const gridColsClass = gridColsMap[colsKey] || "grid-cols-2"
                    const scores = setsArr.map((entry) => {
                      const parts = entry.split(":")[1].trim().split("-")
                      return { home: parseInt(parts[0], 10), away: parseInt(parts[1], 10) }
                    })
                    const currentSetIndex = totalSets - 1

                    return (
                      <div
                        key={match.id}
                        className="w-full border border-border rounded-xl bg-card p-6 shadow-sm hover:shadow-md transition-shadow"
                      >
                        {/* Titolo e stato */}
                        <div className="flex justify-between items-start mb-4">
                          <h3 className="text-xl font-bold font-heading">{match.name}</h3>
                          <span
                            className="px-3 py-1 rounded-full text-xs font-medium bg-volleyball-orange/10 text-volleyball-orange"
                          >
                            {getMatchStatus()}
                          </span>
                        </div>

                        {/* Info base */}
                        <div className="text-sm text-muted-foreground mb-6 space-y-1">
                          <p>
                            Torneo: <span className="text-foreground"> {match.tournament_name} </span>
                          </p>
                          <p>
                            inizio partita:{" "}
                            <span className="text-foreground">
                              {formatMatchDate(match.start_time)}
                            </span>
                          </p>
                        </div>

                        {/* ─────────────────────────────────────────────────────────────── */}
                        {/* Mostra tabella + 2 barre (Forma ultimi 5 + Head-to-Head) solo se 'detailed' è definito */}
                        {detailed ? (
                          <>
                            {/* ─── 1) Flex container: Tabella (a sinistra) + Metriche (a destra) ─── */}
                            <div className="flex gap-16 items-start">
                              {/* ───────────────────────── Tabella ───────────────────────── */}
                              <div className="flex-none w-1/3 bg-white rounded-lg overflow-hidden shadow-lg">
                                {/* Header tabella */}
                                <div
                                  className={`
                                    grid ${gridColsClass} bg-gray-100 text-gray-700 text-xs font-semibold
                                    border-b border-border
                                  `}
                                >
                                  <div className="py-2 px-2 text-center">Squadra</div>
                                  {setsArr.map((_, idx) => {
                                    const isCurrent = idx === currentSetIndex
                                    return (
                                      <div
                                        key={idx}
                                        className={`
                                          py-2 px-2 text-center
                                          ${isCurrent ? "text-volleyball-orange" : ""}
                                        `}
                                      >
                                        {isCurrent ? "Set corrente" : `Set ${idx + 1}`}
                                        {isCurrent && <span className="ml-1">●</span>}
                                      </div>
                                    )
                                  })}
                                </div>
                                {/* Corpo tabella */}
                                <div className="divide-y divide-border">
                                  {/* Riga squadra “Casa” */}
                                  <div className={`grid ${gridColsClass} bg-white`}>
                                    <div className="py-2 px-2 font-medium text-sm truncate text-center">
                                      {homeName}
                                    </div>
                                    {scores.map((s, idx) => {
                                      const won = s.home > s.away
                                      const isCurrent = idx === currentSetIndex
                                      return (
                                        <div
                                          key={idx}
                                          className={`
                                            py-2 px-2 text-center text-sm font-bold
                                            ${won ? "text-green-600" : "text-gray-800"}
                                            ${isCurrent ? "text-volleyball-orange" : ""}
                                          `}
                                        >
                                          {s.home}
                                        </div>
                                      )
                                    })}
                                  </div>
                                  {/* Riga squadra “Ospiti” */}
                                  <div className={`grid ${gridColsClass} bg-white`}>
                                    <div className="py-2 px-2 font-medium text-sm truncate text-center">
                                      {awayName}
                                    </div>
                                    {scores.map((s, idx) => {
                                      const won = s.away > s.home
                                      const isCurrent = idx === currentSetIndex
                                      return (
                                        <div
                                          key={idx}
                                          className={`
                                            py-2 px-2 text-center text-sm font-bold
                                            ${won ? "text-green-600" : "text-gray-800"}
                                            ${isCurrent ? "text-volleyball-orange" : ""}
                                          `}
                                        >
                                          {s.away}
                                        </div>
                                      )
                                    })}
                                  </div>
                                </div>
                              </div>

                              {/* ─── 2) Colonna di destra: Forma ultimi 5 & Head-to-Head ─── */}
                              <div className="flex-1 mt-0 space-y-6">
                                {/* ── 2.1) Blocco “Forma ultimi 5” ── */}
                                <div className="inline-grid grid-cols-2 gap-10">
                                  {/* Home (ultimi 5) */}
                                  <div className="space-y-1">
                                    <span className="block text-sm font-medium text-[#0A1931]">
                                      Home (ultimi 5)
                                    </span>
                                    <div className="flex items-center gap-1">
                                      {Array.from({ length: 5 }).map((_, idx) => {
                                        const winsCount = Math.round(detailed.home_win_rate_last5 * 5)
                                        const isWin = idx < winsCount
                                        return (
                                          <div
                                            key={idx}
                                            className={`
                                              w-6 h-6 rounded-md flex items-center justify-center
                                              text-xs font-semibold text-white
                                              ${isWin ? "bg-green-600" : "bg-red-600"}
                                            `}
                                          >
                                            {isWin ? "V" : "P"}
                                          </div>
                                        )
                                      })}
                                    </div>
                                  </div>

                                  {/* Away (ultimi 5) */}
                                  <div className="space-y-1">
                                    <span className="block text-sm font-medium text-[#0A1931]">
                                      Away (ultimi 5)
                                    </span>
                                    <div className="flex items-center gap-1">
                                      {Array.from({ length: 5 }).map((_, idx) => {
                                        const winsCount = Math.round(detailed.away_win_rate_last5 * 5)
                                        const isWin = idx < winsCount
                                        return (
                                          <div
                                            key={idx}
                                            className={`
                                              w-6 h-6 rounded-md flex items-center justify-center
                                              text-xs font-semibold text-white
                                              ${isWin ? "bg-green-600" : "bg-red-600"}
                                            `}
                                          >
                                            {isWin ? "V" : "P"}
                                          </div>
                                        )
                                      })}
                                    </div>
                                  </div>
                                </div>

                                {/* ── 2.2) Head-to-Head Win Rate ── */}
                                <div className=" w-1/2 space-y-1">
                                  <span className="block text-sm font-medium text-[#0A1931]">
                                    Head-to-Head Win Rate
                                  </span>
                                  <div className="w-full h-3 flex rounded-full overflow-hidden bg-gray-200">
                                    <div
                                      className="h-full"
                                      style={{
                                        width: `${detailed.head_to_head_win_rate_home * 100}%`,
                                        backgroundColor: "#22C55E",
                                      }}
                                    />
                                    <div
                                      className="h-full"
                                      style={{
                                        width: `${(1 - detailed.head_to_head_win_rate_home) * 100}%`,
                                        backgroundColor: "#EF4444",
                                      }}
                                    />
                                  </div>
                                  <div className="flex justify-between text-xs text-[#0A1931]">
                                    <span>
                                      Casa{" "}
                                      {(detailed.head_to_head_win_rate_home * 100).toFixed(1)}%
                                    </span>
                                    <span>
                                      Ospiti{" "}
                                      {((1 - detailed.head_to_head_win_rate_home) * 100).toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* ─────────────────────────────────────────────────────────────── */}
                            {/* ─── 3) Predicted Win (sotto il flex container) ─── */}
                            <div className="mt-6">
                              <div className="w-full space-y-1">
                                <span className="block text-sm font-medium text-[#0A1931]">
                                  Predicted Win
                                </span>
                                <div className="w-full h-3 flex rounded-full overflow-hidden bg-gray-200">
                                  <div
                                    className="h-full"
                                    style={{
                                      width: `${detailed.predicted_win * 100}%`,
                                      backgroundColor: "#F55353",
                                    }}
                                  />
                                  <div
                                    className="h-full"
                                    style={{
                                      width: `${(1 - detailed.predicted_win) * 100}%`,
                                      backgroundColor: "#FFA500",
                                    }}
                                  />
                                </div>
                                <div className="flex justify-between text-xs text-[#0A1931]">
                                  <span>
                                    Casa {(detailed.predicted_win * 100).toFixed(1)}%
                                  </span>
                                  <span>
                                    Ospiti{" "}
                                    {((1 - detailed.predicted_win) * 100).toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="text-center text-sm text-gray-500">
                            Caricamento dettagli…
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full">
                  <h1 className="text-4xl font-bold text-foreground font-heading mb-4">
                    Segui i tuoi match
                  </h1>
                  <p className="text-muted-foreground text-center max-w-md">
                    Seleziona i tuoi match preferiti dalla lista a sinistra per visualizzarli qui.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
