import { NextRequest, NextResponse } from "next/server";
import { verifySessionToken } from "./lib/session";
import { SESSION_COOKIE_NAME } from "./lib/config";

const PROTECTED_PREFIXES = ["/dashboard", "/chat", "/clientes", "/documentos"];

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

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/chat/:path*", "/clientes/:path*", "/documentos/:path*"],
};
