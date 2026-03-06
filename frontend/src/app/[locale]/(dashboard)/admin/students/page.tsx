"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { Users, Plus, Trash2, Pencil } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  useStudents,
  useCreateStudent,
  useUpdateStudent,
  useDeleteStudent,
} from "@/features/admin/api/use-students-crud";

export default function AdminStudentsPage() {
  const t = useTranslations("students");
  const router = useRouter();
  const { data: studentsData, isLoading } = useStudents();
  const createMutation = useCreateStudent();
  const updateMutation = useUpdateStudent();
  const deleteMutation = useDeleteStudent();

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formName, setFormName] = useState("");
  const [formGrade, setFormGrade] = useState("");

  const students = studentsData?.students ?? [];

  const handleAdd = async () => {
    if (!formName.trim()) return;
    await createMutation.mutateAsync({
      name: formName,
      grade_level: formGrade ? parseInt(formGrade, 10) : null,
    });
    setFormName("");
    setFormGrade("");
    setShowAddDialog(false);
  };

  const handleUpdate = async () => {
    if (editingId === null || !formName.trim()) return;
    await updateMutation.mutateAsync({
      id: editingId,
      name: formName,
      grade_level: formGrade ? parseInt(formGrade, 10) : null,
    });
    setEditingId(null);
    setFormName("");
    setFormGrade("");
  };

  const startEdit = (student: { id: number; name: string; grade_level: number | null }) => {
    setEditingId(student.id);
    setFormName(student.name);
    setFormGrade(student.grade_level?.toString() ?? "");
    setShowAddDialog(false);
  };

  const cancelForm = () => {
    setShowAddDialog(false);
    setEditingId(null);
    setFormName("");
    setFormGrade("");
  };

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Users}
        iconGradient="from-violet-400 to-purple-500"
        title={t("title")}
        description={t("description")}
      />

      <div className="grid gap-4 md:grid-cols-2">
        <StatCard
          icon={Users}
          value={studentsData?.total ?? 0}
          label={t("totalStudents")}
          colorScheme="violet"
        />
      </div>

      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg">{t("studentList")}</CardTitle>
            <CardDescription>{t("studentListDesc")}</CardDescription>
          </div>
          <Button
            size="sm"
            onClick={() => {
              cancelForm();
              setShowAddDialog(true);
            }}
            className="bg-gradient-to-r from-violet-500 to-purple-600 text-white"
          >
            <Plus className="size-4 mr-1" />
            Add Student
          </Button>
        </CardHeader>
        <CardContent>
          {/* Add/Edit Form */}
          {(showAddDialog || editingId !== null) && (
            <div className="mb-4 rounded-lg border bg-muted/30 p-4 space-y-3">
              <h3 className="text-sm font-semibold">
                {editingId !== null ? "Edit Student" : "New Student"}
              </h3>
              <div className="grid gap-3 sm:grid-cols-2">
                <input
                  type="text"
                  placeholder="Student name"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                />
                <input
                  type="number"
                  placeholder="Grade level"
                  value={formGrade}
                  onChange={(e) => setFormGrade(e.target.value)}
                  className="rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={editingId !== null ? handleUpdate : handleAdd}
                  disabled={!formName.trim()}
                >
                  {editingId !== null ? "Save" : "Add"}
                </Button>
                <Button size="sm" variant="outline" onClick={cancelForm}>
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-violet-500" />
            </div>
          ) : students.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No students yet.
            </p>
          ) : (
            <div className="space-y-2">
              {students.map((student) => (
                <div
                  key={student.id}
                  className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => router.push(`/admin/students/${student.id}`)}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-violet-400 to-purple-500 text-sm font-bold text-white">
                      {student.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{student.name}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {student.grade_level && (
                          <Badge variant="secondary" className="text-xs">
                            Grade {student.grade_level}
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          ID: {student.id}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => startEdit(student)}
                    >
                      <Pencil className="size-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                      onClick={() => deleteMutation.mutate(student.id)}
                    >
                      <Trash2 className="size-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
