"use client";

import { useEffect, useState } from "react";
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
import { BFF_URL } from "@/lib/config";

interface Cliente {
  id: number;
  nome: string;
  email: string;
  corretor_responsavel: string;
  total_apolices: number;
  proxima_renovacao: string | null;
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

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Clientes
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Visão geral da carteira. Peça ao assistente de IA os detalhes de
        qualquer cliente ou apólice específica.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Cliente</TableCell>
              <TableCell>Corretor responsável</TableCell>
              <TableCell align="center">Apólices</TableCell>
              <TableCell align="right">Próxima renovação</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {clientes
              ? clientes.map((c) => (
                  <TableRow key={c.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {c.nome}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {c.email}
                      </Typography>
                    </TableCell>
                    <TableCell>{c.corretor_responsavel}</TableCell>
                    <TableCell align="center">{c.total_apolices}</TableCell>
                    <TableCell align="right">
                      <RiscoChip dias={diasAte(c.proxima_renovacao)} />
                    </TableCell>
                  </TableRow>
                ))
              : Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell colSpan={4}>
                      <Skeleton variant="text" height={32} />
                    </TableCell>
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
