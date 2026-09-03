const express = require("express");
const bcrypt = require("bcryptjs");
const { pool } = require("../db");
const config = require("../config");
const { signSession } = require("./jwt");
const { requireAuth } = require("../middleware/requireAuth");

const router = express.Router();

const cookieOptions = {
  httpOnly: true,
  secure: config.cookieSecure,
  sameSite: "lax",
  path: "/",
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 dias, deve acompanhar jwtExpiresIn
};

router.post("/login", async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) {
    return res.status(400).json({ error: "Informe email e senha" });
  }

  try {
    const { rows } = await pool.query(
      "SELECT id, email, password_hash, name, role FROM users WHERE email = $1",
      [email.toLowerCase().trim()]
    );
    const user = rows[0];

    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
      return res.status(401).json({ error: "Email ou senha inválidos" });
    }

    const token = signSession(user);
    res.cookie(config.cookieName, token, cookieOptions);
    return res.json({
      user: { id: user.id, email: user.email, name: user.name, role: user.role },
    });
  } catch (err) {
    console.error("Erro no login:", err);
    return res.status(500).json({ error: "Erro interno ao autenticar" });
  }
});

router.post("/logout", (_req, res) => {
  res.clearCookie(config.cookieName, { path: "/" });
  return res.status(204).send();
});

router.get("/me", requireAuth, (req, res) => {
  return res.json({ user: req.user });
});

module.exports = router;
