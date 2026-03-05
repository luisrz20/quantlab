import axios from "axios";

// ── Types ────────────────────────────────────────────────────────────────────

export type StrategyName = "sma_crossover" | "rsi_mean_reversion";
export type SimStatus = "pending" | "running" | "completed" | "failed";
export type TradeSide = "BUY" | "SELL";

export interface Metrics {
  profit_pct: number;
  win_rate: number;
  max_drawdown: number;
  sharpe: number;
  num_trades: number;
}

export interface Trade {
  id: number;
  timestamp: string;
  side: TradeSide;
  qty: number;
  price: number;
  fees: number;
  slippage: number;
  pnl: number | null;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface SimSummary {
  id: number;
  ticker: string;
  strategy_name: string;
  status: SimStatus;
  created_at: string;
  metrics: Metrics | null;
}

export interface SimDetail {
  simulation: SimSummary;
  trades: Trade[];
  equity_curve: EquityPoint[];
}

export interface CompareResult {
  simulation_a: SimDetail;
  simulation_b: SimDetail;
}

export interface RunRequest {
  ticker: string;
  strategy: StrategyName;
  strategy_params: Record<string, number>;
  lookback_days: number;
  initial_cash: number;
  commission_pct: number;
  slippage_pct: number;
}

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: "/simulations",
  headers: { "Content-Type": "application/json" },
});

// ── API functions ─────────────────────────────────────────────────────────────

export async function runSimulation(req: RunRequest): Promise<number> {
  const res = await api.post<{ simulation_id: number }>("/run", req);
  return res.data.simulation_id;
}

export async function listSimulations(): Promise<SimSummary[]> {
  const res = await api.get<SimSummary[]>("");
  return res.data;
}

export async function getSimulation(id: number): Promise<SimDetail> {
  const res = await api.get<SimDetail>(`/${id}`);
  return res.data;
}

export async function compareSimulations(a: number, b: number): Promise<CompareResult> {
  const res = await api.get<CompareResult>(`/compare/pair?a=${a}&b=${b}`);
  return res.data;
}
