const express = require("express");
const { Readable } = require("stream");
const config = require("../config");
const { requireAuth } = require("../middleware/requireAuth");

const router = express.Router();

// Upload é multipart/form-data: repassamos o corpo da requisição como um
// stream direto para o backend Python, sem fazer o Express interpretar o
// arquivo — evita carregar o PDF inteiro na memória do BFF.
router.post("/upload", requireAuth, async (req, res) => {
  try {
    const upstream = await fetch(`${config.aiBackendUrl}/documents/upload`, {
      method: "POST",
      headers: {
        "Content-Type": req.headers["content-type"],
        Authorization: `Bearer ${req.sessionToken}`,
      },
      body: Readable.toWeb(req),
      duplex: "half",
    });

    const data = await upstream.json().catch(() => ({}));
    if (!upstream.ok) {
      return res
        .status(upstream.status)
        .json({ error: data.detail || "Falha ao enviar o documento" });
    }
    return res.json(data);
  } catch (err) {
    console.error("Erro ao repassar upload para o backend de IA:", err);
    return res.status(502).json({ error: "Backend de IA indisponível" });
  }
});

router.get("/", requireAuth, async (req, res) => {
  try {
    const upstream = await fetch(`${config.aiBackendUrl}/documents`, {
      headers: { Authorization: `Bearer ${req.sessionToken}` },
    });
    const data = await upstream.json().catch(() => ({}));
    return res.status(upstream.status).json(data);
  } catch (err) {
    console.error("Erro ao listar documentos:", err);
    return res.status(502).json({ error: "Backend de IA indisponível" });
  }
});

router.get("/:id/download", requireAuth, async (req, res) => {
  try {
    const upstream = await fetch(
      `${config.aiBackendUrl}/documents/${req.params.id}/download`,
      { headers: { Authorization: `Bearer ${req.sessionToken}` } }
    );

    if (!upstream.ok) {
      const data = await upstream.json().catch(() => ({}));
      return res
        .status(upstream.status)
        .json({ error: data.detail || "Falha ao baixar o documento" });
    }

    res.setHeader(
      "Content-Type",
      upstream.headers.get("content-type") || "application/octet-stream"
    );
    const disposition = upstream.headers.get("content-disposition");
    if (disposition) res.setHeader("Content-Disposition", disposition);

    Readable.fromWeb(upstream.body).pipe(res);
  } catch (err) {
    console.error("Erro ao repassar download do backend de IA:", err);
    res.status(502).json({ error: "Backend de IA indisponível" });
  }
});

module.exports = router;
