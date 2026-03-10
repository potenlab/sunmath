"use client";

import { usePathname } from "@/i18n/navigation";
import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/features/auth/context/auth-context";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Settings,
  ClipboardCheck,
  Users,
  Sun,
  LogOut,
  BookOpen,
  Brain,
  FileText,
} from "lucide-react";

export function AppSidebar() {
  const pathname = usePathname();
  const t = useTranslations();
  const { user, logout } = useAuth();

  const adminNavItems = [
    {
      title: t("sidebar.problems"),
      href: "/admin/problems" as const,
      icon: FileText,
      description: t("sidebar.problemsDesc"),
    },
    {
      title: t("nav.grading"),
      href: "/admin/grading" as const,
      icon: ClipboardCheck,
      description: t("nav.gradingDesc"),
    },
    {
      title: t("nav.students"),
      href: "/admin/students" as const,
      icon: Users,
      description: t("nav.studentsDesc"),
    },
    {
      title: t("sidebar.settings"),
      href: "/admin/settings" as const,
      icon: Settings,
      description: t("sidebar.settingsDesc"),
    },
  ];

  const studentNavItems = [
    {
      title: t("sidebar.studentProblems"),
      href: "/student/problems" as const,
      icon: BookOpen,
      description: t("sidebar.studentProblemsDesc"),
    },
    {
      title: t("sidebar.myDiagnosis"),
      href: "/student/diagnosis" as const,
      icon: Brain,
      description: t("sidebar.myDiagnosisDesc"),
    },
  ];

  const navItems = user?.role === "admin" ? adminNavItems : studentNavItems;

  return (
    <Sidebar>
      <SidebarHeader className="px-5 py-5">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 shadow-sm">
            <Sun className="size-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight">{t("common.sunmath")}</span>
            <p className="text-[11px] leading-tight text-sidebar-foreground/60">
              {t("common.aiPlatform")}
            </p>
          </div>
        </Link>
      </SidebarHeader>

      <Separator className="bg-sidebar-border" />

      <SidebarContent className="px-2 pt-2">
        <SidebarGroup>
          <SidebarGroupLabel className="text-[11px] uppercase tracking-wider text-sidebar-foreground/40">
            {t("nav.main")}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const isActive = pathname.startsWith(item.href);
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      className="h-auto py-2.5"
                    >
                      <Link href={item.href}>
                        <item.icon className="size-4" />
                        <div className="flex flex-col">
                          <span className="text-sm font-medium">{item.title}</span>
                          <span className="text-[11px] text-sidebar-foreground/50">
                            {item.description}
                          </span>
                        </div>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="px-5 py-4">
        {user && (
          <div className="mb-2 flex items-center justify-between rounded-lg bg-sidebar-accent/50 p-3">
            <div>
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-[11px] text-sidebar-foreground/50">{user.role}</p>
            </div>
            <button
              onClick={logout}
              className="rounded-md p-1.5 hover:bg-sidebar-accent transition-colors"
              title={t("sidebar.logout")}
            >
              <LogOut className="size-4 text-sidebar-foreground/60" />
            </button>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
