"use client";

import { useEffect, useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { API_URL } from "@/lib/config";

interface Branding {
  slug: string;
  nomeEmpresa: string;
  headerColor: string;
  hasLogo: boolean;
}

const HEX_COLOR_RE = /^#[0-9A-Fa-f]{6}$/;

export default function IdentidadeVisualPage() {
  const router = useRouter();
  const [branding, setBranding] = useState<Branding | null>(null);
  const [nomeEmpresa, setNomeEmpresa] = useState("");
  const [headerColor, setHeaderColor] = useState("#1E2761");
  const [logo, setLogo] = useState<File | null>(null);
  const [logoPreviewUrl, setLogoPreviewUrl] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/tenants/branding`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error("Falha ao carregar a identidade visual");
        return res.json();
      })
      .then((data: Branding) => {
        setBranding(data);
        setNomeEmpresa(data.nomeEmpresa);
        setHeaderColor(data.headerColor);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!logo) {
      setLogoPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(logo);
    setLogoPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [logo]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!HEX_COLOR_RE.test(headerColor)) {
      setError("Informe a cor no formato #RRGGBB");
      return;
    }

    setSaving(true);
    const formData = new FormData();
    formData.append("nome_empresa", nomeEmpresa);
    formData.append("header_color", headerColor);
    if (logo) formData.append("logo", logo);

    try {
      const res = await fetch(`${API_URL}/tenants/branding`, {
        method: "PUT",
        credentials: "include",
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Não foi possível salvar a identidade visual");
        return;
      }

      setBranding(data);
      setLogo(null);
      setSuccess("Identidade visual atualizada.");
      router.refresh();
    } catch {
      setError("Erro de conexão ao salvar.");
    } finally {
      setSaving(false);
    }
  }

  const currentLogoUrl = branding?.hasLogo
    ? `${API_URL}/public/tenants/${branding.slug}/logo`
    : null;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Identidade visual
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Personalize o nome da empresa, a cor do cabeçalho e o logotipo
        exibidos em toda a ferramenta — inclusive na página inicial e no
        login, antes de entrar.
      </Typography>

      <Paper variant="outlined" sx={{ p: 3, borderRadius: 3, maxWidth: 520 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}

            <TextField
              label="Nome da empresa"
              value={nomeEmpresa}
              onChange={(e) => setNomeEmpresa(e.target.value)}
              required
              fullWidth
              disabled={!branding}
            />

            <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
              <Box
                component="input"
                type="color"
                value={headerColor}
                onChange={(e) => setHeaderColor((e.target as HTMLInputElement).value)}
                disabled={!branding}
                sx={{
                  width: 48,
                  height: 40,
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 1,
                  p: 0,
                  cursor: "pointer",
                }}
              />
              <TextField
                label="Cor do cabeçalho"
                value={headerColor}
                onChange={(e) => setHeaderColor(e.target.value)}
                helperText="Formato #RRGGBB"
                disabled={!branding}
                sx={{ flexGrow: 1 }}
              />
            </Stack>

            <Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Logotipo (SVG)
              </Typography>
              <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
                {(logoPreviewUrl || currentLogoUrl) && (
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1,
                      bgcolor: headerColor,
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <Box
                      component="img"
                      src={logoPreviewUrl || currentLogoUrl || undefined}
                      alt="Logotipo"
                      sx={{ height: 32, maxWidth: 140, objectFit: "contain" }}
                    />
                  </Box>
                )}
                <Button variant="outlined" component="label" disabled={!branding}>
                  {logo ? logo.name : "Escolher arquivo SVG"}
                  <input
                    type="file"
                    accept=".svg,image/svg+xml"
                    hidden
                    onChange={(e) => setLogo(e.target.files?.[0] ?? null)}
                  />
                </Button>
              </Stack>
            </Box>

            <Button
              type="submit"
              variant="contained"
              startIcon={saving ? <CircularProgress size={16} color="inherit" /> : <UploadFileIcon />}
              disabled={saving || !branding}
              sx={{ alignSelf: "flex-start" }}
            >
              {saving ? "Salvando..." : "Salvar identidade visual"}
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}
