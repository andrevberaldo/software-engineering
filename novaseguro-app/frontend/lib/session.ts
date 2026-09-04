import { jwtVerify } from "jose";

export interface SessionUser {
  sub: string;
  email: string;
  name: string;
  role: string;
  tenant_id: number;
}

const secret = new TextEncoder().encode(
  process.env.JWT_SECRET || "change-me-in-every-environment"
);

/**
 * Verifica a assinatura do JWT emitido pelo backend no login. O frontend
 * nunca assina/emite esse token, apenas confia nele (mesmo segredo
 * compartilhado via JWT_SECRET) para decidir se uma página protegida pode
 * ser exibida.
 */
export async function verifySessionToken(token: string): Promise<SessionUser | null> {
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as unknown as SessionUser;
  } catch {
    return null;
  }
}
