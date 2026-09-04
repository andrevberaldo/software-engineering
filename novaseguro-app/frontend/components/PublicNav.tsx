"use client";

import { useEffect, useState } from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Link from "next/link";
import { API_URL } from "@/lib/config";
import { getBrowserHost } from "@/lib/tenant";

interface Branding {
  slug: string;
  nomeEmpresa: string;
  headerColor: string;
  hasLogo: boolean;
}

export default function PublicNav() {
  const [branding, setBranding] = useState<Branding | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/public/branding?host=${encodeURIComponent(getBrowserHost())}`)
      .then((res) => (res.ok ? res.json() : null))
      .then(setBranding)
      .catch(() => {});
  }, []);

  return (
    <AppBar position="static" elevation={0} sx={branding ? { bgcolor: branding.headerColor } : undefined}>
      <Toolbar sx={{ maxWidth: 1200, width: "100%", mx: "auto", py: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, flexGrow: 1 }}>
          {branding?.hasLogo ? (
            <Box
              component="img"
              src={`${API_URL}/public/tenants/${branding.slug}/logo`}
              alt={branding.nomeEmpresa}
              sx={{ height: 32, maxWidth: 160, objectFit: "contain" }}
            />
          ) : (
            <Typography variant="h6" component="span" sx={{ fontWeight: 800 }}>
              {branding?.nomeEmpresa ?? "NovaSeguro"}
            </Typography>
          )}
        </Box>
        <Button
          component={Link}
          href="/login"
          variant="contained"
          color="secondary"
          sx={{ fontWeight: 700 }}
        >
          Entrar
        </Button>
      </Toolbar>
    </AppBar>
  );
}
