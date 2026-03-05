import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "@/theme/index";
import AppLayout from "@/components/common/AppLayout";
import AppRoutes from "@/routes";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppLayout>
          <AppRoutes />
        </AppLayout>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
