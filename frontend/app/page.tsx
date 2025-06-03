"use client"

import Link from "next/link"

import type React from "react"
import { Camera, Database, Server, Github, ArrowRight, Mail, MapPin, Twitter, Linkedin, Instagram } from "lucide-react"
import { useEffect, useRef, useState } from "react"

// Hook per le animazioni scroll
function useScrollAnimation() {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
      },
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [])

  return { ref, isVisible }
}

// Componente per sezioni animate
function AnimatedSection({
  children,
  className = "",
  animation = "fade-up",
}: {
  children: React.ReactNode
  className?: string
  animation?: "fade-up" | "fade-left" | "fade-right"
}) {
  const { ref, isVisible } = useScrollAnimation()

  const animationClasses = {
    "fade-up": isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8",
    "fade-left": isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-8",
    "fade-right": isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-8",
  }

  return (
    <div ref={ref} className={`transition-all duration-700 ease-out ${animationClasses[animation]} ${className}`}>
      {children}
    </div>
  )
}

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-white">
      {/* Header fisso */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? "bg-white/95 backdrop-blur-lg shadow-lg border-b border-gray-200" : "bg-transparent"
        }`}
      >
        <div className="flex items-center justify-between w-full px-6 py-4">
          <Link href="/" className={`text-2xl font-bold ${isScrolled ? "text-primary" : "text-white"}`}>
            VolleyApi
          </Link>
          <nav className="flex items-center space-x-8">
            <Link
              href="/"
              className={`transition-colors font-medium ${
                isScrolled ? "text-gray-700 hover:text-primary" : "text-white hover:text-white/80"
              }`}
            >
              Home
            </Link>
            <Link
              href="https://github.com/ClaudioNuncibello/ProgettoTesi"
              className={`flex items-center gap-2 transition-colors font-medium ${
                isScrolled ? "text-gray-700 hover:text-primary" : "text-white hover:text-white/80"
              }`}
            >
              <Github size={18} />
              GitHub
            </Link>
            <Link
              href="/dashboard"
              className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                isScrolled ? "bg-primary text-white hover:bg-primary/90" : "bg-white text-primary hover:bg-white/90"
              }`}
            >
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-primary via-secondary to-volleyball-cyan overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10 text-center text-white px-6 max-w-4xl mx-auto">
          <AnimatedSection animation="fade-up">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Segui i tuoi match
              <span className="block text-volleyball-orange">in tempo reale</span>
            </h1>
          </AnimatedSection>

          <AnimatedSection animation="fade-up" className="delay-200">
            <p className="text-xl md:text-2xl mb-8 text-white/90 max-w-2xl mx-auto">
              La piattaforma definitiva per monitorare le partite di volley con statistiche live, previsioni AI e
              dashboard personalizzate.
            </p>
          </AnimatedSection>

          <AnimatedSection animation="fade-up" className="delay-400">
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-white text-primary px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg"
              >
                Inizia ora
                <ArrowRight size={20} />
              </Link>
              <Link
                href="https://github.com/ClaudioNuncibello/ProgettoTesi"
                className="inline-flex items-center gap-2 border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-primary transition-all"
              >
                <Github size={20} />
                Vedi il codice
              </Link>
            </div>
          </AnimatedSection>
        </div>

        {/* Elementi decorativi */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-white/10 rounded-full blur-xl"></div>
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-volleyball-orange/20 rounded-full blur-xl"></div>
        <div className="absolute top-1/2 right-20 w-16 h-16 bg-white/5 rounded-full blur-lg"></div>
      </section>

      {/* Sezione Live Snapshot */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <AnimatedSection animation="fade-right">
              <div className="space-y-6">
                <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium">
                  <Camera size={16} />
                  Live Snapshot
                </div>
                <h2 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">Dati in tempo reale</h2>
                <p className="text-xl text-gray-600 leading-relaxed">
                  Raccogliamo aggiornamenti ogni 10 secondi dalla Sport Devs API, ottenendo snapshot live di ogni match.
                  Ogni dato viene serializzato e inviato su Kafka per garantire tracciabilità e analisi retrospettive.
                </p>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    Aggiornamenti ogni 10s
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    Kafka Streaming
                  </div>
                </div>
              </div>
            </AnimatedSection>

            <AnimatedSection animation="fade-left">
              <div className="relative">
                <div className="bg-gradient-to-br from-primary/5 to-secondary/5 rounded-2xl p-8 border border-gray-200">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border">
                      <span className="font-medium">Italy vs France</span>
                      <span className="text-green-500 font-bold">LIVE</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border">
                      <span className="font-medium">Brazil vs Argentina</span>
                      <span className="text-green-500 font-bold">LIVE</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border">
                      <span className="font-medium">USA vs Poland</span>
                      <span className="text-green-500 font-bold">LIVE</span>
                    </div>
                  </div>
                </div>
                <div className="absolute -top-4 -right-4 w-24 h-24 bg-primary/10 rounded-full blur-xl"></div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* Sezione Streaming & Processing */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <AnimatedSection animation="fade-right">
              <div className="relative">
                <div className="bg-gradient-to-br from-secondary/10 to-volleyball-cyan/10 rounded-2xl p-8 border border-gray-200">
                  <div className="space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center">
                        <Database className="text-white" size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900">Logstash</h4>
                        <p className="text-sm text-gray-600">Trasformazione dati</p>
                      </div>
                    </div>
                    <div className="h-px bg-gray-300"></div>
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-volleyball-cyan rounded-lg flex items-center justify-center">
                        <Server className="text-white" size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900">Spark ML</h4>
                        <p className="text-sm text-gray-600">Predizioni AI</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="absolute -bottom-4 -left-4 w-20 h-20 bg-secondary/10 rounded-full blur-xl"></div>
              </div>
            </AnimatedSection>

            <AnimatedSection animation="fade-left">
              <div className="space-y-6">
                <div className="inline-flex items-center gap-2 bg-secondary/10 text-secondary px-4 py-2 rounded-full text-sm font-medium">
                  <Database size={16} />
                  Streaming & Analisi
                </div>
                <h2 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">Intelligenza artificiale</h2>
                <p className="text-xl text-gray-600 leading-relaxed">
                  I dati grezzi vengono trasformati con Logstash e processati da Spark Streaming. I nostri modelli di
                  machine learning calcolano probabilità di vittoria e metriche avanzate in tempo reale.
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="text-2xl font-bold text-secondary">???%</div>
                    <div className="text-sm text-gray-600">Accuratezza predizioni</div>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="text-2xl font-bold text-volleyball-cyan">&lt; 1s</div>
                    <div className="text-sm text-gray-600">Latenza processing</div>
                  </div>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* Sezione Deployment & Indexing */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <AnimatedSection animation="fade-right">
              <div className="space-y-6">
                <div className="inline-flex items-center gap-2 bg-volleyball-orange/20 text-volleyball-orange px-4 py-2 rounded-full text-sm font-medium">
                  <Server size={16} />
                  Deployment & Indicizzazione
                </div>
                <h2 className="text-4xl md:text-5xl font-bold leading-tight">Scalabilità enterprise</h2>
                <p className="text-xl text-gray-300 leading-relaxed">
                  L'intera pipeline è containerizzata con Docker per deployment rapido e scalabilità automatica.
                  Elasticsearch indicizza tutti i dati per ricerche veloci e dashboard sempre aggiornate.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-gray-300">Container Docker orchestrati</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-gray-300">Elasticsearch per ricerche veloci</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span className="text-gray-300">Dashboard interattive real-time</span>
                  </div>
                </div>
              </div>
            </AnimatedSection>

            <AnimatedSection animation="fade-left">
              <div className="relative">
                <div className="bg-gradient-to-br from-gray-800 to-gray-700 rounded-2xl p-8 border border-gray-600">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Sistema Status</span>
                      <span className="text-green-400 font-bold">● Online</span>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-400">Docker Containers</span>
                        <span className="text-white">12/12</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-400">Elasticsearch VolleyApi</span>
                        <span className="text-white">● Online</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="absolute -top-4 -right-4 w-24 h-24 bg-volleyball-orange/20 rounded-full blur-xl"></div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <AnimatedSection animation="fade-up">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Pronto a iniziare?</h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Segui i tuoi match preferiti in tempo reale e visualizza metriche avanzate.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-white text-primary px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105"
              >
                Accedi alla Dashboard
                <ArrowRight size={20} />
              </Link>
              <Link
                href="https://github.com/ClaudioNuncibello/ProgettoTesi"
                className="inline-flex items-center gap-2 border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-primary transition-all"
              >
                <Github size={20} />
                Esplora il codice
              </Link>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8">
            <AnimatedSection animation="fade-up">
              <div className="space-y-4">
                <h3 className="text-2xl font-bold text-primary">VolleyApi</h3>
                <p className="text-gray-400">
                  La piattaforma definitiva per seguire le partite di volley con tecnologie all'avanguardia.
                </p>
                <div className="flex space-x-4">
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    <Twitter size={20} />
                  </a>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    <Linkedin size={20} />
                  </a>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    <Instagram size={20} />
                  </a>
                </div>
              </div>
            </AnimatedSection>

            <AnimatedSection animation="fade-up" className="delay-100">
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">Prodotto</h4>
                <ul className="space-y-2">
                  <li>
                    <Link href="/dashboard" className="text-gray-400 hover:text-white transition-colors">
                      Dashboard
                    </Link>
                  </li>
                  <li>
                    <a
                      href="https://sportdevs.com/volleyball"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      API
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/ClaudioNuncibello/ProgettoTesi"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      Documentazione
                    </a>
                  </li>
                </ul>
              </div>
            </AnimatedSection>

            <AnimatedSection animation="fade-up" className="delay-300">
              <div className="space-y-4">
                <h4 className="text-lg font-semibold">Contatti</h4>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Mail size={16} className="text-primary" />
                    <span className="text-gray-400">info@volleyapi.com</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <MapPin size={16} className="text-primary" />
                    <span className="text-gray-400">Catania, Italia</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Github size={16} className="text-primary" />
                      <span className="text-gray-400">ClaudioNuncibello</span>
                  </div>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </footer>
    </div>
  )
}
