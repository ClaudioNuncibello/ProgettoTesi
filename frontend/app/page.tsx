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

      <main className="flex-1 flex flex-col justify-center overflow-y-auto">
        <div className="container mx-auto px-4 py-6 flex flex-col h-full">
          <header className="mb-8 text-center">
            <h1 className="mb-4 text-4xl md:text-5xl font-bold text-foreground bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
              Follow Your Matches
            </h1>
            <p className="mx-auto max-w-2xl text-muted-foreground mb-6">
              Follow your favorite matches: tap the star to save them and see live stats on your dashboard.
            </p>
            <Link
              href="https://github.com/ClaudioNuncibello/ProgettoTesi"
              className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm"
            >
              <Github size={18} />
              View code on GitHub
            </Link>
          </header>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3 max-w-6xl mx-auto flex-1">
            {cards.map((card) => (
              <div
                key={card.id}
                className="flex flex-col rounded-xl bg-card border border-border shadow-sm card-hover overflow-hidden"
                aria-label={`${card.title} card`}
              >
                <div className="flex flex-col h-full p-6">
                  <div className="flex items-center justify-center mb-6">
                    <div className="p-3 rounded-full bg-primary/10 text-primary">
                      <card.icon className="h-8 w-8" />
                    </div>
                  </div>

                  <h2 className="text-xl font-bold text-center mb-4 text-foreground font-heading">{card.title}</h2>

                  <p className="text-muted-foreground text-center flex-grow">{card.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
