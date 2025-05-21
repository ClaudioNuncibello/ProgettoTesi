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
        "Raccogliamo aggiornamenti regolari dalla Sport Devs API (10 s) ottenendo un JSON dello stato di ogni match (snapshoat live) ; ogni snapshoat  viene serializzato e pushato su un topic Kafka dedicato, garantendo tracciabilità storica e facilità di replay per analisi retrospettive.",
    },
    {
      id: 2,
      icon: Database,
      title: "Streaming & Analisi",
      description:
        "Consumiamo i dati grezzi dal topic Kafka dedicato, li trasformiamo con Logstash in eventi JSON standardizzati e li inviamo a Spark Streaming; qui vengono applicati modelli di machine learning che calcolano in tempo reale probabilità di vittoria e metriche chiave, poi pubblicati su un topic di output pronti per la dashboard.",
    },
    {
      id: 3,
      icon: Server,
      title: "Deployment & Indicizzazione",
      description:
        "L’intera pipeline è containerizzata con Docker per garantire deployment rapido e scalabilità automatica; gli snapshoat vengono indicizzati in Elasticsearch, assicurando ricerche veloci e dashboard interattive sempre aggiornate.",
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
            <Link href="/" className="nav-link active">
              Home
            </Link>
            <Link href="https://github.com/ClaudioNuncibello/ProgettoTesi" className="nav-link">
              GitHub
            </Link>
            <Link href="/dashboard" className="nav-link">
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <main className="flex-1 flex flex-col justify-center overflow-y-auto">
        <div className="container mx-auto px-4 py-6 flex flex-col h-full">
          <header className="mb-8 text-center">
            <h1 className="mb-4 text-4xl md:text-5xl font-bold text-foreground bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
              Segui i tuoi match in tempo reale
            </h1>
            <p className="mx-auto max-w-2xl text-muted-foreground mb-6">
              Salva i tuoi incontri preferiti e scopri statistiche live e previsioni direttamente sulla tua dashboard.
            </p>
            <Link
              href="https://github.com/ClaudioNuncibello/ProgettoTesi"
              className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm"
            >
              <Github size={18} />
              Guarda il codice su GitHub
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
