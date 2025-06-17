"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { Star, RefreshCw, ChevronDown, ChevronUp } from "lucide-react"
import PredictedWinGauge from "@/components/ui/PredictedWinGauge"
import MatchSelect from "@/components/ui/MatchSelect";

const API_KEY = "2SRC4Sh4lkukveijWwruFw"
const MATCHES_URL = "https://volleyball.sportdevs.com/matches?status_type=eq.live"
const DETAIL_URL = (matchId: number) => `http://localhost:8000/match/${matchId}`

// --- Tipo per i soli match SportDevs (colonna di sinistra) ---
interface SportDevMatch {
  id: number
  name: string
  tournament_name: string
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
  { id: 100006, name: "Italy vs France", start_time: "2025-06-03T15:30:00Z", tournament_name: "VNL woman" },
  { id: 100002, name: "Brazil vs Argentina", start_time: "2025-06-03T16:00:00Z", tournament_name: "VNL woman" },
  { id: 100003, name: "USA vs Poland", start_time: "2025-06-03T16:30:00Z", tournament_name: "VNL woman" },
]

// --- Dati di fallback per i dettagli dei match (colonna di destra) ---
const testDetailedMatches: Record<number, DetailedMatch> = {
  100006: {
    match_id: 100006,
    home_team_id: 1,
    away_team_id: 2,
    home_score_total: 45,
    away_score_total: 40,
    home_sets_won: 2,
    away_sets_won: 1,
    score_diff: 5,
    set_diff: 1,
    home_current_score: "15",
    away_current_score: "12",
    set_info: "Set 1:15-12 | Set 2:10-15 | Set 3:20-18",
    game_duration: "1h 05m",
    match_status: "live",
    home_win_rate_last5: 0.6,
    away_win_rate_last5: 0.4,
    head_to_head_win_rate_home: 0.3,
    predicted_win: 0.366,
  },
  100002: {
    match_id: 100002,
    home_team_id: 3,
    away_team_id: 4,
    home_score_total: 30,
    away_score_total: 32,
    home_sets_won: 1,
    away_sets_won: 2,
    score_diff: -2,
    set_diff: -1,
    home_current_score: "12",
    away_current_score: "15",
    set_info: "Set 1:12-15 | Set 2:15-10 | Set 3:8-15",
    game_duration: "50m",
    match_status: "live",
    home_win_rate_last5: 0.8,
    away_win_rate_last5: 0.2,
    head_to_head_win_rate_home: 0.0,
    predicted_win: 0.342,
  },
  100003: {
    match_id: 100003,
    home_team_id: 5,
    away_team_id: 6,
    home_score_total: 50,
    away_score_total: 48,
    home_sets_won: 3,
    away_sets_won: 2,
    score_diff: 2,
    set_diff: 1,
    home_current_score: "20",
    away_current_score: "18",
    set_info: "Set 1:25-20 | Set 2:20-25 | Set 3:25-23 | Set 4:22-25 | Set 5:20-18",
    game_duration: "1h 20m",
    match_status: "live",
    home_win_rate_last5: 0.7,
    away_win_rate_last5: 0.3,
    head_to_head_win_rate_home: 0.5,
    predicted_win: 0.75,
  },
}

