import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
} from "@mui/material";
import type { Trade } from "@/api/client";

interface Props {
  trades: Trade[];
}

export default function TradesTable({ trades }: Props) {
  if (trades.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ p: 2 }}>
        No trades for this simulation.
      </Typography>
    );
  }

  return (
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            {["Date", "Side", "Qty", "Price", "Fees", "Slippage", "PnL"].map((h) => (
              <TableCell key={h} sx={{ fontWeight: 700, color: "text.secondary" }}>
                {h}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {trades.map((t) => (
            <TableRow key={t.id} hover>
              <TableCell>{t.timestamp.slice(0, 10)}</TableCell>
              <TableCell>
                <Chip
                  label={t.side}
                  size="small"
                  color={t.side === "BUY" ? "success" : "error"}
                  variant="outlined"
                />
              </TableCell>
              <TableCell>{t.qty.toFixed(4)}</TableCell>
              <TableCell>${t.price.toFixed(2)}</TableCell>
              <TableCell>${t.fees.toFixed(2)}</TableCell>
              <TableCell>${t.slippage.toFixed(2)}</TableCell>
              <TableCell
                sx={{
                  color:
                    t.pnl == null
                      ? "text.secondary"
                      : t.pnl >= 0
                      ? "success.main"
                      : "error.main",
                  fontWeight: 600,
                }}
              >
                {t.pnl == null ? "—" : `$${t.pnl.toFixed(2)}`}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
