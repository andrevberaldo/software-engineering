const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");

const config = require("./config");
const authRoutes = require("./auth/routes");
const agentRoutes = require("./agent/routes");
const dataRoutes = require("./data/routes");
const documentsRoutes = require("./documents/routes");
const { pool } = require("./db");

const app = express();

app.use(
  cors({
    origin: config.frontendOrigin,
    credentials: true,
  })
);
app.use(express.json());
app.use(cookieParser());

app.get("/api/health", async (_req, res) => {
  let dbOk = true;
  try {
    await pool.query("SELECT 1");
  } catch {
    dbOk = false;
  }
  res.json({ status: dbOk ? "ok" : "degraded", database: dbOk });
});

app.use("/api/auth", authRoutes);
app.use("/api/agent", agentRoutes);
app.use("/api/data", dataRoutes);
app.use("/api/documents", documentsRoutes);

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: "Erro interno no BFF" });
});

app.listen(config.port, () => {
  console.log(`BFF da NovaSeguro rodando em http://localhost:${config.port}`);
});
