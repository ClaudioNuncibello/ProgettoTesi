"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Star, RefreshCw } from "lucide-react"

const API_KEY = "AymenURP9kWkgEatcBdcYA"
const MATCHES_URL = "https://volleyball.sportdevs.com/matches?season_id=eq.17700"

// --- Tipi ---
interface MatchScore {
  current: number
  display: number
  period_1?: number
  period_2?: number
  period_3?: number
  period_4?: number
  period_5?: number
  penalties?: number
  default_time?: number
}

interface MatchStatus {
  type: string
  reason?: string
}

interface RawMatch {
  id: number
  name: string
  tournament_name?: string
  status: MatchStatus
  status_type: string
  home_team_name: string
  away_team_name: string
  home_team_hash_image?: string
  away_team_hash_image?: string
  home_team_score: MatchScore
  away_team_score: MatchScore
  start_time: string
  specific_start_time?: string
  times?: { specific_start_time: string }
}

interface Match {
  id: number
  name: string
  tournament_name: string
  status: MatchStatus
  status_type: string
  home_team_name: string
  away_team_name: string
  home_team_hash_image?: string
  away_team_hash_image?: string
  home_team_score: MatchScore
  away_team_score: MatchScore
  start_time: string
  specific_start_time?: string
  isLive: boolean
}

