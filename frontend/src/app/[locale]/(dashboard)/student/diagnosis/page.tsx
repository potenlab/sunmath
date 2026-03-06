"use client";

import { Brain, Sparkles } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { useAuth } from "@/features/auth/context/auth-context";
import { StudentDetail } from "@/features/students/components/detail.students";

export default function StudentDiagnosisPage() {
  const { user } = useAuth();

  if (!user?.student_id) {
    return (
      <div className="space-y-8">
        <PageHeader
          icon={Brain}
          iconGradient="from-violet-400 to-purple-500"
          title="My Diagnosis"
          description="View your learning analysis and recommendations"
        />
        <Card className="shadow-sm">
          <CardContent className="py-12">
            <p className="text-center text-muted-foreground">
              No student profile linked to your account. Contact your teacher.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Brain}
        iconGradient="from-violet-400 to-purple-500"
        title="My Diagnosis"
        description="View your learning analysis and recommendations"
      />

      <StudentDetail id={String(user.student_id)} />

      {/* LoRA Handwriting Analysis Placeholder */}
      <Card className="border-dashed border-2 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="size-5 text-amber-500" />
            LoRA Handwriting Analysis
            <Badge variant="secondary" className="text-xs">
              Coming Soon
            </Badge>
          </CardTitle>
          <CardDescription>
            AI-powered handwriting analysis to identify common mistakes in your
            written math work. This feature uses LoRA fine-tuned models to
            analyze your handwriting patterns.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 rounded-lg bg-muted/30">
            <div className="text-center space-y-2">
              <Sparkles className="size-10 text-amber-400 mx-auto" />
              <p className="text-sm text-muted-foreground">
                This feature is under development
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
