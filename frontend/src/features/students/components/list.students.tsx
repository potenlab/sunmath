import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Users, TrendingDown, BookOpen } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { StudentCard } from "@/components/students/student-card";
import { useStudentSummaries } from "../api/use-student-data";
import type { StudentSummary } from "../types";

const GRADE_MAP: Record<number, string> = {
  7: "middleSchool1",
  8: "middleSchool2",
  9: "middleSchool3",
  10: "highSchool1",
  11: "highSchool2",
  12: "highSchool3",
};

export function StudentList() {
  const t = useTranslations("students");
  const { data, isLoading } = useStudentSummaries();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const students: StudentSummary[] = (data?.students ?? []).map((s) => ({
    id: String(s.id),
    name: s.name,
    grade: s.grade_level ? t(GRADE_MAP[s.grade_level] ?? "-") : "-",
    wrongAnswers: s.wrong_answers,
    rootCause: s.root_cause,
    mastery: s.mastery,
    status: s.status,
  }));

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Users}
        iconGradient="from-violet-400 to-purple-500"
        title={t("title")}
        description={t("description")}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          icon={Users}
          value={data?.total ?? 0}
          label={t("totalStudents")}
          colorScheme="violet"
        />
        <StatCard
          icon={TrendingDown}
          value={data?.needs_attention ?? 0}
          label={t("needAttention")}
          colorScheme="red"
        />
        <StatCard
          icon={BookOpen}
          value={data?.total_wrong_answers ?? 0}
          label={t("totalWrongAnswers")}
          colorScheme="amber"
        />
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("studentList")}</CardTitle>
          <CardDescription>{t("studentListDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {students.map((student) => (
              <StudentCard key={student.id} student={student} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