export default function Dashboard() {
  // Stato per la select
  const [showSelect, setShowSelect] = useState(false)

  // Stato per la colonna sinistra
  const [matches, setMatches] = useState<SportDevMatch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Stato per la colonna di destra
  const [favoriteMatches, setFavoriteMatches] = useState<number[]>([])
  const [detailedMatches, setDetailedMatches] = useState<Record<number, DetailedMatch>>({})
  const [activeFavorite, setActiveFavorite] = useState<number | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Fetch fallback per la lista SportDevs (colonna sinistra)
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

  // --- Fetch “Prod” per la lista SportDevs (colonna di sinistra) ---More actions
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

  // Fetch fallback per i dettagli (colonna di destra)
  async function fetchMatchDetailsDev(matchId: number) {
    try {
      const res = await fetch(DETAIL_URL(matchId))
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data: DetailedMatch = await res.json()
      setDetailedMatches((prev) => ({ ...prev, [matchId]: data }))
    } catch {
      // Usa fallback
      setDetailedMatches((prev) => ({ ...prev, [matchId]: testDetailedMatches[matchId] || prev[matchId] }))
    }
  }

  // --- Fetch “Prod” per i dettagli (colonna di destra) ---Add commentMore actions
  async function fetchMatchDetailsProd(matchId: number) {
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

  // Scegli quale fetch usare
  const fetchMatches = fetchMatchesDev
  const fetchMatchDetails = fetchMatchDetailsDev
  //const fetchMatches = fetchMatchesProd
  //const fetchMatchDetails = fetchMatchDetailsProd

  useEffect(() => {
    fetchMatches()
  }, [])

  // Aggiorna dettagli periodicamente
  useEffect(() => {
    const intervall = setInterval(() => {
      Object.keys(detailedMatches).forEach((key) => {
        fetchMatchDetails(Number(key))
      })
    }, 10000)
    return () => clearInterval(intervall)
  }, [detailedMatches])

  // Sincronizza activeFavorite con favoriteMatches
  useEffect(() => {
    if (favoriteMatches.length > 0 && !favoriteMatches.includes(activeFavorite!)) {
      setActiveFavorite(favoriteMatches[0])
      fetchMatchDetails(favoriteMatches[0])
    } else if (favoriteMatches.length === 0) {
      setActiveFavorite(null)
    }
  }, [favoriteMatches])

  const toggleFavorite = (id: number) => {
    const isAdding = !favoriteMatches.includes(id)
    if (isAdding) fetchMatchDetails(id)
    setFavoriteMatches((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

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

  const sortedMatches = [...matches].sort((a, b) => {
    const aFav = favoriteMatches.includes(a.id)
    const bFav = favoriteMatches.includes(b.id)
    if (aFav && !bFav) return -1
    if (!aFav && bFav) return 1
    return 0
  })

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Navbar */}
      <nav className="flex-shrink-0 sticky top-0 z-50 w-full backdrop-blur-lg bg-background/80 border-b border-border shadow-sm">
        <div className="flex items-center justify-between w-full px-6 py-4">
          <Link href="/" className="text-xl font-heading font-bold text-primary">
            VolleyApi
          </Link>
          <div className="flex space-x-6">
            <Link href="/" className="nav-link">Home</Link>
            <Link href="https://github.com/ClaudioNuncibello/ProgettoTesi" className="nav-link">GitHub</Link>
            <Link href="/dashboard" className="nav-link active">Dashboard</Link>
          </div>
        </div>
      </nav>
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
                  <div key={i} className="h-12:bg-muted rounded-lg" />
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
                  className={`flex items-center justify-between rounded-lg border border-border p-3 hover:bg-primary/5 transition-all duration-500 ${favoriteMatches.includes(match.id) ? "bg-primary/5 border-primary/20" : ""}`}
                >
                  <div className="flex items-center">
                    <button
                      onClick={() => toggleFavorite(match.id)}
                      aria-label={favoriteMatches.includes(match.id)
                        ? `Rimuovi ${match.name} dai preferiti`
                        : `Aggiungi ${match.name} ai preferiti`}
                      className="mr-3 focus:outline-none"
                    >
                      <Star
                        className={`h-5 w-5 ${favoriteMatches.includes(match.id)
                          ? "fill-volleyball-orange text-volleyball-orange"
                          : "text-muted-foreground"} transition-colors`} />
                    </button>
                    <div>
                      <p className="text-sm font-medium">{match.name}</p>
                      <p className="text-xs flex items-center gap-1.5">
                        <span className={`font-medium ${getStatusColor()}`}>{getMatchStatus()}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{formatMatchDate(match.start_time)}</span>
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
       {/* Colonna destra */}
        <div className="md:w-3/4 h-full flex flex-col bg-background">
          <div className="flex-1 overflow-y-auto">
            <div className="p-6 h-full">
              {favoriteMatches.length > 0 ? (
                <div className="space-y-6">
                  <div className="mb-4">
                  <MatchSelect
                    matches={favoriteMatches.map((id) => matches.find((m) => m.id === id)!)}
                    activeFavorite={activeFavorite}
                    onChange={(id) => {
                      setActiveFavorite(id);
                      fetchMatchDetails(id);
                    }}
                  />
                  </div>
                  {activeFavorite !== null && detailedMatches[activeFavorite] ? (
                    <MatchCard
                      match={matches.find((m) => m.id === activeFavorite)!}
                      detailed={detailedMatches[activeFavorite]}
                    />
                  ) : (
                    <p className="text-center text-sm text-gray-500">Caricamento dettagli…</p>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full">
                  <h1 className="text-4xl font-bold text-foreground font-heading mb-4">Segui i tuoi match</h1>
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

function MatchCard({ match, detailed }: { match: SportDevMatch; detailed: DetailedMatch }) {
  const [homeName = "Casa", awayName = "Ospiti"] = match.name.split(" vs ")
  const setsArr = detailed.set_info.split(" | ")
  const totalSets = setsArr.length
  const gridColsMap: Record<number, string> = { 2: "grid-cols-2", 3: "grid-cols-3", 4: "grid-cols-4", 5: "grid-cols-5", 6: "grid-cols-6" }
  const colsKey = totalSets + 1
  const gridColsClass = gridColsMap[colsKey] || "grid-cols-2"
  const scores = setsArr.map((entry) => {
    const parts = entry.split(":")[1].trim().split("-")
    return { home: parseInt(parts[0], 10), away: parseInt(parts[1], 10) }
  })

  return (
    <div className="relative w-full h-[650px] border border-border rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Sfondo campo */}
      <div className="absolute inset-0 bg-center bg-no-repeat bg-cover" style={{ backgroundImage: "url('/campoPallavolo.png')" }} />

      {/* Tabellone TV */}
      <div className="absolute top-4 left-4 bg-white/80 backdrop-blur-sm rounded-lg p-3 shadow">
        <div className={`grid ${gridColsClass} gap-2 text-xs font-semibold text-gray-700`}>
          <div className="py-1 px-2 text-center font-medium">HOME</div>
          {scores.map((_, idx) => (
            <div key={idx} className="py-1 px-2 text-center">Set {idx + 1}</div>
          ))}
        </div>
        <div className={`grid ${gridColsClass} gap-2 text-sm font-bold text-center border-t border-border mt-1`}>
          <div className="py-1 px-2 font-medium truncate">{homeName}</div>
          {scores.map((s, idx) => (
            <div key={idx} className={s.home > s.away ? "text-green-600" : "text-gray-800"}>{s.home}</div>
          ))}
        </div>
        <div className={`grid ${gridColsClass} gap-2 text-sm font-bold text-center`}>
          <div className="py-1 px-2 font-medium truncate">{awayName}</div>
          {scores.map((s, idx) => (
            <div key={idx} className={s.away > s.home ? "text-green-600" : "text-gray-800"}>{s.away}</div>
          ))}
        </div>
        <div className="mt-2 text-[10px] text-gray-600">
          <div>
            Torneo: <span className="font-medium text-gray-800">{match.tournament_name}</span>
          </div>
          <div>
            Inizio: <span className="font-medium text-gray-800">{new Date(match.start_time).toLocaleString("it-IT", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
          </div>
        </div>
      </div>

      {/* Stato match */}
      <span className="absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-medium bg-volleyball-orange/10 text-volleyball-orange">IN CORSO</span>

      {/* Home ultimi 5 */}
      <div className="absolute bottom-4 left-4 bg-white/80 backdrop-blur-sm rounded-lg p-3 shadow">
        <span className="block text-sm font-medium text-[#0A1931]">Win score last 5 ({homeName})</span>
        <div className="flex items-center gap-1 mt-1">
          {Array.from({ length: 5 }).map((_, idx) => {
            const wins = Math.round(detailed.home_win_rate_last5 * 5)
            const win = idx < wins
            return (
              <div key={idx} className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-semibold text-white ${win ? "bg-green-600" : "bg-red-600"}`}>{win ? "V" : "P"}</div>
            )
          })}
        </div>
      </div>

      {/* Away ultimi 5 */}
      <div className="absolute bottom-4 right-4 bg-white/80 backdrop-blur-sm rounded-lg p-3 shadow">
        <span className="block text-sm font-medium text-[#0A1931]">Win score last 5 ({awayName})</span>
        <div className="flex items-center gap-1 mt-1">
          {Array.from({ length: 5 }).map((_, idx) => {
            const wins = Math.round(detailed.away_win_rate_last5 * 5)
            const win = idx < wins
            return (
              <div key={idx} className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-semibold text-white ${win ? "bg-green-600" : "bg-red-600"}`}>{win ? "V" : "P"}</div>
            )
          })}
        </div>
      </div>

      {/* Head-to-Head */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-1/3 bg-white/80 backdrop-blur-sm rounded-lg p-3 shadow">
        <span className="block text-sm font-medium text-[#0A1931]">Head-to-Head Win Rate</span>
        <div className="w-full h-3 flex rounded-full overflow-hidden bg-gray-200 mt-1">
          <div className="h-full" style={{ width: `${detailed.head_to_head_win_rate_home * 100}%`, backgroundColor: "#1E3A8A" }} />
          <div className="h-full" style={{ width: `${(1 - detailed.head_to_head_win_rate_home) * 100}%`, backgroundColor: "#2563EB" }} />
        </div>
        <div className="flex justify-between text-xs text-[#0A1931] mt-1">
          <span>{homeName} {(detailed.head_to_head_win_rate_home * 100).toFixed(1)}%</span>
          <span>{awayName} {((1 - detailed.head_to_head_win_rate_home) * 100).toFixed(1)}%</span>
        </div>
      </div>

      {/* Predicted Win */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
        <PredictedWinGauge
          value={detailed.predicted_win}
          homeName={homeName}
          awayName={awayName}
          size={300}
          strokeWidth={28}
        />
      </div>
    </div>
  )
}