// Dati di fallback migliorati
// Tutte le partite sono "inprogress" con punteggi live coerenti
const fallbackMatches: Match[] = [
  {
    id: 1,
    name: "Italy vs France",
    tournament_name: "European Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Italy",
    away_team_name: "France",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 25,
      period_2: 23,
      period_3: 25,
      period_4: 8,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 20,
      period_2: 25,
      period_3: 22,
      period_4: 6,
    },
    start_time: new Date().toISOString(),
    isLive: true,
  },
  {
    id: 2,
    name: "Brazil vs Argentina",
    tournament_name: "South American Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Brazil",
    away_team_name: "Argentina",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 18,
      period_2: 25,
      period_3: 10,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 20,
      period_3: 8,
    },
    start_time: new Date().toISOString(),
    isLive: true,
  },
  {
    id: 3,
    name: "USA vs Poland",
    tournament_name: "World Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "USA",
    away_team_name: "Poland",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 20,
      period_2: 25,
      period_3: 22,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 18,
      period_3: 25,
    },
    start_time: new Date(Date.now() - 86400000).toISOString(),
    isLive: true,
  },
  {
    id: 4,
    name: "Serbia vs Germany",
    tournament_name: "European Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Serbia",
    away_team_name: "Germany",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 15,
    },
    start_time: new Date(Date.now() - 172800000).toISOString(),
    isLive: true,
  },
  {
    id: 5,
    name: "Japan vs Slovenia",
    tournament_name: "Friendly Match",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Japan",
    away_team_name: "Slovenia",
    home_team_score: {
      current: 0,
      display: 0,
      period_1: 5,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 3,
    },
    start_time: new Date(Date.now() + 86400000).toISOString(),
    isLive: true,
  },
  {
    id: 6,
    name: "Canada vs Cuba",
    tournament_name: "North American Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Canada",
    away_team_name: "Cuba",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 22,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 20,
    },
    start_time: new Date(Date.now() + 172800000).toISOString(),
    isLive: true,
  },
  {
    id: 7,
    name: "Russia vs China",
    tournament_name: "World Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Russia",
    away_team_name: "China",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 19,
      period_2: 25,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 23,
    },
    start_time: new Date(Date.now() + 259200000).toISOString(),
    isLive: true,
  },
  {
    id: 8,
    name: "Netherlands vs Belgium",
    tournament_name: "European Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Netherlands",
    away_team_name: "Belgium",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 25,
      period_2: 27,
      period_3: 25,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 23,
      period_2: 29,
      period_3: 21,
    },
    start_time: new Date(Date.now() + 345600000).toISOString(),
    isLive: true,
  },
  {
    id: 9,
    name: "Italy vs Germany",
    tournament_name: "World League",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Italy",
    away_team_name: "Germany",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 25,
      period_2: 18,
      period_3: 23,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 21,
      period_2: 25,
      period_3: 25,
    },
    start_time: new Date().toISOString(),
    isLive: true,
  },
  {
    id: 10,
    name: "USA vs Brazil",
    tournament_name: "World League",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "USA",
    away_team_name: "Brazil",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 20,
      period_2: 25,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 23,
    },
    start_time: new Date().toISOString(),
    isLive: true,
  },
  {
    id: 11,
    name: "Argentina vs Poland",
    tournament_name: "Pan American Cup",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Argentina",
    away_team_name: "Poland",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 25,
      period_2: 22,
      period_3: 25,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 20,
      period_2: 25,
      period_3: 23,
    },
    start_time: new Date(Date.now() - 432000000).toISOString(),
    isLive: true,
  },
  {
    id: 12,
    name: "France vs Russia",
    tournament_name: "European Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "France",
    away_team_name: "Russia",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 23,
      period_2: 21,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 25,
    },
    start_time: new Date(Date.now() - 259200000).toISOString(),
    isLive: true,
  },
  {
    id: 13,
    name: "Korea vs Thailand",
    tournament_name: "Asian Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Korea",
    away_team_name: "Thailand",
    home_team_score: {
      current: 0,
      display: 0,
      period_1: 8,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 10,
    },
    start_time: new Date(Date.now() + 432000000).toISOString(),
    isLive: true,
  },
  {
    id: 14,
    name: "Tunisia vs Egypt",
    tournament_name: "African Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Tunisia",
    away_team_name: "Egypt",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
    },
    away_team_score: {
      current: 0,
      display: 0,
      period_1: 22,
    },
    start_time: new Date(Date.now() + 518400000).toISOString(),
    isLive: true,
  },
  {
    id: 15,
    name: "Mexico vs Cuba",
    tournament_name: "NORCECA Championship",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Mexico",
    away_team_name: "Cuba",
    home_team_score: {
      current: 1,
      display: 1,
      period_1: 18,
      period_2: 21,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 25,
      period_2: 23,
    },
    start_time: new Date(Date.now() + 604800000).toISOString(),
    isLive: true,
  },
  {
    id: 16,
    name: "Belgium vs Spain",
    tournament_name: "European League",
    status: { type: "inprogress" },
    status_type: "inprogress",
    home_team_name: "Belgium",
    away_team_name: "Spain",
    home_team_score: {
      current: 2,
      display: 2,
      period_1: 25,
      period_2: 27,
      period_3: 25,
    },
    away_team_score: {
      current: 1,
      display: 1,
      period_1: 23,
      period_2: 29,
      period_3: 21,
    },
    start_time: new Date(Date.now() + 691200000).toISOString(),
    isLive: true,
  },
]

function formatSetScores(home: MatchScore, away: MatchScore): string {
  const parts: string[] = []
  for (let i = 1; i <= 5; i++) {
    const h = (home as any)[`period_${i}`]
    const a = (away as any)[`period_${i}`]
    if (h != null || a != null) {
      parts.push(`Set ${i}: ${h ?? "?"}-${a ?? "?"}`)
    }
  }
  return parts.join(" | ")
}

