"use client";

import { createTheme } from "@mui/material/styles";

// Mesma identidade visual usada na apresentação da NovaSeguro
// (navy dominante, gelo como secundária, âmbar como destaque).
const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1E2761",
      light: "#3A4A9E",
      dark: "#141a45",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#E8A33D",
      contrastText: "#1E2761",
    },
    background: {
      default: "#F7F9FC",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#2B2B33",
      secondary: "#6B7280",
    },
  },
  shape: {
    borderRadius: 10,
  },
  typography: {
    fontFamily: [
      "Inter",
      "Roboto",
      "Helvetica",
      "Arial",
      "sans-serif",
    ].join(","),
    h1: { fontWeight: 800 },
    h2: { fontWeight: 800 },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        // Cor de fallback, usada só até a marca do tenant carregar (ou se
        // ele não tiver nenhuma) — PublicNav, AppShell e a tela de login
        // sobrescrevem via `sx={{ bgcolor: tenant.headerColor }}`, que tem
        // prioridade sobre este styleOverrides.
        root: {
          backgroundColor: "#1E2761",
        },
      },
    },
  },
});

export default theme;
