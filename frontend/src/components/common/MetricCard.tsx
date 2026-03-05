import { Card, CardContent, Typography, Box } from "@mui/material";

interface Props {
  title: string;
  value: string | number;
  unit?: string;
  color?: string;
}

export default function MetricCard({ title, value, unit, color }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
          {title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "baseline", gap: 0.5, mt: 1 }}>
          <Typography variant="h4" fontWeight={700} sx={{ color: color ?? "primary.main" }}>
            {value}
          </Typography>
          {unit && (
            <Typography variant="body2" color="text.secondary">
              {unit}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
