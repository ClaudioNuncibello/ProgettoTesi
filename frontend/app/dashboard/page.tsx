"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { Star, RefreshCw } from "lucide-react"

const API_KEY = "AymenURP9kWkgEatcBdcYA"
const MATCHES_URL = "https://volleyball.sportdevs.com/matches?season_id=eq.17700"
const DETAIL_URL = (matchId: number) => `http://localhost:8000/match/${matchId}`

// --- Tipo per i soli match SportDevs (colonna di sinistra) ---
interface SportDevMatch {
  id: number
  name: string
  start_time: string
}

// --- Unica interfaccia per i dettagli (colonna di destra) ---
interface DetailedMatch {
  match_id: number
  timestamp: string
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
  { id: 1, name: "Italy vs France", start_time: "2025-06-03T15:30:00Z" },
  { id: 2, name: "Brazil vs Argentina", start_time: "2025-06-03T16:00:00Z" },
  { id: 3, name: "USA vs Poland", start_time: "2025-06-03T16:30:00Z" },
]

// --- Dati di fallback per la colonna di destra ---
const testDetailedMatches: Record<number, DetailedMatch> = {
  1: {
    match_id: 1,
    timestamp: "2025-05-13 13:16:47.079969",
    home_team_id: 2164,
    away_team_id: 370209,
    home_score_total: 70,
    away_score_total: 44,
    home_sets_won: 2,
    away_sets_won: 0,
    score_diff: 26,
    set_diff: 2,
    home_current_score: "20",
    away_current_score: "14",
    set_info: "Set 1: 25-14 | Set 2: 25-16 | Set 3: 20-14",
    game_duration: "150m 0s",
    match_status: "3rd set",
    home_win_rate_last5: 0.8,
    away_win_rate_last5: 0.6666666666666666,
    head_to_head_win_rate_home: 1.0,
    predicted_win: 0.65,
  },
  2: {
    match_id: 2,
    timestamp: "2025-05-14 20:57:28.290246",
    home_team_id: 44350,
    away_team_id: 44433,
    home_score_total: 91,
    away_score_total: 93,
    home_sets_won: 2,
    away_sets_won: 2,
    score_diff: -2,
    set_diff: 0,
    home_current_score: "22",
    away_current_score: "25",
    set_info: "Set 1: 25-22 | Set 2: 19-25 | Set 3: 25-21 | Set 4: 22-25",
    game_duration: "150m 0s",
    match_status: "4th set",
    home_win_rate_last5: 0.6,
    away_win_rate_last5: 0.4,
    head_to_head_win_rate_home: 0.45,
    predicted_win: 0.45,
  },
  3: {
    match_id: 3,
    timestamp: "2025-05-14 20:57:28.290386",
    home_team_id: 44300,
    away_team_id: 44561,
    home_score_total: 94,
    away_score_total: 90,
    home_sets_won: 1,
    away_sets_won: 2,
    score_diff: 4,
    set_diff: -1,
    home_current_score: "22",
    away_current_score: "16",
    set_info: "Set 1: 23-25 | Set 2: 23-25 | Set 3: 26-24 | Set 4: 22-16",
    game_duration: "150m 0s",
    match_status: "4th set",
    home_win_rate_last5: 0.5,
    away_win_rate_last5: 0.2,
    head_to_head_win_rate_home: 0.25,
    predicted_win: 0.25,
  },
}

