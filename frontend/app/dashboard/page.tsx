"use client"

import Link from "next/link"
import { Star } from "lucide-react"
import { useState } from "react"

export default function Dashboard() {
  // Dati delle partite
  const matches = [
    { id: 1, teams: "Italy vs France", status: "LIVE", isLive: true },
    { id: 2, teams: "Brazil vs Argentina", status: "LIVE", isLive: true },
    { id: 3, teams: "USA vs Poland", status: "Not live", isLive: false },
    { id: 4, teams: "Serbia vs Germany", status: "Niot", isLive: false },
    { id: 5, teams: "Japan vs Slovenia", status: "Niot", isLive: false },
  ]

  // Stato per le stelle selezionate
  const [favoriteMatches, setFavoriteMatches] = useState<number[]>([])

  // Funzione per gestire il click sulla stella
  const toggleFavorite = (matchId: number) => {
    setFavoriteMatches((prev) => {
      if (prev.includes(matchId)) {
        return prev.filter((id) => id !== matchId)
      } else {
        return [...prev, matchId]
      }
    })
  }

  // Trova tutti i match preferiti
  const selectedMatches = matches.filter((match) => favoriteMatches.includes(match.id))

  return (
    <div className="min-h-screen bg-white">
      <nav className="flex items-center justify-between p-5 bg-gray-900 text-white shadow-md">
        <Link href="/" className="text-lg font-bold">
          VolleyApi
        </Link>
        <div className="flex space-x-6">
          <Link href="/" className="hover:underline hover:text-gray-300 transition-colors">
            Home
          </Link>
          <Link
            href="https://github.com/ClaudioNuncibello/ProgettoTesi"
            className="hover:underline hover:text-gray-300 transition-colors"
          >
            GitHub
          </Link>
          <Link href="/dashboard" className="hover:underline hover:text-gray-300 transition-colors">
            Dashboard
          </Link>
        </div>
      </nav>

      <main className="flex flex-col md:flex-row">
        {/* Colonna sinistra con le partite (attaccata al bordo) */}
        <div className="md:w-1/4 space-y-2 p-2 border-r border-gray-200">
          <h2 className="text-xl font-bold mb-3 text-gray-900">Match disponibili</h2>
          {matches.map((match) => (
            <div
              key={match.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 p-2 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center">
                  <button
                    onClick={() => toggleFavorite(match.id)}
                    className="mr-2 focus:outline-none"
                    aria-label={
                      favoriteMatches.includes(match.id)
                        ? `Rimuovi ${match.teams} dai preferiti`
                        : `Aggiungi ${match.teams} ai preferiti`
                    }
                  >
                    <Star
                      className={`h-5 w-5 ${
                        favoriteMatches.includes(match.id) ? "fill-yellow-400 text-yellow-400" : "text-gray-400"
                      } transition-colors`}
                    />
                  </button>
                  <span className="text-sm">{match.teams}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Colonna destra con le card dei match selezionati in cascata */}
        <div className="md:w-3/4 p-4 bg-gray-50 min-h-[calc(100vh-80px)]">
          {selectedMatches.length > 0 ? (
            <div className="space-y-4">
              {selectedMatches.map((match) => (
                <div key={match.id} className="w-full border border-gray-200 rounded-lg bg-white p-4 shadow-sm">
                  <h2 className="text-xl font-bold mb-2">{match.teams}</h2>
                  {/* Card vuota per ora, come richiesto */}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <h1 className="text-4xl font-bold text-gray-900">Follow your matchs</h1>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
