import React, { useState } from "react";
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import BarChartIcon from "@mui/icons-material/BarChart";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import { useNavigate, useLocation } from "react-router-dom";

const DRAWER_WIDTH = 220;

const NAV = [
  { label: "Simulate", icon: <PlayArrowIcon />, path: "/simulate" },
  { label: "Compare", icon: <CompareArrowsIcon />, path: "/compare" },
] as const;

interface Props {
  children: React.ReactNode;
}

export default function AppLayout({ children }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const drawer = (
    <Box sx={{ width: DRAWER_WIDTH }}>
      <Toolbar>
        <BarChartIcon sx={{ mr: 1, color: "primary.main" }} />
        <Typography variant="h6" fontWeight={700} color="primary.main">
          QuantLab
        </Typography>
      </Toolbar>
      <List>
        {NAV.map((n) => (
          <ListItemButton
            key={n.path}
            selected={location.pathname.startsWith(n.path)}
            onClick={() => {
              navigate(n.path);
              setOpen(false);
            }}
          >
            <ListItemIcon
              sx={{
                color: location.pathname.startsWith(n.path)
                  ? "primary.main"
                  : "inherit",
              }}
            >
              {n.icon}
            </ListItemIcon>
            <ListItemText primary={n.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          bgcolor: "background.paper",
          borderBottom: "1px solid rgba(99,102,241,0.2)",
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton edge="start" onClick={() => setOpen(true)} sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
          )}
          <BarChartIcon sx={{ mr: 1, color: "primary.main" }} />
          <Typography variant="h6" fontWeight={700} color="primary.main">
            QuantLab
          </Typography>
        </Toolbar>
      </AppBar>

      {isMobile ? (
        <Drawer open={open} onClose={() => setOpen(false)} variant="temporary">
          {drawer}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            width: DRAWER_WIDTH,
            "& .MuiDrawer-paper": {
              width: DRAWER_WIDTH,
              bgcolor: "background.paper",
              borderRight: "1px solid rgba(99,102,241,0.15)",
            },
          }}
        >
          {drawer}
        </Drawer>
      )}

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: isMobile ? 0 : `${DRAWER_WIDTH}px`,
          mt: "64px",
          p: 3,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
