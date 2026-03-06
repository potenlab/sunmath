"use client";

import { useRouter } from "@/i18n/navigation";
import { BookOpen } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { useStudentProblems } from "@/features/student/api/use-problems";

export default function StudentProblemsPage() {
  const router = useRouter();
  const { data: problemsData, isLoading } = useStudentProblems();
  const problems = problemsData?.problems ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        icon={BookOpen}
        iconGradient="from-blue-400 to-cyan-500"
        title="Problems"
        description="Browse available math problems and submit your answers"
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      ) : problems.length === 0 ? (
        <Card className="shadow-sm">
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">
              No problems available yet. Check back later!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {problems.map((problem) => (
            <Card
              key={problem.id}
              className="shadow-sm hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => router.push(`/student/problems/${problem.id}`)}
            >
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <p className="text-sm font-medium line-clamp-3 group-hover:text-blue-600 transition-colors">
                    {problem.content}
                  </p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className="text-xs">
                      {problem.expected_form}
                    </Badge>
                    {problem.target_grade && (
                      <Badge variant="secondary" className="text-xs">
                        Grade {problem.target_grade}
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Problem #{problem.id}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