export default function Dashboard() {
  // Stato per la colonna di sinistra
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

  // --- Fetch “Prod” per la lista SportDevs (colonna sinistra) ---
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
  const fetchMatches = fetchMatchesDev
  // const fetchMatches = fetchMatchesProd

  // --- Fetch fallback per i dettagli (colonna di destra) ---
  async function fetchMatchDetailsDev(matchId: number) {
    await new Promise((r) => setTimeout(r, 300))
    const demo = testDetailedMatches[matchId]
    if (demo) {
      setDetailedMatches((prev) => ({
        ...prev,
        [matchId]: demo,
      }))
    }
  }

  // --- Fetch “Prod” per i dettagli (colonna di destra) ---
  async function fetchMatchDetailsProd(matchId: number) {
    try {
      const res = await fetch(DETAIL_URL(matchId))
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data: DetailedMatch = await res.json()
      setDetailedMatches((prev) => ({
        ...prev,
        [matchId]: data,
      }))
    } catch (err) {
      console.error(`Errore fetch dettagli match ${matchId}:`, err)
      // fallback automatico
      const demo = testDetailedMatches[matchId]
      if (demo) {
        setDetailedMatches((prev) => ({
          ...prev,
          [matchId]: demo,
        }))
      }
    }
  }

  // ==== SCEGLI QUALE USARE per la colonna di destra ====
  const fetchMatchDetails = fetchMatchDetailsDev
  // const fetchMatchDetails = fetchMatchDetailsProd

  useEffect(() => {
    fetchMatches()
  }, [])

  // Formatta data/ora in italiano
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
                        <span className="text-muted-foreground">{formatMatchDate(match.start_time)}</span>
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
                            Torneo: <span className="text-foreground">–</span>
                          </p>
                          <p>
                            Ultimo aggiornamento:{" "}
                            <span className="text-foreground">
                              {detailed ? formatMatchDate(detailed.timestamp) : formatMatchDate(match.start_time)}
                            </span>
                          </p>
                        </div>

                        {/* ----------------- RIGA: Tabellone + Storico Set ----------------- */}
                        <div className="flex gap-4 justify-start">
                          {/* Tabellone sportivo compatto */}
                          <div className="bg-black rounded-lg overflow-hidden shadow-lg">
                            {/* Header colonne */}
                            <div className="grid grid-cols-3 bg-gray-700 text-white text-xs font-medium">
                              <div className="py-2 px-3 text-center border-r border-gray-600">Squadra</div>
                              <div className="py-2 px-3 text-center border-r border-gray-600 bg-secondary/30">
                                Set vinti
                              </div>
                              <div className="py-2 px-3 text-center bg-primary/30">Punti totali</div>
                            </div>
                            {/* Corpo tabellone */}
                            <div className="grid grid-cols-3 text-white">
                              {/* Casa */}
                              <div className="py-3 px-3 border-r border-gray-700 border-b border-gray-700 font-medium text-sm truncate">
                                {homeName}
                              </div>
                              <div className="py-3 px-3 border-r border-gray-700 border-b border-gray-700 text-center bg-secondary/20">
                                <span className="text-xl font-bold text-secondary">
                                  {detailed ? detailed.home_sets_won : "–"}
                                </span>
                              </div>
                              <div className="py-3 px-3 border-b border-gray-700 text-center bg-primary/20">
                                <span className="text-2xl font-bold text-primary">
                                  {detailed ? detailed.home_current_score : "–"}
                                </span>
                              </div>
                              {/* Ospiti */}
                              <div className="py-3 px-3 border-r border-gray-700 font-medium text-sm truncate">
                                {awayName}
                              </div>
                              <div className="py-3 px-3 border-r border-gray-700 text-center bg-secondary/20">
                                <span className="text-xl font-bold text-secondary">
                                  {detailed ? detailed.away_sets_won : "–"}
                                </span>
                              </div>
                              <div className="py-3 px-3 text-center bg-primary/20">
                                <span className="text-2xl font-bold text-primary">
                                  {detailed ? detailed.away_current_score : "–"}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Storico Set - Layout Orizzontale Dinamico */}
                          {detailed && (() => {
                            // 1) Dividi set_info in array di righe
                            const setsArr = detailed.set_info.split(" | ")
                            const totalSets = setsArr.length
                            if (totalSets === 0) return null

                            // 2) Mappa totalSets+1 a una classe Tailwind fissa
                            const gridColsMap: Record<number, string> = {
                              2: "grid-cols-2",
                              3: "grid-cols-3",
                              4: "grid-cols-4",
                              5: "grid-cols-5",
                              6: "grid-cols-6",
                            }
                            // vogliamo totalSets+1 colonne
                            const colsKey = totalSets + 1
                            const gridColsClass = gridColsMap[colsKey] || "grid-cols-2"

                            // 3) Estrai punteggi da ciascun "Set X: H-A"
                            const scores = setsArr.map((entry) => {
                              const parts = entry.split(":")[1].trim().split("-")
                              return {
                                home: parseInt(parts[0], 10),
                                away: parseInt(parts[1], 10),
                              }
                            })

                            // 4) Ultimo indice = set corrente
                            const currentSetIndex = totalSets - 1

                            return (
                              <div className="bg-white border border-border rounded-lg overflow-hidden shadow-lg">
                                {/* Header storico */}
                                <div className="bg-gray-100 text-gray-800 text-center py-2 font-bold text-sm border-b border-border">
                                  Storico Set
                                </div>

                                {/* Intestazioni colonne - numeri dei set */}
                                <div
                                  className={`grid ${gridColsClass} bg-gray-50 text-gray-700 text-xs font-medium border-b border-border`}
                                >
                                  {/* Colonna “Squadra” */}
                                  <div className="py-2 px-2 text-center border-r border-border">Squadra</div>
                                  {setsArr.map((_, idx) => {
                                    const isCurrent = idx === currentSetIndex
                                    return (
                                      <div
                                        key={idx}
                                        className={`py-2 px-2 text-center border-r border-border ${
                                          isCurrent ? "bg-primary/20" : ""
                                        }`}
                                      >
                                        Set {idx + 1}
                                        {isCurrent && <span className="text-primary ml-1">●</span>}
                                      </div>
                                    )
                                  })}
                                </div>

                                {/* Righe con i punteggi di ciascun set */}
                                <div className="text-gray-800">
                                  {/* Riga squadra casa */}
                                  <div className={`grid ${gridColsClass} border-b border-border`}>
                                    <div className="py-3 px-2 border-r border-border font-medium text-sm truncate">
                                      {homeName}
                                    </div>
                                    {scores.map((s, idx) => {
                                      const won = s.home > s.away
                                      const isCurrent = idx === currentSetIndex
                                      return (
                                        <div
                                          key={idx}
                                          className={`py-3 px-2 text-center border-r border-border text-sm font-bold ${
                                            won ? "text-green-600" : ""
                                          } ${isCurrent ? "bg-primary/10" : ""}`}
                                        >
                                          {s.home}
                                        </div>
                                      )
                                    })}
                                  </div>

                                  {/* Riga squadra ospiti */}
                                  <div className={`grid ${gridColsClass}`}>
                                    <div className="py-3 px-2 border-r border-border font-medium text-sm truncate">
                                      {awayName}
                                    </div>
                                    {scores.map((s, idx) => {
                                      const won = s.away > s.home
                                      const isCurrent = idx === currentSetIndex
                                      return (
                                        <div
                                          key={idx}
                                          className={`py-3 px-2 text-center border-r border-border text-sm font-bold ${
                                            won ? "text-green-600" : ""
                                          } ${isCurrent ? "bg-primary/10" : ""}`}
                                        >
                                          {s.away}
                                        </div>
                                      )
                                    })}
                                  </div>
                                </div>
                              </div>
                            )
                          })()}
                        </div>
                        {/* ----------------- fine riga tabellone + storico ----------------- */}
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
