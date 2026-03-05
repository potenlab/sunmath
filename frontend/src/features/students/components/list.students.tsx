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
import { getMockStudents } from "../data/mock";

export function StudentList() {
  const t = useTranslations("students");
  const mockStudents = getMockStudents(t);

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
          value={3}
          label={t("totalStudents")}
          colorScheme="violet"
        />
        <StatCard
          icon={TrendingDown}
          value={1}
          label={t("needAttention")}
          colorScheme="red"
        />
        <StatCard
          icon={BookOpen}
          value={15}
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
            {mockStudents.map((student) => (
              <StudentCard key={student.id} student={student} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
