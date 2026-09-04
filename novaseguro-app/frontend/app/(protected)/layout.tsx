import { cookies } from "next/headers";
import AppShell from "@/components/AppShell";
import { API_URL, SESSION_COOKIE_NAME } from "@/lib/config";

async function fetchCurrentUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE_NAME)?.value;
  if (!token) return null;

  try {
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Cookie: `${SESSION_COOKIE_NAME}=${token}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.user as { name: string; email: string };
  } catch {
    return null;
  }
}

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await fetchCurrentUser();
  return <AppShell user={user}>{children}</AppShell>;
}
