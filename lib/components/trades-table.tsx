'use client';

import { useState } from 'react';
import { Position } from '../types';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface TradesTableProps {
  positions: Position[];
}

type SortField = 'closed_at' | 'pair' | 'direction' | 'net_pnl' | 'roi_percent';
type SortOrder = 'asc' | 'desc';

export function TradesTable({ positions }: TradesTableProps) {
  const [sortField, setSortField] = useState<SortField>('closed_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Sort positions
  const sortedPositions = [...positions].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (sortField === 'closed_at' || sortField === 'pair' || sortField === 'direction') {
      aValue = String(aValue);
      bValue = String(bValue);
      return sortOrder === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }

    const numA = Number(aValue);
    const numB = Number(bValue);
    return sortOrder === 'asc' ? numA - numB : numB - numA;
  });

  // Paginate
  const totalPages = Math.ceil(sortedPositions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedPositions = sortedPositions.slice(startIndex, startIndex + itemsPerPage);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />;
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (!positions || positions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No positions available
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-700">#</th>
              <th
                className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('closed_at')}
              >
                <div className="flex items-center gap-1">
                  Time <SortIcon field="closed_at" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('pair')}
              >
                <div className="flex items-center gap-1">
                  Pair <SortIcon field="pair" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('direction')}
              >
                <div className="flex items-center gap-1">
                  Type <SortIcon field="direction" />
                </div>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Entry</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Exit</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Qty</th>
              <th className="px-4 py-3 text-center font-medium text-gray-700">Leverage</th>
              <th className="px-4 py-3 text-center font-medium text-gray-700">Duration</th>
              <th
                className="px-4 py-3 text-right font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('net_pnl')}
              >
                <div className="flex items-center justify-end gap-1">
                  PnL <SortIcon field="net_pnl" />
                </div>
              </th>
              <th
                className="px-4 py-3 text-right font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('roi_percent')}
              >
                <div className="flex items-center justify-end gap-1">
                  ROI% <SortIcon field="roi_percent" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {paginatedPositions.map((position, index) => (
              <tr key={position.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-gray-600">{startIndex + index + 1}</td>
                <td className="px-4 py-3 text-gray-900">
                  {new Date(position.closed_at).toLocaleString('en-US', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </td>
                <td className="px-4 py-3 font-medium text-gray-900">{position.pair}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    position.direction === 'LONG'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                  }`}>
                    {position.direction}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-gray-900">
                  ${position.entry_price.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-gray-900">
                  ${position.exit_price.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-gray-600">
                  {position.quantity.toFixed(4)}
                </td>
                <td className="px-4 py-3 text-center text-gray-600">
                  {position.leverage}X
                </td>
                <td className="px-4 py-3 text-center text-gray-600">
                  {formatDuration(position.duration_seconds)}
                </td>
                <td className={`px-4 py-3 text-right font-semibold ${
                  position.net_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {position.net_pnl >= 0 ? '+' : ''}${position.net_pnl.toFixed(2)}
                </td>
                <td className={`px-4 py-3 text-right font-semibold ${
                  position.roi_percent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {position.roi_percent >= 0 ? '+' : ''}{position.roi_percent.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-600">
            Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, positions.length)} of {positions.length} positions
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
