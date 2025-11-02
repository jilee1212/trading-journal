"""
Trading Journal FastAPI Backend
Processes CSV/Excel files with trading history and provides analytics
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pandas as pd
import io
from datetime import datetime
from collections import defaultdict

app = FastAPI(title="Trading Journal API")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
positions_data: List[Dict[str, Any]] = []
trades_data: List[Dict[str, Any]] = []


def parse_binance_csv(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Parse BingX/Binance Futures trading history CSV/Excel"""
    positions = []

    # Check for BingX/Binance Futures format (with Type column: Open Long/Short, Close Long/Short)
    if 'Type' in df.columns and 'Pair' in df.columns:
        return parse_bingx_futures(df)

    # Fallback to simple CSV format
    return parse_simple_csv(df)


def parse_bingx_futures(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Parse BingX Futures Order History (Perp_Futures_Order_History format)"""
    positions = []

    # Parse time column (handle different formats)
    time_col = 'Time(UTC+8)' if 'Time(UTC+8)' in df.columns else 'Time'
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.sort_values(time_col)

    # Group by Pair and track open positions
    open_positions = {}
    position_id = 1

    for _, row in df.iterrows():
        if pd.isna(row[time_col]):
            continue

        pair = row.get('Pair', '').replace('-', '')  # BTC-USDT -> BTCUSDT
        trade_type = row.get('Type', '')
        leverage = float(row.get('Leverage', '1').replace('X', ''))
        deal_price = float(row.get('DealPrice', 0))
        quantity = float(row.get('Quantity', 0))
        fee = abs(float(row.get('Fee', 0)))
        realized_pnl = float(row.get('Realized PNL', '0.0000 USDT').split()[0])
        time = row[time_col]

        if quantity == 0:
            continue

        # Determine if opening or closing position
        if 'Open Long' in trade_type:
            key = f"{pair}_LONG"
            if key not in open_positions:
                open_positions[key] = {
                    'id': f'POS_{position_id}',
                    'symbol': pair,
                    'pair': pair,
                    'direction': 'LONG',
                    'entry_time': time.isoformat(),
                    'entry_price': deal_price,
                    'quantity': quantity,
                    'entry_fee': fee,
                    'leverage': int(leverage),
                    'total_quantity': quantity,
                }
                position_id += 1
            else:
                # Adding to existing position (averaging)
                pos = open_positions[key]
                total_qty = pos['total_quantity'] + quantity
                pos['entry_price'] = (pos['entry_price'] * pos['total_quantity'] + deal_price * quantity) / total_qty
                pos['total_quantity'] = total_qty
                pos['quantity'] = total_qty
                pos['entry_fee'] += fee

        elif 'Open Short' in trade_type:
            key = f"{pair}_SHORT"
            if key not in open_positions:
                open_positions[key] = {
                    'id': f'POS_{position_id}',
                    'symbol': pair,
                    'pair': pair,
                    'direction': 'SHORT',
                    'entry_time': time.isoformat(),
                    'entry_price': deal_price,
                    'quantity': quantity,
                    'entry_fee': fee,
                    'leverage': int(leverage),
                    'total_quantity': quantity,
                }
                position_id += 1
            else:
                # Adding to existing position (averaging)
                pos = open_positions[key]
                total_qty = pos['total_quantity'] + quantity
                pos['entry_price'] = (pos['entry_price'] * pos['total_quantity'] + deal_price * quantity) / total_qty
                pos['total_quantity'] = total_qty
                pos['quantity'] = total_qty
                pos['entry_fee'] += fee

        elif 'Close Long' in trade_type:
            key = f"{pair}_LONG"
            if key in open_positions:
                pos = open_positions[key]

                # Partial or full close
                close_ratio = quantity / pos['total_quantity']

                duration = (time - pd.to_datetime(pos['entry_time'])).total_seconds()

                # Use realized PNL from the file if available, otherwise calculate
                if realized_pnl != 0:
                    net_pnl = realized_pnl
                    # Back-calculate percentage
                    position_value = pos['entry_price'] * quantity * leverage
                    roi_percent = (net_pnl / position_value * 100) if position_value > 0 else 0
                else:
                    pnl_pct = ((deal_price - pos['entry_price']) / pos['entry_price']) * 100
                    position_value = pos['entry_price'] * quantity * leverage
                    net_pnl = position_value * (pnl_pct / 100) - fee
                    roi_percent = pnl_pct

                position = {
                    **pos,
                    'exit_time': time.isoformat(),
                    'exit_price': deal_price,
                    'closed_at': time.isoformat(),
                    'quantity': quantity,
                    'exit_fee': fee,
                    'fees': pos['entry_fee'] * close_ratio + fee,
                    'duration_seconds': int(duration),
                    'net_pnl': round(net_pnl, 2),
                    'roi_percent': round(roi_percent, 2),
                    'status': 'CLOSED',
                }

                positions.append(position)

                # Update or remove position
                if close_ratio >= 0.99:  # Fully closed
                    del open_positions[key]
                else:  # Partially closed
                    pos['total_quantity'] -= quantity
                    pos['entry_fee'] *= (1 - close_ratio)

        elif 'Close Short' in trade_type:
            key = f"{pair}_SHORT"
            if key in open_positions:
                pos = open_positions[key]

                # Partial or full close
                close_ratio = quantity / pos['total_quantity']

                duration = (time - pd.to_datetime(pos['entry_time'])).total_seconds()

                # Use realized PNL from the file if available
                if realized_pnl != 0:
                    net_pnl = realized_pnl
                    position_value = pos['entry_price'] * quantity * leverage
                    roi_percent = (net_pnl / position_value * 100) if position_value > 0 else 0
                else:
                    pnl_pct = ((pos['entry_price'] - deal_price) / pos['entry_price']) * 100
                    position_value = pos['entry_price'] * quantity * leverage
                    net_pnl = position_value * (pnl_pct / 100) - fee
                    roi_percent = pnl_pct

                position = {
                    **pos,
                    'exit_time': time.isoformat(),
                    'exit_price': deal_price,
                    'closed_at': time.isoformat(),
                    'quantity': quantity,
                    'exit_fee': fee,
                    'fees': pos['entry_fee'] * close_ratio + fee,
                    'duration_seconds': int(duration),
                    'net_pnl': round(net_pnl, 2),
                    'roi_percent': round(roi_percent, 2),
                    'status': 'CLOSED',
                }

                positions.append(position)

                # Update or remove position
                if close_ratio >= 0.99:  # Fully closed
                    del open_positions[key]
                else:  # Partially closed
                    pos['total_quantity'] -= quantity
                    pos['entry_fee'] *= (1 - close_ratio)

    # Add any remaining open positions
    for pos in open_positions.values():
        pos['fees'] = pos.get('entry_fee', 0)
        pos['net_pnl'] = 0
        pos['roi_percent'] = 0
        pos['duration_seconds'] = 0
        pos['exit_price'] = pos['entry_price']
        pos['closed_at'] = pos['entry_time']
        pos['status'] = 'OPEN'
        positions.append(pos)

    return positions


def parse_simple_csv(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Parse simple CSV format (Time, Symbol, Side, Price, Quantity, Fee)"""
    positions = []

    # Group trades by symbol and approximate time to form positions
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values('Time')

    # Simple position matching: match buys with sells
    open_positions = {}
    position_id = 1

    for _, row in df.iterrows():
        symbol = row.get('Symbol', row.get('Pair', ''))
        side = row.get('Side', '').upper()
        qty = float(row.get('Executed', row.get('Qty', row.get('Quantity', 0))))
        price = float(row.get('Price', row.get('Average', 0)))
        fee = float(row.get('Fee', 0))
        time = row['Time']

        if pd.isna(qty) or qty == 0:
            continue

        key = symbol

        if side in ['BUY', 'LONG']:
            if key not in open_positions:
                open_positions[key] = {
                    'id': f'POS_{position_id}',
                    'symbol': symbol,
                    'pair': symbol,
                    'direction': 'LONG',
                    'entry_time': time.isoformat(),
                    'entry_price': price,
                    'quantity': qty,
                    'entry_fee': fee,
                    'leverage': 1,
                }
                position_id += 1
        elif side in ['SELL', 'SHORT']:
            if key in open_positions:
                pos = open_positions[key]
                duration = (time - pd.to_datetime(pos['entry_time'])).total_seconds()

                # Calculate PnL
                if pos['direction'] == 'LONG':
                    pnl_pct = ((price - pos['entry_price']) / pos['entry_price']) * 100
                else:
                    pnl_pct = ((pos['entry_price'] - price) / pos['entry_price']) * 100

                # Assume $10,000 position size
                position_value = 10000
                net_pnl = position_value * (pnl_pct / 100) - pos['entry_fee'] - fee

                position = {
                    **pos,
                    'exit_time': time.isoformat(),
                    'exit_price': price,
                    'closed_at': time.isoformat(),
                    'exit_fee': fee,
                    'fees': pos['entry_fee'] + fee,
                    'duration_seconds': int(duration),
                    'net_pnl': round(net_pnl, 2),
                    'roi_percent': round(pnl_pct, 2),
                    'status': 'CLOSED',
                }

                positions.append(position)
                del open_positions[key]

    # Add any remaining open positions
    for pos in open_positions.values():
        pos['fees'] = pos.get('entry_fee', 0)
        pos['net_pnl'] = 0
        pos['roi_percent'] = 0
        pos['duration_seconds'] = 0
        pos['exit_price'] = pos['entry_price']
        pos['closed_at'] = pos['entry_time']
        pos['status'] = 'OPEN'
        positions.append(pos)

    return positions


def calculate_stats(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate trading statistics"""
    if not positions:
        return {
            'total_positions': 0,
            'total_trades': 0,
            'net_pnl': 0,
            'total_pnl': 0,
            'total_fees': 0,
            'total_volume': 0,
            'win_rate': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
        }

    closed_positions = [p for p in positions if p['status'] == 'CLOSED']

    total_pnl = sum(p['net_pnl'] for p in closed_positions)
    total_fees = sum(p.get('fees', 0) for p in positions)

    winning_trades = [p for p in closed_positions if p['net_pnl'] > 0]
    losing_trades = [p for p in closed_positions if p['net_pnl'] < 0]

    avg_win = sum(p['net_pnl'] for p in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(p['net_pnl'] for p in losing_trades) / len(losing_trades) if losing_trades else 0

    # Estimate volume (assuming $10k position size)
    total_volume = len(closed_positions) * 10000

    return {
        'total_positions': len(positions),
        'total_trades': len(closed_positions),
        'net_pnl': round(total_pnl, 2),
        'total_pnl': round(total_pnl + total_fees, 2),
        'total_fees': round(total_fees, 2),
        'total_volume': total_volume,
        'win_rate': round((len(winning_trades) / len(closed_positions) * 100) if closed_positions else 0, 2),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
    }


def calculate_chart_data(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate chart data"""
    if not positions:
        return {
            'equity_curve': [],
            'daily_pnl': [],
            'pair_distribution': [],
            'long_vs_short': {
                'long': {'count': 0, 'pnl': 0, 'win_rate': 0},
                'short': {'count': 0, 'pnl': 0, 'win_rate': 0},
            }
        }

    closed_positions = [p for p in positions if p['status'] == 'CLOSED']
    sorted_positions = sorted(closed_positions, key=lambda x: x['closed_at'])

    # Equity curve
    equity = 10000  # Starting equity
    equity_curve = []
    for pos in sorted_positions:
        equity += pos['net_pnl']
        equity_curve.append({
            'date': pos['closed_at'].split('T')[0],
            'equity': round(equity, 2),
            'pnl': round(pos['net_pnl'], 2),
        })

    # Daily PnL
    daily_pnl_dict = defaultdict(float)
    for pos in sorted_positions:
        date = pos['closed_at'].split('T')[0]
        daily_pnl_dict[date] += pos['net_pnl']

    daily_pnl = [
        {'date': date, 'pnl': round(pnl, 2)}
        for date, pnl in sorted(daily_pnl_dict.items())
    ]

    # Pair distribution
    pair_stats = defaultdict(lambda: {'count': 0, 'pnl': 0})
    for pos in closed_positions:
        pair = pos['pair']
        pair_stats[pair]['count'] += 1
        pair_stats[pair]['pnl'] += pos['net_pnl']

    pair_distribution = [
        {'pair': pair, 'count': stats['count'], 'pnl': round(stats['pnl'], 2)}
        for pair, stats in sorted(pair_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    ]

    # Long vs Short
    long_positions = [p for p in closed_positions if p['direction'] == 'LONG']
    short_positions = [p for p in closed_positions if p['direction'] == 'SHORT']

    long_winning = len([p for p in long_positions if p['net_pnl'] > 0])
    short_winning = len([p for p in short_positions if p['net_pnl'] > 0])

    long_vs_short = {
        'long': {
            'count': len(long_positions),
            'pnl': round(sum(p['net_pnl'] for p in long_positions), 2),
            'win_rate': round((long_winning / len(long_positions) * 100) if long_positions else 0, 2),
        },
        'short': {
            'count': len(short_positions),
            'pnl': round(sum(p['net_pnl'] for p in short_positions), 2),
            'win_rate': round((short_winning / len(short_positions) * 100) if short_positions else 0, 2),
        }
    }

    return {
        'equity_curve': equity_curve,
        'daily_pnl': daily_pnl,
        'pair_distribution': pair_distribution,
        'long_vs_short': long_vs_short,
    }


@app.get("/")
def read_root():
    return {"message": "Trading Journal API", "version": "1.0.0"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process trading history file"""
    try:
        # Read file
        contents = await file.read()

        # Determine file type and parse
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or Excel.")

        # Parse positions
        global positions_data
        positions_data = parse_binance_csv(df)

        return {
            "message": "File processed successfully",
            "trades_processed": len(positions_data),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/stats")
def get_stats():
    """Get trading statistics"""
    return calculate_stats(positions_data)


@app.get("/api/chart-data")
def get_chart_data():
    """Get chart data"""
    return calculate_chart_data(positions_data)


@app.get("/api/positions")
def get_positions(limit: int = 100, offset: int = 0):
    """Get positions list"""
    return {
        "positions": positions_data[offset:offset + limit],
        "total": len(positions_data),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
