const express = require("express");
const { pool } = require("../db");
const { requireAuth } = require("../middleware/requireAuth");

const router = express.Router();

router.get("/seguradoras", requireAuth, async (_req, res) => {
  try {
    const { rows } = await pool.query("SELECT id, nome FROM seguradoras ORDER BY nome");
    res.json({ seguradoras: rows });
  } catch (err) {
    console.error("Erro ao listar seguradoras:", err);
    res.status(500).json({ error: "Erro ao buscar seguradoras" });
  }
});

router.get("/dashboard", requireAuth, async (_req, res) => {
  try {
    const [clientesRes, apolicesRes, emRiscoRes, previsoesRes] = await Promise.all([
      pool.query("SELECT COUNT(*)::int AS total FROM clientes"),
      pool.query("SELECT COUNT(*)::int AS total FROM apolices WHERE status = 'ativa'"),
      pool.query(
        "SELECT COUNT(*)::int AS total FROM apolices WHERE status = 'ativa' AND data_renovacao <= CURRENT_DATE + INTERVAL '30 days'"
      ),
      pool.query(
        `SELECT AVG(probabilidade_renovacao)::numeric(5,1) AS media
         FROM (
           SELECT DISTINCT ON (apolice_id) apolice_id, probabilidade_renovacao
           FROM previsoes_renovacao
           ORDER BY apolice_id, calculado_em DESC
         ) ultimas`
      ),
    ]);

    res.json({
      totalClientes: clientesRes.rows[0].total,
      apolicesAtivas: apolicesRes.rows[0].total,
      apolicesEmRisco30d: emRiscoRes.rows[0].total,
      probabilidadeMediaRenovacao: previsoesRes.rows[0].media
        ? Number(previsoesRes.rows[0].media)
        : null,
    });
  } catch (err) {
    console.error("Erro ao montar dashboard:", err);
    res.status(500).json({ error: "Erro ao buscar indicadores" });
  }
});

router.get("/clientes", requireAuth, async (_req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT
        c.id,
        c.nome,
        c.email,
        c.corretor_responsavel,
        COUNT(a.id)::int AS total_apolices,
        MIN(a.data_renovacao) FILTER (WHERE a.status = 'ativa') AS proxima_renovacao
      FROM clientes c
      LEFT JOIN apolices a ON a.cliente_id = c.id
      GROUP BY c.id
      ORDER BY proxima_renovacao NULLS LAST
    `);
    res.json({ clientes: rows });
  } catch (err) {
    console.error("Erro ao listar clientes:", err);
    res.status(500).json({ error: "Erro ao buscar clientes" });
  }
});

module.exports = router;
