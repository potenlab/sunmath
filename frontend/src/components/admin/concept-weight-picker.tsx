"use client";

import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Plus, X, Search } from "lucide-react";
import type { ConceptOption } from "@/features/admin/types";

interface ConceptWeightEntry {
  conceptId: number;
  name: string;
  weight: number;
}

interface ConceptWeightPickerProps {
  concepts: ConceptOption[];
  entries: ConceptWeightEntry[];
  onChange: (entries: ConceptWeightEntry[]) => void;
  isLoading?: boolean;
}

export type { ConceptWeightEntry };

export function ConceptWeightPicker({
  concepts,
  entries,
  onChange,
  isLoading = false,
}: ConceptWeightPickerProps) {
  const [search, setSearch] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const selectedIds = new Set(entries.map((e) => e.conceptId));

  const filtered = useMemo(() => {
    if (!search.trim()) return concepts.filter((c) => !selectedIds.has(c.id));
    const q = search.toLowerCase();
    return concepts.filter(
      (c) =>
        !selectedIds.has(c.id) &&
        (c.name.toLowerCase().includes(q) ||
          c.category?.toLowerCase().includes(q))
    );
  }, [concepts, search, selectedIds]);

  const handleAdd = (concept: ConceptOption) => {
    onChange([...entries, { conceptId: concept.id, name: concept.name, weight: 1.0 }]);
    setSearch("");
    setDropdownOpen(false);
  };

  const handleRemove = (conceptId: number) => {
    onChange(entries.filter((e) => e.conceptId !== conceptId));
  };

  const handleWeightChange = (conceptId: number, weight: number) => {
    onChange(
      entries.map((e) =>
        e.conceptId === conceptId ? { ...e, weight } : e
      )
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">Concept Weights</label>
        <div className="rounded-md border bg-muted/20 p-4 text-center text-sm text-muted-foreground">
          Loading concepts...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium">Concept Weights</label>

      {/* Search & add */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
          <Input
            placeholder="Search concepts to add..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setDropdownOpen(true);
            }}
            onFocus={() => setDropdownOpen(true)}
            onBlur={() => {
              // Delay so click on item registers
              setTimeout(() => setDropdownOpen(false), 200);
            }}
            className="pl-8 text-sm"
          />
        </div>

        {dropdownOpen && filtered.length > 0 && (
          <div className="absolute z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-md border bg-white shadow-md">
            {filtered.slice(0, 20).map((concept) => (
              <button
                key={concept.id}
                type="button"
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-muted/50"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleAdd(concept)}
              >
                <Plus className="size-3 shrink-0 text-muted-foreground" />
                <span className="truncate">{concept.name}</span>
                {concept.category && (
                  <Badge variant="outline" className="ml-auto shrink-0 text-[10px]">
                    {concept.category}
                  </Badge>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected concepts with weight sliders */}
      {entries.length > 0 && (
        <div className="space-y-2">
          {entries.map((entry) => (
            <div
              key={entry.conceptId}
              className="flex items-center gap-3 rounded-lg border bg-muted/10 px-3 py-2"
            >
              <span className="min-w-0 flex-shrink-0 truncate text-sm font-medium">
                {entry.name}
              </span>
              <div className="flex min-w-0 flex-1 items-center gap-2">
                <Slider
                  value={[entry.weight * 100]}
                  onValueChange={([v]) =>
                    handleWeightChange(entry.conceptId, Math.round(v) / 100)
                  }
                  min={0}
                  max={100}
                  step={5}
                  className="flex-1"
                />
                <span className="w-10 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
                  {entry.weight.toFixed(2)}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="size-6 shrink-0 p-0 text-muted-foreground hover:text-red-600"
                onClick={() => handleRemove(entry.conceptId)}
              >
                <X className="size-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {entries.length === 0 && (
        <p className="text-xs text-muted-foreground">
          No concepts selected. Search above to add concepts, or leave empty for auto-extraction.
        </p>
      )}
    </div>
  );
}
