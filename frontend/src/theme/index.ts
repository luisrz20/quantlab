import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#6366f1" },
    secondary: { main: "#10b981" },
    background: { default: "#0f172a", paper: "#1e293b" },
  },
  typography: { fontFamily: '"Inter", "Roboto", sans-serif' },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12, border: "1px solid rgba(99,102,241,0.2)" },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: "none", fontWeight: 600 },
      },
    },
  },
});

export default theme;