export default function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [favoriteMatches, setFavoriteMatches] = useState<number[]>([])

  // === Dev: usa sempre i fallback ===
  async function fetchMatchesDev() {
    setError(null)
    setLoading(true)
    try {
      await new Promise((r) => setTimeout(r, 1000))
      setMatches(fallbackMatches)
    } catch (err) {
      console.error("fetchMatchesDev errore:", err)
      setMatches(fallbackMatches)
    } finally {
      setLoading(false)
    }
  }

  // === Prod: chiama l'API vera e, in caso di errore, mostra l'errore in UI ===
  async function fetchMatchesProd() {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(MATCHES_URL, {
        headers: { Authorization: `Bearer ${API_KEY}` },
      })
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data: RawMatch[] = await res.json()
      const parsed: Match[] = data.map((m) => ({
        ...m,
        isLive: m.status_type === "inprogress",
        tournament_name: m.tournament_name ?? "–",
      }))
      setMatches(parsed)
    } catch (err) {
      setError("Errore nella richiesta API")
    } finally {
      setLoading(false)
    }
  }

  // ==== SCEGLI QUALE USARE ====
  const fetchMatches = fetchMatchesDev
  // const fetchMatches = fetchMatchesProd

  useEffect(() => {
    fetchMatches()
  }, [])

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

  const getMatchStatus = (m: Match) => {
    if (m.isLive) return "IN CORSO"
    if (m.status_type === "finished") return "TERMINATO"
    if (m.status_type === "scheduled") return "PROGRAMMATO"
    return "NON DISPONIBILE"
  }

  const getStatusColor = (m: Match) => {
    if (m.isLive) return "text-volleyball-orange"
    if (m.status_type === "finished") return "text-muted-foreground"
    if (m.status_type === "scheduled") return "text-volleyball-blue"
    return "text-muted-foreground"
  }

  const toggleFavorite = (id: number) =>
    setFavoriteMatches((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))

  const selected = matches.filter((m) => favoriteMatches.includes(m.id))

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

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
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
              matches.map((match) => (
                <div
                  key={match.id}
                  className="flex items-center justify-between rounded-lg border border-border p-3 hover:bg-primary/5 transition-colors"
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
                        className={`h-5 w-5 ${
                          favoriteMatches.includes(match.id)
                            ? "fill-volleyball-orange text-volleyball-orange"
                            : "text-muted-foreground"
                        } transition-colors`}
                      />
                    </button>
                    <div>
                      <p className="text-sm font-medium">{match.name}</p>
                      <p className="text-xs flex items-center gap-1.5">
                        <span className={`font-medium ${getStatusColor(match)}`}>{getMatchStatus(match)}</span>
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
              {selected.length > 0 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-heading font-bold text-foreground mb-4">I tuoi match preferiti</h2>
                  {selected.map((match) => (
                    <div
                      key={match.id}
                      className="w-full border border-border rounded-xl bg-card p-6 shadow-sm hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-bold font-heading">{match.name}</h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            match.isLive
                              ? "bg-volleyball-orange/10 text-volleyball-orange"
                              : match.status_type === "finished"
                                ? "bg-muted text-muted-foreground"
                                : "bg-volleyball-blue/10 text-volleyball-blue"
                          }`}
                        >
                          {getMatchStatus(match)}
                        </span>
                      </div>

                      <div className="text-sm text-muted-foreground mb-6 space-y-1">
                        <p>
                          Torneo: <span className="text-foreground">{match.tournament_name}</span>
                        </p>
                        <p>
                          Data: <span className="text-foreground">{formatMatchDate(match.start_time)}</span>
                        </p>
                        <p className="mt-2 text-xs">{formatSetScores(match.home_team_score, match.away_team_score)}</p>
                      </div>

                      <div className="flex justify-between items-center bg-muted/30 p-4 rounded-lg">
                        <div className="text-center">
                          <p className="font-medium text-foreground mb-2">{match.home_team_name}</p>
                          <p className="text-3xl font-bold text-primary">{match.home_team_score.display}</p>
                        </div>
                        <div className="text-xl font-bold text-muted-foreground">vs</div>
                        <div className="text-center">
                          <p className="font-medium text-foreground mb-2">{match.away_team_name}</p>
                          <p className="text-3xl font-bold text-primary">{match.away_team_score.display}</p>
                        </div>
                      </div>
                    </div>
                  ))}
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
