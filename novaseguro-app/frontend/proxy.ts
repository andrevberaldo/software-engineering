import { NextRequest, NextResponse } from "next/server";
import { verifySessionToken } from "./lib/session";
import { SESSION_COOKIE_NAME } from "./lib/config";

const PROTECTED_PREFIXES = ["/dashboard", "/chat", "/clientes", "/documentos", "/configuracoes"];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));

  if (!isProtected) {
    return NextResponse.next();
  }

  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const session = token ? await verifySessionToken(token) : null;

  if (!session) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Gate de UX só — quem garante de verdade é o backend (require_admin em
  // PUT /tenants/branding), já que um cookie pode ser forjado/reaproveitado.
  if (pathname.startsWith("/configuracoes") && session.role !== "admin") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/chat/:path*",
    "/clientes/:path*",
    "/documentos/:path*",
    "/configuracoes/:path*",
  ],
};
