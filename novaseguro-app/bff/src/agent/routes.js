const express = require("express");
const config = require("../config");
const { requireAuth } = require("../middleware/requireAuth");

const router = express.Router();

router.post("/chat", requireAuth, async (req, res) => {
  const { message, thread_id: threadId } = req.body || {};
  if (!message || !message.trim()) {
    return res.status(400).json({ error: "Mensagem vazia" });
  }

  try {
    const upstream = await fetch(`${config.aiBackendUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${req.sessionToken}`,
      },
      body: JSON.stringify({ message, thread_id: threadId }),
    });

    const data = await upstream.json().catch(() => ({}));

    if (!upstream.ok) {
      return res
        .status(upstream.status)
        .json({ error: data.detail || "Falha ao consultar o assistente de IA" });
    }

    return res.json(data);
  } catch (err) {
    console.error("Erro ao chamar o backend de IA:", err);
    return res.status(502).json({ error: "Backend de IA indisponível" });
  }
});

module.exports = router;
