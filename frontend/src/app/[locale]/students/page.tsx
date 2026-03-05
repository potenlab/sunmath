import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, ChevronRight, TrendingDown, BookOpen } from "lucide-react";
import { Link } from "@/i18n/navigation";

export default function StudentsPage() {
  const t = useTranslations("students");

  const mockStudents = [
    {
      id: "1",
      name: t("studentA"),
      grade: t("highSchool2"),
      wrongAnswers: 8,
      rootCause: t("completingTheSquare"),
      mastery: 0.3,
      status: "needs-attention" as const,
    },
    {
      id: "2",
      name: t("studentB"),
      grade: t("highSchool1"),
      wrongAnswers: 5,
      rootCause: t("radianMeasure"),
      mastery: 0.45,
      status: "improving" as const,
    },
    {
      id: "3",
      name: t("studentC"),
      grade: t("middleSchool3"),
      wrongAnswers: 2,
      rootCause: null,
      mastery: 0.82,
      status: "on-track" as const,
    },
  ];

  const statusConfig = {
    "needs-attention": {
      label: t("needsAttention"),
      className: "bg-red-100 text-red-700 hover:bg-red-100",
    },
    improving: {
      label: t("improving"),
      className: "bg-amber-100 text-amber-700 hover:bg-amber-100",
    },
    "on-track": {
      label: t("onTrack"),
      className: "bg-emerald-100 text-emerald-700 hover:bg-emerald-100",
    },
  };

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 shadow-sm">
            <Users className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{t("title")}</h1>
            <p className="text-sm text-muted-foreground">{t("description")}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-none bg-gradient-to-br from-violet-50 to-purple-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
              <Users className="size-6 text-violet-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-violet-700">3</p>
              <p className="text-xs text-violet-600/70">{t("totalStudents")}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none bg-gradient-to-br from-red-50 to-rose-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100">
              <TrendingDown className="size-6 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-red-700">1</p>
              <p className="text-xs text-red-600/70">{t("needAttention")}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none bg-gradient-to-br from-amber-50 to-orange-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100">
              <BookOpen className="size-6 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-700">15</p>
              <p className="text-xs text-amber-600/70">{t("totalWrongAnswers")}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("studentList")}</CardTitle>
          <CardDescription>{t("studentListDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockStudents.map((student) => {
              const status = statusConfig[student.status];
              return (
                <Link
                  key={student.id}
                  href={`/students/${student.id}`}
                  className="group flex items-center gap-4 rounded-xl border p-4 transition-all hover:border-primary/30 hover:bg-accent/50 hover:shadow-sm"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-violet-100 to-purple-100 text-sm font-bold text-violet-600">
                    {student.name.charAt(student.name.length - 1)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold">{student.name}</p>
                      <Badge className={status.className}>{status.label}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {student.grade}
                      {student.rootCause && (
                        <span>
                          {" "}&middot; {t("rootCause")}:{" "}
                          <span className="font-medium text-foreground/70">{student.rootCause}</span>
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-lg font-bold">{student.wrongAnswers}</p>
                    <p className="text-[11px] text-muted-foreground">{t("wrongAnswers")}</p>
                  </div>
                  <ChevronRight className="size-4 text-muted-foreground/40 transition-transform group-hover:translate-x-0.5" />
                </Link>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
