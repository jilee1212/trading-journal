'use client';

import { useState, useEffect } from 'react';
import { FileUpload } from '@/lib/components/file-upload';
import { KpiCard } from '@/lib/components/kpi-card';
import { EquityCurveChart } from '@/lib/components/equity-curve-chart';
import { DailyPnlChart } from '@/lib/components/daily-pnl-chart';
import { PairDistributionChart } from '@/lib/components/pair-distribution-chart';
import { TradesTable } from '@/lib/components/trades-table';
import { Stats, ChartData, Position } from '@/lib/types';
import { TrendingUp, Activity, Target, DollarSign, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch stats
      const statsResponse = await fetch('http://localhost:8000/api/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch chart data
      const chartResponse = await fetch('http://localhost:8000/api/chart-data');
      if (chartResponse.ok) {
        const chartDataResponse = await chartResponse.json();
        setChartData(chartDataResponse);
      }

      // Fetch positions
      const positionsResponse = await fetch('http://localhost:8000/api/positions?limit=1000');
      if (positionsResponse.ok) {
        const positionsData = await positionsResponse.json();
        setPositions(positionsData.positions);
      }
    } catch (err) {
      setError('Failed to connect to API. Make sure the Python backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUploadSuccess = () => {
    fetchData();
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Crypto Trading Journal</h1>
              <p className="text-sm text-gray-600 mt-1">Track, analyze, and improve your trading performance</p>
            </div>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {!stats ? (
          <div className="text-center py-16">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Data Yet</h2>
            <p className="text-gray-600">Upload your trading history CSV to get started</p>
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
              <KpiCard
                title="Net P&L"
                value={`$${stats.net_pnl.toFixed(2)}`}
                subtitle={`Gross: $${stats.total_pnl.toFixed(2)}`}
                trend={stats.net_pnl >= 0 ? 'up' : 'down'}
                icon={<DollarSign className="w-6 h-6" />}
              />
              <KpiCard
                title="Total Positions"
                value={stats.total_positions}
                subtitle={`${stats.total_trades} trades`}
                trend="neutral"
                icon={<Activity className="w-6 h-6" />}
              />
              <KpiCard
                title="Win Rate"
                value={`${stats.win_rate.toFixed(1)}%`}
                subtitle={`${stats.winning_trades}W / ${stats.losing_trades}L`}
                trend={stats.win_rate >= 50 ? 'up' : 'down'}
                icon={<Target className="w-6 h-6" />}
              />
              <KpiCard
                title="Avg P&L"
                value={`$${stats.avg_win.toFixed(2)}`}
                subtitle={`Loss: $${stats.avg_loss.toFixed(2)}`}
                trend={stats.avg_win > Math.abs(stats.avg_loss) ? 'up' : 'down'}
                icon={<TrendingUp className="w-6 h-6" />}
              />
              <KpiCard
                title="Fees Paid"
                value={`$${Math.abs(stats.total_fees).toFixed(2)}`}
                subtitle={`${((Math.abs(stats.total_fees) / stats.total_volume) * 100).toFixed(3)}% of volume`}
                trend="neutral"
              />
            </div>

            {/* Charts Section */}
            {chartData && (
              <>
                {/* Equity Curve */}
                <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Equity Curve</h2>
                  <EquityCurveChart data={chartData.equity_curve} />
                </div>

                {/* Daily P&L */}
                <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Daily P&L</h2>
                  <DailyPnlChart data={chartData.daily_pnl} />
                </div>

                {/* Analysis Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {/* Pair Distribution */}
                  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Pair Distribution</h2>
                    <PairDistributionChart data={chartData.pair_distribution} />
                  </div>

                  {/* Long vs Short Performance */}
                  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Long vs Short Performance</h2>
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-blue-900">LONG Positions</span>
                          <span className="text-xs text-blue-700">{chartData.long_vs_short.long.count} trades</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className={`text-2xl font-bold ${chartData.long_vs_short.long.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {chartData.long_vs_short.long.pnl >= 0 ? '+' : ''}${chartData.long_vs_short.long.pnl.toFixed(2)}
                          </span>
                          <span className="text-sm text-blue-700">
                            Win Rate: {chartData.long_vs_short.long.win_rate.toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-purple-900">SHORT Positions</span>
                          <span className="text-xs text-purple-700">{chartData.long_vs_short.short.count} trades</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className={`text-2xl font-bold ${chartData.long_vs_short.short.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {chartData.long_vs_short.short.pnl >= 0 ? '+' : ''}${chartData.long_vs_short.short.pnl.toFixed(2)}
                          </span>
                          <span className="text-sm text-purple-700">
                            Win Rate: {chartData.long_vs_short.short.win_rate.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Trades Table */}
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Position History</h2>
              <TradesTable positions={positions} />
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Crypto Trading Journal - Built with Next.js & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}
