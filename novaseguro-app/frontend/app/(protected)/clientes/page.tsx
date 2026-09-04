"use client";

import { useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Chip from "@mui/material/Chip";
import Alert from "@mui/material/Alert";
import Skeleton from "@mui/material/Skeleton";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import { BFF_URL } from "@/lib/config";

interface Apolice {
  id: number;
  cliente_id: number;
  tipo_cobertura: string;
  status: string;
  data_inicio: string;
  data_renovacao: string;
  valor_patrimonio_segurado: string | null;
  descricao_patrimonio: string | null;
  seguradora: string;
}

interface Cliente {
  id: number;
  nome: string;
  email: string;
  corretor_responsavel: string;
  total_apolices: number;
  proxima_renovacao: string | null;
  patrimonio_total: string;
  apolices: Apolice[];
}

function formatMoeda(valor: string | number | null): string {
  if (valor === null) return "—";
  const n = typeof valor === "string" ? Number(valor) : valor;
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

function formatData(dataIso: string | null): string {
  if (!dataIso) return "—";
  return new Date(dataIso).toLocaleDateString("pt-BR", { timeZone: "UTC" });
}

function diasAte(dataIso: string | null): number | null {
  if (!dataIso) return null;
  const diffMs = new Date(dataIso).getTime() - Date.now();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

function RiscoChip({ dias }: { dias: number | null }) {
  if (dias === null) return <Chip size="small" label="Sem apólice ativa" />;
  if (dias <= 15) return <Chip size="small" color="error" label={`Renova em ${dias}d`} />;
  if (dias <= 30) return <Chip size="small" color="warning" label={`Renova em ${dias}d`} />;
  return <Chip size="small" color="success" label={`Renova em ${dias}d`} />;
}

function KpiCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3, height: "100%" }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="h4" sx={{ fontWeight: 700, mt: 0.5 }}>
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

function ClienteRow({ cliente }: { cliente: Cliente }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <TableRow hover>
        <TableCell width={48}>
          <IconButton size="small" onClick={() => setOpen((v) => !v)} aria-label="expandir apólices">
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {cliente.nome}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {cliente.email}
          </Typography>
        </TableCell>
        <TableCell>{cliente.corretor_responsavel}</TableCell>
        <TableCell align="center">{cliente.total_apolices}</TableCell>
        <TableCell align="right">
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {formatMoeda(cliente.patrimonio_total)}
          </Typography>
        </TableCell>
        <TableCell align="right">
          <RiscoChip dias={diasAte(cliente.proxima_renovacao)} />
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={6} sx={{ py: 0, borderBottom: open ? undefined : "none" }}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ my: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Patrimônio assegurado por apólice
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Cobertura</TableCell>
                    <TableCell>Seguradora</TableCell>
                    <TableCell>Descrição do patrimônio</TableCell>
                    <TableCell align="right">Valor assegurado</TableCell>
                    <TableCell align="right">Início da apólice</TableCell>
                    <TableCell align="right">Renovação</TableCell>
                    <TableCell align="center">Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cliente.apolices.map((a) => (
                    <TableRow key={a.id}>
                      <TableCell>{a.tipo_cobertura}</TableCell>
                      <TableCell>{a.seguradora}</TableCell>
                      <TableCell>{a.descricao_patrimonio ?? "—"}</TableCell>
                      <TableCell align="right">{formatMoeda(a.valor_patrimonio_segurado)}</TableCell>
                      <TableCell align="right">{formatData(a.data_inicio)}</TableCell>
                      <TableCell align="right">{formatData(a.data_renovacao)}</TableCell>
                      <TableCell align="center">
                        <Chip
                          size="small"
                          label={a.status}
                          color={a.status === "ativa" ? "success" : "default"}
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

export default function ClientesPage() {
  const [clientes, setClientes] = useState<Cliente[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BFF_URL}/api/data/clientes`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error("Falha ao carregar clientes");
        return res.json();
      })
      .then((data) => setClientes(data.clientes))
      .catch((err) => setError(err.message));
  }, []);

  const kpis = useMemo(() => {
    if (!clientes) return null;
    const patrimonioTotal = clientes.reduce((soma, c) => soma + Number(c.patrimonio_total || 0), 0);
    const totalApolices = clientes.reduce((soma, c) => soma + c.total_apolices, 0);
    const em30dias = clientes.filter((c) => {
      const dias = diasAte(c.proxima_renovacao);
      return dias !== null && dias <= 30;
    }).length;
    return { patrimonioTotal, totalApolices, em30dias };
  }, [clientes]);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Clientes
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Patrimônio assegurado de cada cliente, com datas de início e renovação
        de cada apólice. Clique em uma linha para ver o detalhe.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" },
          gap: 2,
          mb: 3,
        }}
      >
        <KpiCard
          label="Patrimônio total assegurado"
          value={kpis ? formatMoeda(kpis.patrimonioTotal) : "—"}
          hint="Soma das apólices ativas"
        />
        <KpiCard
          label="Apólices na carteira"
          value={kpis ? String(kpis.totalApolices) : "—"}
          hint="Ativas e encerradas"
        />
        <KpiCard
          label="Clientes a renovar em 30 dias"
          value={kpis ? String(kpis.em30dias) : "—"}
          hint="Prioridade de contato"
        />
      </Box>

      <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={48} />
              <TableCell>Cliente</TableCell>
              <TableCell>Corretor responsável</TableCell>
              <TableCell align="center">Apólices</TableCell>
              <TableCell align="right">Patrimônio assegurado</TableCell>
              <TableCell align="right">Próxima renovação</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {clientes
              ? clientes.map((c) => <ClienteRow key={c.id} cliente={c} />)
              : Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell colSpan={6}>
                      <Skeleton variant="text" height={32} />
                    </TableCell>
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </TableContainer>

      {clientes && clientes.length === 0 && (
        <Box sx={{ textAlign: "center", py: 6, color: "text.secondary" }}>
          <ShieldOutlinedIcon sx={{ fontSize: 40, mb: 1 }} />
          <Typography>Nenhum cliente cadastrado ainda.</Typography>
        </Box>
      )}
    </Box>
  );
}
