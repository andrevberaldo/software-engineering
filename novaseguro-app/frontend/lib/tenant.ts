/**
 * Nos 2-3 pontos que ainda não têm sessão (home pública, login), o backend
 * não tem como saber o tenant pelo próprio Host da chamada de API (que em
 * produção pode ser um domínio compartilhado, ex. api.dominio.com,
 * diferente do subdomínio que o visitante está usando). Por isso o
 * frontend manda explicitamente o host que o navegador está vendo.
 *
 * Rotas autenticadas não precisam disso: o tenant já vem da claim do JWT.
 */
export function getBrowserHost(): string {
  if (typeof window === "undefined") return "";
  return window.location.host;
}
