export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-amber-50 to-orange-50 dark:from-neutral-950 dark:to-neutral-900 p-4">
      {children}
    </div>
  );
}
