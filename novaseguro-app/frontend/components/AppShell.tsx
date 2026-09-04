"use client";

import { useRouter, usePathname } from "next/navigation";
import Box from "@mui/material/Box";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Container from "@mui/material/Container";
import Avatar from "@mui/material/Avatar";
import Stack from "@mui/material/Stack";
import Link from "next/link";
import { API_URL } from "@/lib/config";

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

const NAV_ITEMS = [
  { label: "Painel", href: "/dashboard" },
  { label: "Assistente de IA", href: "/chat" },
  { label: "Clientes", href: "/clientes" },
  { label: "Documentos", href: "/documentos" },
];

const ADMIN_NAV_ITEM = { label: "Configurações", href: "/configuracoes/identidade-visual" };

export default function AppShell({
  user,
  tenant,
  children,
}: {
  user: CurrentUser | null;
  tenant: CurrentTenant | null;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const navItems = user?.role === "admin" ? [...NAV_ITEMS, ADMIN_NAV_ITEM] : NAV_ITEMS;
  const currentTab = navItems.find((item) => pathname.startsWith(item.href))?.href ?? false;

  async function handleLogout() {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    router.push("/");
    router.refresh();
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar position="static" elevation={0} sx={tenant ? { bgcolor: tenant.headerColor } : undefined}>
        <Toolbar sx={{ maxWidth: 1200, width: "100%", mx: "auto" }}>
          <Box
            component={Link}
            href="/dashboard"
            sx={{ display: "flex", alignItems: "center", mr: 4, textDecoration: "none", color: "inherit" }}
          >
            {tenant?.hasLogo ? (
              <Box
                component="img"
                src={`${API_URL}/public/tenants/${tenant.slug}/logo`}
                alt={tenant.nomeEmpresa}
                sx={{ height: 32, maxWidth: 160, objectFit: "contain" }}
              />
            ) : (
              <Typography variant="h6" sx={{ fontWeight: 800 }}>
                {tenant?.nomeEmpresa ?? "NovaSeguro"}
              </Typography>
            )}
          </Box>

          <Tabs
            value={currentTab}
            textColor="inherit"
            sx={{
              flexGrow: 1,
              "& .MuiTabs-indicator": { backgroundColor: "secondary.main" },
            }}
          >
            {navItems.map((item) => (
              <Tab
                key={item.href}
                label={item.label}
                value={item.href}
                component={Link}
                href={item.href}
                sx={{ color: "white", opacity: 0.85, "&.Mui-selected": { opacity: 1 } }}
              />
            ))}
          </Tabs>

          <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: "secondary.main", fontSize: 14 }}>
              {(user?.name || "?").charAt(0).toUpperCase()}
            </Avatar>
            <Typography variant="body2" sx={{ display: { xs: "none", sm: "block" } }}>
              {user?.name || "Usuário"}
            </Typography>
            <Button color="inherit" size="small" onClick={handleLogout}>
              Sair
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {children}
      </Container>
    </Box>
  );
}
