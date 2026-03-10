import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Brain } from "lucide-react";
import type { ConceptFrequency } from "@/features/students/types";

interface RootCauseGraphProps {
  /** Root cause concepts identified by diagnosis */
  coreWeaknesses: string[];
  /** Prerequisite chains: each chain is an array of concept names */
  prerequisiteChains: string[][];
  /** Concept frequency data (includes mastery) */
  conceptFrequencies: ConceptFrequency[];
}

export function RootCauseGraph({
  coreWeaknesses,
  prerequisiteChains,
  conceptFrequencies,
}: RootCauseGraphProps) {
  const t = useTranslations("studentDetail");

  // Build a mastery lookup from concept frequencies
  const masteryMap = new Map<string, number>();
  for (const cf of conceptFrequencies) {
    masteryMap.set(cf.concept_name, cf.mastery);
  }

  // Determine the prerequisite (upstream) concept — the first item in the longest chain
  // and the "affected" concepts — everything downstream of core weaknesses
  const longestChain = prerequisiteChains.reduce(
    (longest, chain) => (chain.length > longest.length ? chain : longest),
    [] as string[],
  );

  // Upstream: concepts that appear before core weaknesses in chains
  const coreSet = new Set(coreWeaknesses);
  const upstreamConcepts: string[] = [];
  const downstreamConcepts: string[] = [];

  for (const chain of prerequisiteChains) {
    let foundCore = false;
    for (const concept of chain) {
      if (coreSet.has(concept)) {
        foundCore = true;
        continue;
      }
      if (!foundCore) {
        if (!upstreamConcepts.includes(concept)) upstreamConcepts.push(concept);
      } else {
        if (!downstreamConcepts.includes(concept)) downstreamConcepts.push(concept);
      }
    }
  }

  // If there are no clear upstream/downstream from chains, use concept frequencies
  // as affected concepts (excluding core weaknesses)
  const affected =
    downstreamConcepts.length > 0
      ? downstreamConcepts
      : conceptFrequencies
          .filter((c) => !coreSet.has(c.concept_name))
          .slice(0, 4)
          .map((c) => c.concept_name);

  // If no prerequisite chains, show a simplified view
  if (coreWeaknesses.length === 0) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Brain className="size-4 text-amber-500" />
            {t("rootCauseTracing")}
          </CardTitle>
          <CardDescription>{t("rootCauseTracingDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="py-6 text-center text-sm text-muted-foreground">
            {t("noConcepts")}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Brain className="size-4 text-amber-500" />
          {t("rootCauseTracing")}
        </CardTitle>
        <CardDescription>{t("rootCauseTracingDesc")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-center py-6">
          <div className="flex items-center gap-3 flex-wrap justify-center">
            {/* Upstream prerequisites (if any) */}
            {upstreamConcepts.length > 0 && (
              <>
                <div className="flex flex-col gap-2">
                  {upstreamConcepts.slice(0, 3).map((concept) => (
                    <div
                      key={concept}
                      className="rounded-lg border-2 border-amber-300 bg-amber-50 px-4 py-2 text-center"
                    >
                      <p className="text-xs font-semibold text-amber-700">
                        {t("rootCauseLabel")}
                      </p>
                      <p className="text-sm font-bold text-amber-900">{concept}</p>
                      {masteryMap.has(concept) && (
                        <p className="text-[10px] text-amber-600">
                          {t("mastery")}: {masteryMap.get(concept)!.toFixed(2)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
                <div className="text-2xl text-muted-foreground/40">&rarr;</div>
              </>
            )}

            {/* Core weaknesses */}
            <div className="flex flex-col gap-2">
              {coreWeaknesses.map((weakness) => (
                <div
                  key={weakness}
                  className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-2 text-center"
                >
                  <p className="text-xs font-semibold text-red-700">
                    {t("coreWeakness")}
                  </p>
                  <p className="text-sm font-bold text-red-900">{weakness}</p>
                  {masteryMap.has(weakness) && (
                    <p className="text-[10px] text-red-600">
                      {t("mastery")}: {masteryMap.get(weakness)!.toFixed(2)}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {/* Affected concepts */}
            {affected.length > 0 && (
              <>
                <div className="text-2xl text-muted-foreground/40">&rarr;</div>
                <div className="flex flex-col gap-2">
                  {affected.slice(0, 4).map((concept) => (
                    <div
                      key={concept}
                      className="rounded-lg border bg-muted/50 px-3 py-1.5 text-center"
                    >
                      <p className="text-xs font-medium">{concept}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
