import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  direction: "rtl",
  palette: {
    primary: {
      main: "#a855f7",
      dark: "#9333ea",
    },
    secondary: {
      main: "#ec4899",
      dark: "#db2777",
    },
    success: {
      main: "#22c55e",
      dark: "#16a34a",
    },
    error: {
      main: "#ef4444",
      dark: "#dc2626",
    },
    warning: {
      main: "#f59e0b",
    },
    info: {
      main: "#3b82f6",
      dark: "#2563eb",
    },
    background: {
      default: "#f5f0ff",
      paper: "#ffffff",
    },
    text: {
      primary: "#1e1b4b",
      secondary: "#6b7280",
    },
  },
  typography: {
    fontFamily: "'Rubik', 'Fredoka', sans-serif",
    h1: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    h2: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    h3: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    h4: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    h5: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    h6: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
    button: { fontFamily: "'Fredoka', 'Rubik', sans-serif" },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 9999,
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 24,
        },
      },
    },
  },
});

export default theme;
