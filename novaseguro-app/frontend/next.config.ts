import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Só afeta `next dev` (produção usa `next start`, sem essa checagem).
  // Necessário para testar o multi-tenant por subdomínio localmente — o
  // servidor de dev bloqueia por padrão requisições vindas de um host
  // diferente do que ele foi iniciado. Ex.: NEXT_DEV_ALLOWED_ORIGINS=
  // "*.meudominio.local,*.localhost"
  allowedDevOrigins: process.env.NEXT_DEV_ALLOWED_ORIGINS?.split(",").map((o) => o.trim()),
};

export default nextConfig;
