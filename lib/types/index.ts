// Trade and Position types
export interface Trade {
  id?: number;
  order_no: string;
  timestamp: string;
  pair: string;
  type: string;
  direction: 'LONG' | 'SHORT';
  action: 'OPEN' | 'CLOSE';
  leverage: number;
  deal_price: number;
  quantity: number;
  amount: number;
  fee: number;
  realized_pnl: number;
  avg_price?: number;
  file_source: string;
  created_at?: string;
}

export interface Position {
  id?: number;
  open_order_no: string;
  close_order_nos: string[];
  pair: string;
  direction: 'LONG' | 'SHORT';
  leverage: number;
  entry_price: number;
  exit_price: number;
  quantity: number;
  duration_seconds: number;
  gross_pnl: number;
  net_pnl: number;
  roi_percent: number;
  opened_at: string;
  closed_at: string;
}

export interface Stats {
  total_trades: number;
  total_positions: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_pnl: number;
  total_fees: number;
  net_pnl: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
  max_drawdown: number;
  sharpe_ratio: number;
  total_volume: number;
  avg_leverage: number;
  long_positions: number;
  short_positions: number;
  long_pnl: number;
  short_pnl: number;
}

export interface ChartData {
  equity_curve: Array<{ date: string; equity: number; pnl: number }>;
  daily_pnl: Array<{ date: string; pnl: number }>;
  pair_distribution: Array<{ pair: string; count: number; pnl: number }>;
  leverage_performance: Array<{ leverage: string; count: number; pnl: number }>;
  long_vs_short: {
    long: { count: number; pnl: number; win_rate: number };
    short: { count: number; pnl: number; win_rate: number };
  };
  hourly_heatmap: Array<{ hour: number; day: string; trades: number }>;
}

export interface DailySummary {
  date: string;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  gross_pnl: number;
  total_fees: number;
  net_pnl: number;
  win_rate: number;
}
