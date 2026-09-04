"use client";

import { useRef, useState } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import SendIcon from "@mui/icons-material/Send";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import { API_URL } from "@/lib/config";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGESTOES = [
  "Quais apólices vencem nos próximos 30 dias?",
  "Consulte os dados da cliente Juliana Pereira",
  "Preveja a renovação da apólice 8",
  "Quais são as coberturas do plano Auto Completo da Seguradora Atlas?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Olá! Sou o copiloto de IA da corretora. Posso consultar clientes e apólices, " +
        "explicar coberturas, prever renovação e registrar contatos de renovação. Como posso ajudar?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadId = useRef(`web-${Date.now()}`);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: trimmed, thread_id: threadId.current }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Não foi possível falar com o assistente");
        return;
      }

      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch {
      setError("Erro de conexão com o assistente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Assistente de IA
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Converse em linguagem natural — as respostas usam dados reais da base
        da carteira.
      </Typography>

      <Paper
        variant="outlined"
        sx={{
          borderRadius: 3,
          display: "flex",
          flexDirection: "column",
          height: "60vh",
          minHeight: 420,
        }}
      >
        <Box sx={{ flexGrow: 1, overflowY: "auto", p: 3 }}>
          <Stack spacing={2}>
            {messages.map((m, i) => (
              <Stack
                key={i}
                direction="row"
                spacing={1.5}
                sx={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "80%",
                  flexDirection: m.role === "user" ? "row-reverse" : "row",
                }}
              >
                <Box
                  sx={{
                    bgcolor: m.role === "user" ? "primary.main" : "grey.200",
                    color: m.role === "user" ? "white" : "text.primary",
                    borderRadius: 3,
                    px: 2,
                    py: 1.2,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  <Stack direction="row" spacing={0.75} sx={{ mb: 0.5, opacity: 0.75, alignItems: "center" }}>
                    {m.role === "user" ? <PersonIcon fontSize="inherit" /> : <SmartToyIcon fontSize="inherit" />}
                    <Typography variant="caption">
                      {m.role === "user" ? "Você" : "Copiloto"}
                    </Typography>
                  </Stack>
                  <Typography variant="body2">{m.content}</Typography>
                </Box>
              </Stack>
            ))}
            {loading && (
              <Stack direction="row" spacing={1} sx={{ color: "text.secondary", alignItems: "center" }}>
                <CircularProgress size={16} />
                <Typography variant="body2">Pensando...</Typography>
              </Stack>
            )}
          </Stack>
        </Box>

        {error && (
          <Typography variant="body2" color="error" sx={{ px: 3, pb: 1 }}>
            {error}
          </Typography>
        )}

        <Box sx={{ p: 2, borderTop: "1px solid", borderColor: "divider" }}>
          <Stack direction="row" spacing={1} sx={{ mb: 1.5, flexWrap: "wrap", gap: 1 }}>
            {SUGESTOES.map((s) => (
              <Chip key={s} label={s} size="small" onClick={() => sendMessage(s)} />
            ))}
          </Stack>
          <Stack
            direction="row"
            spacing={1}
            component="form"
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
          >
            <TextField
              fullWidth
              size="small"
              placeholder="Pergunte algo ao copiloto..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <IconButton type="submit" color="primary" disabled={loading || !input.trim()}>
              <SendIcon />
            </IconButton>
          </Stack>
        </Box>
      </Paper>
    </Box>
  );
}
