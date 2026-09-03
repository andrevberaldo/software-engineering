"use client";

import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import Link from "next/link";
import PublicNav from "@/components/PublicNav";
import SearchIcon from "@mui/icons-material/Search";
import HubIcon from "@mui/icons-material/Hub";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";

const FEATURES = [
  {
    icon: <SearchIcon fontSize="large" />,
    title: "Consulta inteligente a apólices",
    description:
      "O assistente responde dúvidas de cobertura, franquia e carência consultando os manuais das seguradoras parceiras — sempre citando a fonte.",
  },
  {
    icon: <HubIcon fontSize="large" />,
    title: "Visão relacionada do cliente",
    description:
      "Entenda de uma vez como cada cliente se conecta a apólices, seguradoras e sinistros, em vez de olhar um documento isolado por vez.",
  },
  {
    icon: <TrendingUpIcon fontSize="large" />,
    title: "Previsão de receita e cancelamento",
    description:
      "A cada apólice, o copiloto estima a chance de renovação e projeta a receita futura, com base em sinais reais de uso e relacionamento.",
  },
  {
    icon: <NotificationsActiveIcon fontSize="large" />,
    title: "Renovação antecipada",
    description:
      "Clientes de baixo risco recebem um lembrete automático direto do sistema; casos sensíveis são priorizados para um corretor humano.",
  },
];

export default function HomePage() {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <PublicNav />

      <Box
        sx={{
          bgcolor: "primary.main",
          color: "white",
          py: { xs: 8, md: 12 },
        }}
      >
        <Container maxWidth="md">
          <Chip
            label="Corretora de seguros · Assistente de IA"
            sx={{ bgcolor: "rgba(255,255,255,0.12)", color: "white", mb: 3 }}
          />
          <Typography variant="h2" sx={{ fontSize: { xs: "2.2rem", md: "3rem" }, mb: 2 }}>
            O copiloto de IA da NovaSeguro Corretora
          </Typography>
          <Typography variant="h6" sx={{ fontWeight: 400, opacity: 0.9, mb: 4 }}>
            Uma ferramenta interna que ajuda corretores a responder clientes mais
            rápido, entender o que conecta cada apólice e antecipar renovações
            antes que elas virem cancelamento.
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              component={Link}
              href="/login"
              variant="contained"
              color="secondary"
              size="large"
              sx={{ fontWeight: 700, px: 4 }}
            >
              Entrar na ferramenta
            </Button>
          </Stack>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Do atendimento manual ao atendimento assistido por IA
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 5, maxWidth: 720 }}>
          Apólices de seguro são renovadas periodicamente, assim como uma assinatura.
          O copiloto usa isso a favor do negócio: consulta documentos, entende
          relações entre clientes e seguradoras, e age antes da data de vencimento.
        </Typography>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
            gap: 3,
          }}
        >
          {FEATURES.map((f) => (
            <Paper
              key={f.title}
              variant="outlined"
              sx={{ p: 3, height: "100%", borderRadius: 3 }}
            >
              <Box sx={{ color: "primary.main", mb: 1.5 }}>{f.icon}</Box>
              <Typography variant="h6" sx={{ mb: 1 }}>
                {f.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {f.description}
              </Typography>
            </Paper>
          ))}
        </Box>
      </Container>

      <Box sx={{ bgcolor: "grey.100", py: { xs: 6, md: 8 } }}>
        <Container maxWidth="md" sx={{ textAlign: "center" }}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Acesso restrito à equipe da NovaSeguro
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Faça login para consultar clientes, conversar com o assistente de IA
            e acompanhar os indicadores de renovação da carteira.
          </Typography>
          <Button component={Link} href="/login" variant="contained" size="large">
            Fazer login
          </Button>
        </Container>
      </Box>

      <Box component="footer" sx={{ py: 4, textAlign: "center" }}>
        <Typography variant="body2" color="text.secondary">
          NovaSeguro Corretora — exemplo fictício para fins de demonstração.
        </Typography>
      </Box>
    </Box>
  );
}
