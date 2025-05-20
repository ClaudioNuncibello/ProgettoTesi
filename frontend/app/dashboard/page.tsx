"use client"

import React, { useState, useEffect } from "react"
import Link from "next/link"
import { Star } from "lucide-react"

const API_KEY = "AymenURP9kWkgEatcBdcYA"
const MATCHES_URL = "https://volleyball.sportdevs.com/matches?season_id=eq.17700"

// --- Tipi ---

// Un singolo oggetto punteggio, non un array
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

// Risposta "raw" dell’endpoint
interface RawMatch {
  id: number
  name: string
  tournament_name?: string
  status: MatchStatus           // <— non è un array
  status_type: string
  home_team_name: string
  away_team_name: string
  home_team_hash_image?: string
  away_team_hash_image?: string
  home_team_score: MatchScore   // <— direttamente un oggetto
  away_team_score: MatchScore
  start_time: string
  specific_start_time?: string
  times?: { specific_start_time: string }  // <— non è un array
}

// Modello usato nel componente
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

// Utility per formattare i punteggi di ogni set
function formatSetScores(home: MatchScore, away: MatchScore): string {
  // Scandiamo fino a 5 set
  const parts: string[] = []
  for (let i = 1; i <= 5; i++) {
    const h = (home as any)[`period_${i}`]
    const a = (away as any)[`period_${i}`]
    // se almeno uno dei due ha il campo, includiamo il set
    if (h != null || a != null) {
      parts.push(`Set ${i}: ${h ?? "?"}-${a ?? "?"}`)
    }
  }
  return parts.join(" | ")
}

export default function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [favoriteMatches, setFavoriteMatches] = useState<number[]>([])

  useEffect(() => {
    const fetchMatches = async () => {
      setLoading(true)
      try {
        const res = await fetch(MATCHES_URL, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${API_KEY}`,
            apikey: API_KEY,
            "Content-Type": "application/json",
          },
        })
        if (!res.ok) {
          console.warn(`API restituisce HTTP ${res.status}`)
          setMatches([])
          return
        }

        const json = await res.json()
        const data: RawMatch[] = Array.isArray(json) ? json : []

        const formatted: Match[] = data.map((m) => {
          const homeScore = m.home_team_score
          const awayScore = m.away_team_score
          const specific =
            m.specific_start_time ?? m.times?.specific_start_time

          return {
            id: m.id,
            name: m.name,
            tournament_name: m.tournament_name ?? "Non disponibile",
            status: m.status,
            status_type: m.status_type,
            home_team_name: m.home_team_name,
            away_team_name: m.away_team_name,
            home_team_hash_image: m.home_team_hash_image,
            away_team_hash_image: m.away_team_hash_image,
            home_team_score: homeScore,
            away_team_score: awayScore,
            start_time: m.start_time,
            specific_start_time: specific,
            isLive: m.status_type === "live",
          }
        })

        setMatches(formatted)
      } catch (err) {
        console.error("fetchMatches errore:", err)
        setMatches([])
      } finally {
        setLoading(false)
      }
    }

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

  const toggleFavorite = (id: number) =>
    setFavoriteMatches((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )

  const selected = matches.filter((m) => favoriteMatches.includes(m.id))

  return (
    <div className="min-h-screen bg-white">
      <nav className="flex items-center justify-between p-5 bg-gray-900 text-white shadow-md">
        <Link href="/" className="text-lg font-bold">
          VolleyApi
        </Link>
        <div className="flex space-x-6">
          <Link href="/" className="hover:underline hover:text-gray-300">
            Home
          </Link>
          <Link
            href="https://github.com/ClaudioNuncibello/ProgettoTesi"
            className="hover:underline hover:text-gray-300"
          >
            GitHub
          </Link>
          <Link href="/dashboard" className="hover:underline hover:text-gray-300">
            Dashboard
          </Link>
        </div>
      </nav>

      <main className="flex flex-col md:flex-row">
        {/* Colonna sinistra: tutti i match */}
        <div className="md:w-1/4 space-y-2 p-2 border-r border-gray-200">
          <h2 className="text-xl font-bold mb-3 text-gray-900">
            Match disponibili
          </h2>

          {loading ? (
            <div className="py-4 px-2 animate-pulse space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-10 bg-gray-200 rounded-lg" />
              ))}
            </div>
          ) : matches.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              Nessuna partita in corso
            </div>
          ) : (
            matches.map((match) => (
              <div
                key={match.id}
                className="flex items-center justify-between rounded-lg border border-gray-200 p-2 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center">
                  <button
                    onClick={() => toggleFavorite(match.id)}
                    aria-label={
                      favoriteMatches.includes(match.id)
                        ? `Rimuovi ${match.name} dai preferiti`
                        : `Aggiungi ${match.name} ai preferiti`
                    }
                    className="mr-2 focus:outline-none"
                  >
                    <Star
                      className={`h-5 w-5 ${
                        favoriteMatches.includes(match.id)
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-gray-400"
                      } transition-colors`}
                    />
                  </button>
                  <div>
                    <p className="text-sm font-medium">{match.name}</p>
                    <p className="text-xs text-gray-500">
                      {getMatchStatus(match)} •{" "}
                      {formatMatchDate(match.start_time)}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Colonna destra: partite selezionate */}
        <div className="md:w-3/4 p-4 bg-gray-50 min-h-[calc(100vh-80px)]">
          {selected.length > 0 ? (
            <div className="space-y-4">
              {selected.map((match) => (
                <div
                  key={match.id}
                  className="w-full border border-gray-200 rounded-lg bg-white p-4 shadow-sm"
                >
                  <h2 className="text-xl font-bold mb-2">{match.name}</h2>
                  <div className="text-sm text-gray-600 mb-3">
                    <p>Torneo: {match.tournament_name}</p>
                    <p>Data: {formatMatchDate(match.start_time)}</p>
                    <p>Stato: {getMatchStatus(match)}</p>
                    <p className="mt-2 text-gray-500">
                      {formatSetScores(
                        match.home_team_score,
                        match.away_team_score
                      )}
                    </p>
                  </div>
                  <div className="flex justify-between items-center">
                    <div className="text-center">
                      <p className="font-semibold">
                        {match.home_team_name}
                      </p>
                      <p className="text-2xl font-bold">
                        {match.home_team_score.display}
                      </p>
                    </div>
                    <div className="text-xl font-bold">vs</div>
                    <div className="text-center">
                      <p className="font-semibold">
                        {match.away_team_name}
                      </p>
                      <p className="text-2xl font-bold">
                        {match.away_team_score.display}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <h1 className="text-4xl font-bold text-gray-900">
                Follow your matches
              </h1>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
