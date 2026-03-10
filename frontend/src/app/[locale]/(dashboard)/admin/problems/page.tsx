"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { FileText, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { ProblemManager } from "@/features/admin/components/problem-manager";
import { useAdminSettings } from "@/features/admin/hooks/use-admin-settings";
import { useProblems, useDeleteProblem } from "@/features/admin/api/use-problems";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function AdminProblemsPage() {
  const t = useTranslations("admin");
  const tp = useTranslations("problemsPage");
  const tc = useTranslations("common");
  const { duplicateMode } = useAdminSettings();
  const { data: problemsData, isLoading } = useProblems();
  const deleteMutation = useDeleteProblem();

  const problems = problemsData?.problems ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        icon={FileText}
        iconGradient="from-amber-400 to-orange-500"
        title={tp("title")}
        description={tp("description")}
      />

      <ProblemManager
        duplicateMode={duplicateMode}
        onProblemsCountChange={() => {}}
      />

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{tp("allProblems")}</CardTitle>
          <CardDescription>
            {tp("problemsRegistered", { count: problemsData?.total ?? 0 })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-500" />
            </div>
          ) : problems.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              {tp("noProblems")}
            </p>
          ) : (
            <div className="space-y-2">
              {problems.map((problem) => (
                <Link
                  key={problem.id}
                  href={`/admin/problems/${problem.id}`}
                  className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {problem.content}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {problem.expected_form}
                      </Badge>
                      {problem.target_grade && (
                        <Badge variant="secondary" className="text-xs">
                          {tc("grade", { grade: problem.target_grade })}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">
                        ID: {problem.id}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        deleteMutation.mutate(problem.id);
                      }}
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
