// Trading Journal Type Definitions

export interface Stats {
  total_positions: number;
  total_trades: number;
  net_pnl: number;
  total_pnl: number;
  total_fees: number;
  total_volume: number;
  win_rate: number;
  winning_trades: number;
  losing_trades: number;
  avg_win: number;
  avg_loss: number;
}

export interface EquityCurvePoint {
  date: string;
  equity: number;
  pnl: number;
}

export interface DailyPnlPoint {
  date: string;
  pnl: number;
}

export interface PairDistribution {
  pair: string;
  count: number;
  trades?: number;
  pnl: number;
  winRate?: number;
}

export interface LongShortPerformance {
  long: {
    count: number;
    pnl: number;
    win_rate: number;
  };
  short: {
    count: number;
    pnl: number;
    win_rate: number;
  };
}

export interface ChartData {
  equity_curve: EquityCurvePoint[];
  daily_pnl: DailyPnlPoint[];
  pair_distribution: PairDistribution[];
  long_vs_short: LongShortPerformance;
}

export interface Position {
  id: string;
  symbol: string;
  pair: string;
  side: 'LONG' | 'SHORT';
  direction: 'LONG' | 'SHORT';
  entry_time: string;
  entry_price: number;
  exit_time?: string;
  exit_price: number;
  closed_at: string;
  quantity: number;
  leverage: number;
  duration_seconds: number;
  pnl?: number;
  net_pnl: number;
  pnl_percent?: number;
  roi_percent: number;
  fees: number;
  status: 'OPEN' | 'CLOSED';
}

export interface Trade {
  id: string;
  position_id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  price: number;
  quantity: number;
  fee: number;
  time: string;
}
