require("dotenv").config();

module.exports = {
  port: process.env.PORT || 4000,
  databaseUrl:
    process.env.DATABASE_URL ||
    "postgresql://novaseguro:novaseguro_dev_pw@localhost:5432/novaseguro",
  jwtSecret: process.env.JWT_SECRET || "change-me-in-every-environment",
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || "7d",
  cookieName: "ns_session",
  cookieSecure: process.env.COOKIE_SECURE === "true",
  frontendOrigin: process.env.FRONTEND_ORIGIN || "http://localhost:3000",
  aiBackendUrl: process.env.AI_BACKEND_URL || "http://localhost:8000",
};
