const jwt = require("jsonwebtoken");
const config = require("../config");

function signSession(user) {
  return jwt.sign(
    { sub: String(user.id), email: user.email, name: user.name, role: user.role },
    config.jwtSecret,
    { algorithm: "HS256", expiresIn: config.jwtExpiresIn }
  );
}

function verifySession(token) {
  return jwt.verify(token, config.jwtSecret, { algorithms: ["HS256"] });
}

module.exports = { signSession, verifySession };
