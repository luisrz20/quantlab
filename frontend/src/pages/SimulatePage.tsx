import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  TextField,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { useNavigate } from "react-router-dom";
import { runSimulation } from "@/api/client";
import type { StrategyName } from "@/api/client";

const STRATEGIES: { value: StrategyName; label: string }[] = [
  { value: "sma_crossover", label: "SMA Crossover" },
  { value: "rsi_mean_reversion", label: "RSI Mean Reversion" },
];

export default function SimulatePage() {
  const navigate = useNavigate();
  const [tickers, setTickers] = useState<string[]>(["AAPL"]);
  const [tickerInput, setTickerInput] = useState("");
  const [strategy, setStrategy] = useState<StrategyName>("sma_crossover");
  const [lookback, setLookback] = useState(180);
  const [cash, setCash] = useState(100000);
  const [commission, setCommission] = useState(0.001);
  const [slippage, setSlippage] = useState(0.001);
  // SMA params
  const [fast, setFast] = useState(20);
  const [slow, setSlow] = useState(50);
  // RSI params
  const [period, setPeriod] = useState(14);
  const [lower, setLower] = useState(30);
  const [upper, setUpper] = useState(70);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addTicker = () => {
    const t = tickerInput.trim().toUpperCase();
    if (t && !tickers.includes(t)) setTickers((p) => [...p, t]);
    setTickerInput("");
  };

  const getParams = () =>
    strategy === "sma_crossover"
      ? { fast, slow }
      : { period, lower, upper };

  const handleRun = async () => {
    if (tickers.length === 0) { setError("Add at least one ticker."); return; }
    setLoading(true);
    setError(null);
    try {
      const ticker = tickers[0];
      const sid = await runSimulation({
        ticker,
        strategy,
        strategy_params: getParams(),
        lookback_days: lookback,
        initial_cash: cash,
        commission_pct: commission,
        slippage_pct: slippage,
      });
      navigate(`/results/${sid}`);
    } catch {
      setError("Simulation failed. Check ticker and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 700, mx: "auto" }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        New Simulation
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>
            Tickers
          </Typography>
          <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap" }}>
            {tickers.map((t) => (
              <Chip key={t} label={t} onDelete={() => setTickers((p) => p.filter((x) => x !== t))} />
            ))}
          </Box>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              size="small"
              placeholder="e.g. MSFT"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addTicker()}
            />
            <Button variant="outlined" size="small" startIcon={<AddIcon />} onClick={addTicker}>
              Add
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>
            Strategy
          </Typography>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel>Strategy</InputLabel>
            <Select value={strategy} label="Strategy" onChange={(e) => setStrategy(e.target.value as StrategyName)}>
              {STRATEGIES.map((s) => (
                <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {strategy === "sma_crossover" ? (
            <Box sx={{ display: "flex", gap: 2 }}>
              <TextField label="Fast" type="number" size="small" value={fast}
                onChange={(e) => setFast(Number(e.target.value))} inputProps={{ min: 2 }} />
              <TextField label="Slow" type="number" size="small" value={slow}
                onChange={(e) => setSlow(Number(e.target.value))} inputProps={{ min: 3 }} />
            </Box>
          ) : (
            <Box sx={{ display: "flex", gap: 2 }}>
              <TextField label="Period" type="number" size="small" value={period}
                onChange={(e) => setPeriod(Number(e.target.value))} inputProps={{ min: 2 }} />
              <TextField label="Lower" type="number" size="small" value={lower}
                onChange={(e) => setLower(Number(e.target.value))} inputProps={{ min: 1, max: 49 }} />
              <TextField label="Upper" type="number" size="small" value={upper}
                onChange={(e) => setUpper(Number(e.target.value))} inputProps={{ min: 51, max: 99 }} />
            </Box>
          )}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>
            Parameters
          </Typography>
          <Typography gutterBottom>Lookback: {lookback} days</Typography>
          <Slider value={lookback} min={60} max={1825} step={30}
            onChange={(_, v) => setLookback(v as number)} sx={{ mb: 2 }} />
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <TextField label="Initial Cash ($)" type="number" size="small" value={cash}
              onChange={(e) => setCash(Number(e.target.value))} inputProps={{ min: 1000 }} />
            <TextField label="Commission (%)" type="number" size="small"
              value={(commission * 100).toFixed(2)}
              onChange={(e) => setCommission(Number(e.target.value) / 100)}
              inputProps={{ step: 0.01, min: 0 }} />
            <TextField label="Slippage (%)" type="number" size="small"
              value={(slippage * 100).toFixed(2)}
              onChange={(e) => setSlippage(Number(e.target.value) / 100)}
              inputProps={{ step: 0.01, min: 0 }} />
          </Box>
        </CardContent>
      </Card>

      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

      <Button
        variant="contained"
        size="large"
        startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <PlayArrowIcon />}
        onClick={handleRun}
        disabled={loading}
        fullWidth
      >
        {loading ? "Running..." : "Run Simulation"}
      </Button>
    </Box>
  );
}
