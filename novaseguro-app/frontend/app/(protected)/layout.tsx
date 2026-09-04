import { cookies } from "next/headers";
import AppShell from "@/components/AppShell";
import { API_URL, SESSION_COOKIE_NAME } from "@/lib/config";

interface CurrentUser {
  name: string;
  email: string;
  role: string;
}

interface CurrentTenant {
  slug: string;
  nomeEmpresa: string;
  headerColor: string;
  hasLogo: boolean;
}

async function fetchMe(): Promise<{ user: CurrentUser | null; tenant: CurrentTenant | null }> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE_NAME)?.value;
  if (!token) return { user: null, tenant: null };

  try {
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Cookie: `${SESSION_COOKIE_NAME}=${token}` },
      cache: "no-store",
    });
    if (!res.ok) return { user: null, tenant: null };
    const data = await res.json();
    return { user: data.user ?? null, tenant: data.tenant ?? null };
  } catch {
    return { user: null, tenant: null };
  }
}

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, tenant } = await fetchMe();
  return (
    <AppShell user={user} tenant={tenant}>
      {children}
    </AppShell>
  );
}
