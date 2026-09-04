"use client";

import { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Link from "next/link";
import { API_URL } from "@/lib/config";

interface DashboardSummary {
  totalClientes: number;
  apolicesAtivas: number;
  apolicesEmRisco30d: number;
  probabilidadeMediaRenovacao: number | null;
}

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 3, borderRadius: 3, height: "100%" }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h3" sx={{ fontWeight: 800, my: 1 }}>
        {value}
      </Typography>
      {hint && (
        <Typography variant="caption" color="text.secondary">
          {hint}
        </Typography>
      )}
    </Paper>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/data/dashboard`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error("Falha ao carregar indicadores");
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Painel da carteira
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Indicadores de uso, receita e renovação da carteira — os mesmos grupos
        de métricas discutidos na apresentação.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "repeat(4, 1fr)" },
          gap: 3,
          mb: 4,
        }}
      >
        {data ? (
          <>
            <StatCard label="Clientes ativos" value={String(data.totalClientes)} hint="Licenças/usuários ativos" />
            <StatCard label="Apólices ativas" value={String(data.apolicesAtivas)} hint="Uso e adoção" />
            <StatCard
              label="Vencendo em 30 dias"
              value={String(data.apolicesEmRisco30d)}
              hint="Prioridade de contato"
            />
            <StatCard
              label="Renovação média prevista"
              value={
                data.probabilidadeMediaRenovacao !== null
                  ? `${data.probabilidadeMediaRenovacao}%`
                  : "—"
              }
              hint="Receita e retenção"
            />
          </>
        ) : (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="rounded" height={130} />
          ))
        )}
      </Box>

      <Paper variant="outlined" sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Quer saber quem precisa de atenção agora?
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Pergunte ao assistente de IA quais apólices estão em risco nos
          próximos 30 dias, ou peça para ele registrar um contato de renovação.
        </Typography>
        <Button component={Link} href="/chat" variant="contained">
          Abrir o assistente de IA
        </Button>
      </Paper>
    </Box>
  );
}
