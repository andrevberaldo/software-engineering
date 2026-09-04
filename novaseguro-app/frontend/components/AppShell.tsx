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

const NAV_ITEMS = [
  { label: "Painel", href: "/dashboard" },
  { label: "Assistente de IA", href: "/chat" },
  { label: "Clientes", href: "/clientes" },
  { label: "Documentos", href: "/documentos" },
];

export default function AppShell({
  user,
  children,
}: {
  user: { name: string; email: string } | null;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const currentTab = NAV_ITEMS.find((item) => pathname.startsWith(item.href))?.href ?? false;

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
      <AppBar position="static" elevation={0}>
        <Toolbar sx={{ maxWidth: 1200, width: "100%", mx: "auto" }}>
          <Typography
            component={Link}
            href="/dashboard"
            variant="h6"
            sx={{ fontWeight: 800, color: "inherit", textDecoration: "none", mr: 4 }}
          >
            NovaSeguro
          </Typography>

          <Tabs
            value={currentTab}
            textColor="inherit"
            sx={{
              flexGrow: 1,
              "& .MuiTabs-indicator": { backgroundColor: "secondary.main" },
            }}
          >
            {NAV_ITEMS.map((item) => (
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
