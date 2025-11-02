import { Stats, ChartData, Trade, Position } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  /**
   * Upload a CSV/Excel file
   */
  static async uploadFile(file: File): Promise<{
    success: boolean;
    message: string;
    trades_processed: number;
    errors: number;
    total_trades: number;
    total_positions: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload file');
    }

    return response.json();
  }

  /**
   * Get all trades
   */
  static async getTrades(params?: {
    pair?: string;
    direction?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    trades: Trade[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.pair) queryParams.append('pair', params.pair);
    if (params?.direction) queryParams.append('direction', params.direction);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = `${API_BASE_URL}/api/trades${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch trades');
    }

    return response.json();
  }

  /**
   * Get all positions
   */
  static async getPositions(params?: {
    pair?: string;
    direction?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    positions: Position[];
    total: number;
    limit: number;
    offset: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.pair) queryParams.append('pair', params.pair);
    if (params?.direction) queryParams.append('direction', params.direction);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = `${API_BASE_URL}/api/positions${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to fetch positions');
    }

    return response.json();
  }

  /**
   * Get trading statistics
   */
  static async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/api/stats`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch stats');
    }

    return response.json();
  }

  /**
   * Get chart data
   */
  static async getChartData(): Promise<ChartData> {
    const response = await fetch(`${API_BASE_URL}/api/chart-data`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch chart data');
    }

    return response.json();
  }

  /**
   * Trigger recalculation
   */
  static async recalculate(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/recalculate`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to recalculate');
    }

    return response.json();
  }

  /**
   * Clear all data
   */
  static async clearAll(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/clear`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to clear data');
    }

    return response.json();
  }

  /**
   * Check API health
   */
  static async healthCheck(): Promise<{
    status: string;
    version: string;
    trades_count: number;
    positions_count: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/`);

    if (!response.ok) {
      throw new Error('API is not responding');
    }

    return response.json();
  }
}
