"use client";

import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Link from "next/link";

export default function PublicNav() {
  return (
    <AppBar position="static" elevation={0}>
      <Toolbar sx={{ maxWidth: 1200, width: "100%", mx: "auto", py: 1 }}>
        <Box sx={{ display: "flex", alignItems: "baseline", gap: 1, flexGrow: 1 }}>
          <Typography variant="h6" component="span" sx={{ fontWeight: 800 }}>
            NovaSeguro
          </Typography>
          <Typography variant="body2" component="span" sx={{ opacity: 0.8 }}>
            Copiloto
          </Typography>
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
