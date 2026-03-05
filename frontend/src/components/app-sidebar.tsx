"use client";

import { usePathname } from "@/i18n/navigation";
import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
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
  SidebarMenuBadge,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Settings,
  ClipboardCheck,
  Users,
  Sun,
} from "lucide-react";

export function AppSidebar() {
  const pathname = usePathname();
  const t = useTranslations();

  const navItems = [
    {
      title: t("nav.adminPanel"),
      href: "/admin" as const,
      icon: Settings,
      description: t("nav.adminDesc"),
    },
    {
      title: t("nav.grading"),
      href: "/grading" as const,
      icon: ClipboardCheck,
      description: t("nav.gradingDesc"),
    },
    {
      title: t("nav.students"),
      href: "/students" as const,
      icon: Users,
      description: t("nav.studentsDesc"),
      badge: "3",
    },
  ];

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
                    {item.badge && (
                      <SidebarMenuBadge>
                        <Badge
                          variant="secondary"
                          className="h-5 min-w-5 justify-center rounded-full bg-sidebar-primary/20 px-1.5 text-[10px] font-semibold text-sidebar-primary"
                        >
                          {item.badge}
                        </Badge>
                      </SidebarMenuBadge>
                    )}
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

      </SidebarContent>

      <SidebarFooter className="px-5 py-4">
        <div className="rounded-lg bg-sidebar-accent/50 p-3">
          <p className="text-[11px] font-medium text-sidebar-foreground/70">
            {t("common.mvpDemo")}
          </p>
          <p className="text-[10px] text-sidebar-foreground/40">
            {t("common.daechiDong")}
          </p>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
