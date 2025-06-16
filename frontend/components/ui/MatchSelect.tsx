import { useState } from "react";
import { Listbox, Transition } from "@headlessui/react";
import { ChevronDown, Check } from "lucide-react";

interface Match {
  id: number;
  name: string;
  start_time: string;
}

interface MatchSelectProps {
  matches: Match[];
  activeFavorite: number | null;
  onChange: (matchId: number) => void;
}

const MatchSelect = ({ matches, activeFavorite, onChange }: MatchSelectProps) => {
  const activeMatch = matches.find((m) => m.id === activeFavorite) || matches[0];

  return (
    <div className="relative w-1/6">
      <Listbox value={activeMatch.id} onChange={onChange}>
        <div className="relative">
          <Listbox.Button className="relative cursor-pointer rounded-lg border border-border bg-card p-3 pr-10 text-left shadow-sm transition hover:bg-primary/5 focus:outline-none focus:ring-2 focus:ring-primary/30 ">
            <span className="block truncate">
              {activeMatch.name}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            </span>
          </Listbox.Button>

          <Transition
            enter="transition ease-out duration-100"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-card py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              {matches.map((match) => (
                <Listbox.Option
                  key={match.id}
                  className={({ active }) =>
                    `relative cursor-pointer select-none py-2 pl-10 pr-4 ${
                      active ? "bg-primary/10 text-primary" : "text-foreground"
                    }`
                  }
                  value={match.id}
                >
                  {({ selected }) => (
                    <>
                      <span className={`block truncate ${selected ? "font-medium" : "font-normal"}`}>
                        {match.name} 
                      </span>
                      {selected && (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-primary">
                          <Check className="h-5 w-5" />
                        </span>
                      )}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
    </div>
  );
};

export default MatchSelect;
