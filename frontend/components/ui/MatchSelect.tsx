// components/ui/MatchSelect.tsx
"use client"

import { Fragment } from "react"
import { Listbox, Transition } from "@headlessui/react"
import { ChevronDown, Check } from "lucide-react"

export interface Match {
  id: number
  name: string
  start_time: string
  tournament_name: string
}

interface MatchSelectProps {
  matches: Match[]
  activeFavorite: number | null
  onChange: (matchId: number) => void
}

export default function MatchSelect({
  matches,
  activeFavorite,
  onChange,
}: MatchSelectProps) {
  // Selezionato
  const selected =
    matches.find((m) => m.id === activeFavorite) || matches[0]

  return (
    <Listbox value={selected.id} onChange={onChange}>
      {({ open } : {open : boolean}) => (
        <div className="relative inline-block text-left">
          {/* Il pulsante */}
          <Listbox.Button className="flex items-center justify-between w-60 px-4 py-2 bg-white border border-border rounded-lg shadow-sm hover:text-primary transition-colors border-primary">
            <span className="truncate">{selected.name}</span>
            <ChevronDown className="ml-2 h-5 w-5 text-muted-foreground" />
          </Listbox.Button>

          {/* Quando open, portalto il menu a livello di <body> */}
          <Transition
            as={Fragment}
            show={open}
            enter="transition ease-out duration-100"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Listbox.Options
              static
              className="absolute z-50 mt-2 w-60 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
            >
              {matches.map((match) => (
                <Listbox.Option
                  key={match.id}
                  value={match.id}
                  className={({ active }: { active: boolean }) =>
                    `cursor-pointer select-none px-4 py-2 ${
                      active
                        ? "bg-primary/10 text-primary"
                        : "text-gray-800"
                    }`
                  }
                >
                  {({ selected }: { selected: boolean }) => (
                    <div className="flex items-center justify-between">
                      <span
                        className={`truncate ${
                          selected ? "font-medium" : "font-normal"
                        }`}
                      >
                        {match.name}
                      </span>
                      {selected && (
                        <Check className="h-5 w-5 text-primary" />
                      )}
                    </div>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      )}
    </Listbox>
  )
}
