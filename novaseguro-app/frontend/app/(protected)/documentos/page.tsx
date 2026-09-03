"use client";

import { useEffect, useState, FormEvent } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import DownloadIcon from "@mui/icons-material/Download";
import { BFF_URL } from "@/lib/config";

interface Documento {
  id: number;
  titulo: string;
  seguradora_id: number | null;
  seguradora_nome: string | null;
  arquivo_nome: string | null;
  mime_type: string | null;
  tamanho_bytes: number | null;
  total_chunks: number;
  criado_em: string;
}

interface Seguradora {
  id: number;
  nome: string;
}

function formatBytes(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentosPage() {
  const [documentos, setDocumentos] = useState<Documento[] | null>(null);
  const [seguradoras, setSeguradoras] = useState<Seguradora[]>([]);
  const [titulo, setTitulo] = useState("");
  const [seguradoraId, setSeguradoraId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  function loadDocumentos() {
    fetch(`${BFF_URL}/api/documents`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error("Falha ao carregar documentos");
        return res.json();
      })
      .then(setDocumentos)
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    loadDocumentos();
    fetch(`${BFF_URL}/api/data/seguradoras`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setSeguradoras(data.seguradoras || []))
      .catch(() => {});
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Selecione um arquivo PDF");
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append("titulo", titulo);
    if (seguradoraId) formData.append("seguradora_id", seguradoraId);
    formData.append("file", file);

    try {
      const res = await fetch(`${BFF_URL}/api/documents/upload`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Falha ao enviar o documento");
        return;
      }

      setSuccess(`"${data.titulo}" processado com sucesso: ${data.total_chunks} trechos indexados.`);
      setTitulo("");
      setSeguradoraId("");
      setFile(null);
      loadDocumentos();
    } catch {
      setError("Erro de conexão ao enviar o documento.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Documentos
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Envie PDFs de apólices para o assistente de IA consultar. O Docling
        extrai o texto e divide em trechos (chunks), que ficam indexados no
        banco para busca por similaridade — e o arquivo original fica
        disponível para download.
      </Typography>

      <Paper variant="outlined" sx={{ p: 3, borderRadius: 3, mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Enviar novo PDF
        </Typography>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                label="Título do documento"
                value={titulo}
                onChange={(e) => setTitulo(e.target.value)}
                required
                fullWidth
              />
              <TextField
                select
                label="Seguradora (opcional)"
                value={seguradoraId}
                onChange={(e) => setSeguradoraId(e.target.value)}
                sx={{ minWidth: 220 }}
              >
                <MenuItem value="">Nenhuma / geral</MenuItem>
                {seguradoras.map((s) => (
                  <MenuItem key={s.id} value={s.id}>
                    {s.nome}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
            <Button variant="outlined" component="label" sx={{ alignSelf: "flex-start" }}>
              {file ? file.name : "Escolher arquivo PDF"}
              <input
                type="file"
                accept="application/pdf"
                hidden
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={uploading ? <CircularProgress size={16} color="inherit" /> : <UploadFileIcon />}
              disabled={uploading}
              sx={{ alignSelf: "flex-start" }}
            >
              {uploading ? "Processando..." : "Enviar e processar"}
            </Button>
          </Stack>
        </form>
      </Paper>

      <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Título</TableCell>
              <TableCell>Seguradora</TableCell>
              <TableCell align="center">Trechos</TableCell>
              <TableCell align="right">Tamanho</TableCell>
              <TableCell align="right">Ação</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documentos?.map((d) => (
              <TableRow key={d.id} hover>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {d.titulo}
                  </Typography>
                  {d.arquivo_nome && (
                    <Typography variant="caption" color="text.secondary">
                      {d.arquivo_nome}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>{d.seguradora_nome || "—"}</TableCell>
                <TableCell align="center">
                  <Chip size="small" label={d.total_chunks} />
                </TableCell>
                <TableCell align="right">{formatBytes(d.tamanho_bytes)}</TableCell>
                <TableCell align="right">
                  {d.arquivo_nome ? (
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      href={`${BFF_URL}/api/documents/${d.id}/download`}
                    >
                      Baixar
                    </Button>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      Sem arquivo
                    </Typography>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
