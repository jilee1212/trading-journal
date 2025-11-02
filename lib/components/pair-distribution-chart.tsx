'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface PairDistributionData {
  pair: string;
  count: number;
  pnl: number;
}

interface PairDistributionChartProps {
  data: PairDistributionData[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function PairDistributionChart({ data }: PairDistributionChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  // Calculate percentages
  const total = data.reduce((sum, item) => sum + item.count, 0);
  const chartData = data.map(item => ({
    ...item,
    percentage: ((item.count / total) * 100).toFixed(1)
  }));

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ pair, percentage }) => `${pair} (${percentage}%)`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="count"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="text-sm font-bold text-gray-900">{data.pair}</p>
                    <p className="text-xs text-gray-600">Trades: {data.count} ({data.percentage}%)</p>
                    <p className={`text-xs ${data.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      PnL: {data.pnl >= 0 ? '+' : ''}${data.pnl.toFixed(2)}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
