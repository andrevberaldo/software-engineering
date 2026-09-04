"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Stack from "@mui/material/Stack";
import Link from "next/link";
import { API_URL } from "@/lib/config";
import { getBrowserHost } from "@/lib/tenant";

interface Branding {
  slug: string;
  nomeEmpresa: string;
  headerColor: string;
  hasLogo: boolean;
}

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const from = searchParams.get("from") || "/dashboard";

  const [email, setEmail] = useState("admin@novaseguro.com.br");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [branding, setBranding] = useState<Branding | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/public/branding?host=${encodeURIComponent(getBrowserHost())}`)
      .then((res) => (res.ok ? res.json() : null))
      .then(setBranding)
      .catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(
        `${API_URL}/auth/login?host=${encodeURIComponent(getBrowserHost())}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email, password }),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Não foi possível entrar");
        return;
      }

      router.push(from);
      router.refresh();
    } catch {
      setError("Não foi possível contatar o servidor. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: branding?.headerColor ?? "primary.main",
        p: 2,
      }}
    >
      <Paper sx={{ p: 4, width: "100%", maxWidth: 400, borderRadius: 3 }}>
        {branding?.hasLogo && (
          <Box
            component="img"
            src={`${API_URL}/public/tenants/${branding.slug}/logo`}
            alt={branding.nomeEmpresa}
            sx={{ height: 40, maxWidth: "100%", objectFit: "contain", mb: 1.5 }}
          />
        )}
        <Typography variant="h5" sx={{ mb: 0.5, fontWeight: 700 }}>
          {branding?.nomeEmpresa ?? "NovaSeguro"} Copiloto
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Entre com sua conta para acessar a ferramenta.
        </Typography>

        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Senha"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              fullWidth
            />
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? "Entrando..." : "Entrar"}
            </Button>
          </Stack>
        </form>

        <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 3 }}>
          Ambiente de demonstração — usuário padrão: admin@novaseguro.com.br / senha: admin
        </Typography>

        <Typography variant="body2" sx={{ mt: 2 }}>
          <Link href="/">← Voltar para a página inicial</Link>
        </Typography>
      </Paper>
    </Box>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
