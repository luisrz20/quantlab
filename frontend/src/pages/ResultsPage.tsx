import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import MetricCard from "@/components/common/MetricCard";
import EquityChart from "@/components/common/EquityChart";
import TradesTable from "@/components/common/TradesTable";
import { getSimulation } from "@/api/client";
import type { SimDetail } from "@/api/client";

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<SimDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getSimulation(Number(id))
      .then(setData)
      .catch(() => setError("Could not load simulation."));
  }, [id]);

  if (error) return <Typography color="error">{error}</Typography>;
  if (!data) return <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}><CircularProgress /></Box>;

  const m = data.simulation.metrics;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/simulate")} sx={{ mb: 2 }}>
        New simulation
      </Button>

      <Typography variant="h5" fontWeight={700} gutterBottom>
        {data.simulation.ticker} — {data.simulation.strategy_name.replace("_", " ")}
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {data.simulation.created_at.slice(0, 19).replace("T", " ")}
      </Typography>

      {m && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {[
            { title: "Profit", value: m.profit_pct.toFixed(2), unit: "%", color: m.profit_pct >= 0 ? "#10b981" : "#ef4444" },
            { title: "Win Rate", value: m.win_rate.toFixed(1), unit: "%" },
            { title: "Max Drawdown", value: m.max_drawdown.toFixed(2), unit: "%", color: "#f59e0b" },
            { title: "Sharpe", value: m.sharpe.toFixed(2) },
            { title: "Trades", value: m.num_trades },
          ].map((c) => (
            <Grid item xs={6} sm={4} md={2} key={c.title}>
              <MetricCard {...c} />
            </Grid>
          ))}
        </Grid>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} gutterBottom>
            Equity Curve
          </Typography>
          <EquityChart
            series={[{ data: data.equity_curve, name: data.simulation.ticker, color: "#6366f1" }]}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} gutterBottom>
            Trades
          </Typography>
          <TradesTable trades={data.trades} />
        </CardContent>
      </Card>
    </Box>
  );
}
