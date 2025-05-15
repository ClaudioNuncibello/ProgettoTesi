import Link from "next/link"
import { Camera, Database, Server, Github } from "lucide-react"

export default function Home() {
  // Dati delle card
  const cards = [
    {
      id: 1,
      icon: Camera,
      title: "Live Snapshot",
      description:
        "Estraiamo in tempo reale lo stato della partita dalle Sport Devs API: ogni snapshot è una fotografia puntuale del match in corso.",
    },
    {
      id: 2,
      icon: Database,
      title: "Streaming & Processing",
      description:
        "I dati grezzi viaggiano su Kafka, vengono trasformati da Logstash e infine elaborati da Spark con modelli di predizione per la vittoria.",
    },
    {
      id: 3,
      icon: Server,
      title: "Indexing & Deployment",
      description:
        "Tutto il processo gira in container Docker e i risultati vengono indicizzati in Elasticsearch per ricerche veloci e visualizzazioni su dashboard.",
    },
  ]

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

      <main className="container mx-auto px-4 py-6">
        <header className="mb-6 text-center">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Follow Your Matches</h1>
          <p className="mx-auto max-w-2xl text-sm text-gray-700 mb-4">
            Follow your favorite matches: tap the star to save them and see live stats on your dashboard.
          </p>
          <Link
            href="https://github.com/ClaudioNuncibello/ProgettoTesi"
            className="inline-flex items-center gap-2 bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-800 transition-colors"
          >
            <Github size={16} />
            View code on GitHub
          </Link>
        </header>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-3 max-w-6xl mx-auto">
          {cards.map((card) => (
            <div
              key={card.id}
              className="flex flex-col rounded-xl bg-white border border-gray-300 shadow-sm transform transition-all duration-300 hover:scale-102 hover:shadow-[0_0_15px_rgba(59,130,246,0.5)] hover:border-blue-200 overflow-hidden min-h-[400px]"
              aria-label={`${card.title} card`}
            >
              <div className="flex flex-col h-full p-6">
                <div className="flex items-center justify-center mb-6">
                  <div className="p-3 bg-gray-100 rounded-full">
                    <card.icon className="h-8 w-8 text-gray-700" />
                  </div>
                </div>

                <h2 className="text-xl font-bold text-center mb-4 text-gray-900">{card.title}</h2>

                <p className="text-gray-600 text-center flex-grow">{card.description}</p>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
