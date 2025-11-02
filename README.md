# Crypto Trading Journal

A comprehensive trading journal application for analyzing cryptocurrency trading performance. Built with Next.js and FastAPI.

## Features

- **CSV/Excel Import**: Upload your trading history from BingX, Binance, or other exchanges
- **Performance Analytics**: Track win rate, PnL, ROI, and other key metrics
- **Interactive Charts**:
  - Equity curve visualization
  - Daily PnL bar chart
  - Trading pair distribution
  - Long vs Short performance comparison
- **Position History**: Detailed table with sorting and pagination
- **Real-time Statistics**: KPI cards showing overall performance

## Tech Stack

### Frontend
- Next.js 16 (React 19)
- TypeScript
- Tailwind CSS 4
- Recharts (data visualization)
- TanStack Table (data tables)

### Backend
- FastAPI (Python)
- Pandas (data processing)
- Uvicorn (ASGI server)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm/yarn/pnpm

### Installation

1. **Install frontend dependencies**
```bash
npm install
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### Running the Application

1. **Start the backend server** (Terminal 1)
```bash
cd backend
python main.py
```
The API will be available at [http://localhost:8000](http://localhost:8000)

2. **Start the frontend** (Terminal 2)
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser

### Usage

1. Click "Upload CSV/Excel" button
2. Select your trading history file (CSV or Excel format)
3. Wait for processing
4. View your analytics and performance metrics

## Supported File Formats

### BingX Futures Order History (Recommended)
The application automatically detects BingX Perpetual Futures Order History format:

**File name**: `Perp_Futures_Order_History_YYYY_MM_DD.csv` (Excel format)

**Required columns**:
- `Time(UTC+8)`: Trade timestamp
- `Pair`: Trading pair (e.g., BTC-USDT, ETH-USDT)
- `Type`: Open Long/Short, Close Long/Short
- `Leverage`: Leverage multiplier (e.g., 3X, 5X)
- `DealPrice`: Execution price
- `Quantity`: Amount traded
- `Fee`: Trading fee
- `Realized PNL`: Profit/Loss in USDT

### Simple CSV Format
Alternative simple CSV format:

```csv
Time,Symbol,Side,Price,Executed,Fee
2024-01-01 10:00:00,BTCUSDT,BUY,45000,0.1,4.5
2024-01-01 12:00:00,BTCUSDT,SELL,45500,0.1,4.55
```

Required columns:
- `Time` or `Date`: Trade timestamp
- `Symbol` or `Pair`: Trading pair (e.g., BTCUSDT)
- `Side`: BUY/SELL or LONG/SHORT
- `Price` or `Average`: Trade price
- `Executed` or `Qty`: Quantity traded
- `Fee`: Trading fee

## Project Structure

```
trading-journal/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Main dashboard page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── lib/
│   ├── components/        # React components
│   │   ├── file-upload.tsx
│   │   ├── kpi-card.tsx
│   │   ├── equity-curve-chart.tsx
│   │   ├── daily-pnl-chart.tsx
│   │   ├── pair-distribution-chart.tsx
│   │   └── trades-table.tsx
│   └── types.ts           # TypeScript type definitions
├── backend/
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
└── package.json           # Node.js dependencies
```

## API Endpoints

- `GET /` - API health check
- `POST /api/upload` - Upload trading history file
- `GET /api/stats` - Get trading statistics
- `GET /api/chart-data` - Get chart data
- `GET /api/positions?limit=100&offset=0` - Get positions list

## Development

### Frontend Development
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend Development
```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
