import { TrendingUp, TrendingDown } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
}

export function KpiCard({ title, value, subtitle, trend = 'neutral', icon }: KpiCardProps) {
  const trendColor = {
    up: 'text-green-500',
    down: 'text-red-500',
    neutral: 'text-gray-500',
  }[trend];

  const bgColor = {
    up: 'bg-green-50',
    down: 'bg-red-50',
    neutral: 'bg-gray-50',
  }[trend];

  return (
    <div className={`${bgColor} rounded-lg p-6 border border-gray-200 transition-all hover:shadow-md`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${trendColor}`}>
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`${trendColor}`}>
            {icon}
          </div>
        )}
        {!icon && trend !== 'neutral' && (
          <div className={trendColor}>
            {trend === 'up' ? (
              <TrendingUp className="w-6 h-6" />
            ) : (
              <TrendingDown className="w-6 h-6" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
