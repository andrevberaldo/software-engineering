const config = require("../config");
const { verifySession } = require("../auth/jwt");

function requireAuth(req, res, next) {
  const token = req.cookies?.[config.cookieName];
  if (!token) {
    return res.status(401).json({ error: "Não autenticado" });
  }

  try {
    req.user = verifySession(token);
    req.sessionToken = token;
    return next();
  } catch (err) {
    return res.status(401).json({ error: "Sessão inválida ou expirada" });
  }
}

module.exports = { requireAuth };
