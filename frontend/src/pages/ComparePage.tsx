import { useEffect, useState } from "react";
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import MetricCard from "@/components/common/MetricCard";
import EquityChart from "@/components/common/EquityChart";
import TradesTable from "@/components/common/TradesTable";
import { listSimulations, compareSimulations } from "@/api/client";
import type { SimSummary, CompareResult } from "@/api/client";

export default function ComparePage() {
  const [sims, setSims] = useState<SimSummary[]>([]);
  const [idA, setIdA] = useState<number | "">("");
  const [idB, setIdB] = useState<number | "">("");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    listSimulations().then(setSims).catch(console.error);
  }, []);

  useEffect(() => {
    if (!idA || !idB || idA === idB) return;
    setLoading(true);
    compareSimulations(Number(idA), Number(idB))
      .then(setResult)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [idA, idB]);

  const completedSims = sims.filter((s) => s.status === "completed");

  const label = (s: SimSummary) =>
    `#${s.id} ${s.ticker} (${s.strategy_name.replace("_", " ")})`;

  const metricsRow = (result: CompareResult) => {
    const a = result.simulation_a.simulation.metrics;
    const b = result.simulation_b.simulation.metrics;
    const fields: Array<{ key: keyof typeof a; title: string; unit?: string }> = [
      { key: "profit_pct", title: "Profit", unit: "%" },
      { key: "win_rate", title: "Win Rate", unit: "%" },
      { key: "max_drawdown", title: "Max DD", unit: "%" },
      { key: "sharpe", title: "Sharpe" },
      { key: "num_trades", title: "Trades" },
    ];
    return fields.map((f) => ({ ...f, a: a ? a[f.key] : null, b: b ? b[f.key] : null }));
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Compare Simulations
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: "Simulation A", value: idA, set: setIdA },
          { label: "Simulation B", value: idB, set: setIdB },
        ].map((s, i) => (
          <Grid item xs={12} sm={6} key={i}>
            <FormControl fullWidth size="small">
              <InputLabel>{s.label}</InputLabel>
              <Select
                value={s.value}
                label={s.label}
                onChange={(e) => s.set(e.target.value as number)}
              >
                {completedSims.map((sim) => (
                  <MenuItem key={sim.id} value={sim.id}>
                    {label(sim)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        ))}
      </Grid>

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {result && !loading && (
        <>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Equity Curves
              </Typography>
              <EquityChart
                height={320}
                series={[
                  {
                    data: result.simulation_a.equity_curve,
                    name: label(result.simulation_a.simulation),
                    color: "#6366f1",
                  },
                  {
                    data: result.simulation_b.equity_curve,
                    name: label(result.simulation_b.simulation),
                    color: "#10b981",
                  },
                ]}
              />
            </CardContent>
          </Card>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Metrics Comparison
              </Typography>
              <Grid container spacing={2}>
                {metricsRow(result).map((row) => (
                  <Grid item xs={6} sm={4} md={2} key={row.title}>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase" }}>
                        {row.title}
                      </Typography>
                      <Typography variant="body1" sx={{ color: "#6366f1", fontWeight: 700 }}>
                        A: {row.a != null ? Number(row.a).toFixed(2) : "—"}{row.unit}
                      </Typography>
                      <Typography variant="body1" sx={{ color: "#10b981", fontWeight: 700 }}>
                        B: {row.b != null ? Number(row.b).toFixed(2) : "—"}{row.unit}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Tabs value={tab} onChange={(_, v: number) => setTab(v)} sx={{ mb: 2 }}>
                <Tab label={`Trades A (${result.simulation_a.trades.length})`} />
                <Tab label={`Trades B (${result.simulation_b.trades.length})`} />
              </Tabs>
              {tab === 0 && <TradesTable trades={result.simulation_a.trades} />}
              {tab === 1 && <TradesTable trades={result.simulation_b.trades} />}
            </CardContent>
          </Card>
        </>
      )}

      {!loading && !result && idA && idB && idA !== idB && (
        <Typography color="text.secondary">Loading comparison…</Typography>
      )}
    </Box>
  );
}
