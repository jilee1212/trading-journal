"""
Trading Journal FastAPI Backend
Processes CSV/Excel files with trading history and provides analytics
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pandas as pd
import io
import os
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from database import TradingDatabase

app = FastAPI(title="Trading Journal API")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database instance
db = TradingDatabase()

# CSV folder path (configurable via environment variable)
CSV_FOLDER = os.getenv("CSV_FOLDER_PATH", "./csv_data")


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

    for _, row in df.iterrows():
        if pd.isna(row[time_col]):
            continue

        pair = row.get('Pair', '').replace('-', '')  # BTC-USDT -> BTCUSDT
        trade_type = row.get('Type', '')
        leverage = float(row.get('Leverage', '1').replace('X', ''))
        deal_price = float(row.get('DealPrice', 0))
        quantity = float(row.get('Quantity', 0))
        fee = abs(float(row.get('Fee', 0)))

        # Handle Realized PNL - can be float or string with USDT suffix
        pnl_value = row.get('Realized PNL', 0)
        if isinstance(pnl_value, str):
            realized_pnl = float(pnl_value.split()[0]) if pnl_value.strip() else 0
        else:
            realized_pnl = float(pnl_value) if not pd.isna(pnl_value) else 0

        time = row[time_col]

        if quantity == 0:
            continue

        # Determine if opening or closing position
        if 'Open Long' in trade_type:
            key = f"{pair}_LONG"
            if key not in open_positions:
                # Generate unique ID using hash of key attributes
                unique_str = f"{pair}_LONG_{time.isoformat()}_{deal_price}_{quantity}"
                pos_id = hashlib.md5(unique_str.encode()).hexdigest()[:16]
                open_positions[key] = {
                    'id': pos_id,
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
                # Generate unique ID using hash of key attributes
                unique_str = f"{pair}_SHORT_{time.isoformat()}_{deal_price}_{quantity}"
                pos_id = hashlib.md5(unique_str.encode()).hexdigest()[:16]
                open_positions[key] = {
                    'id': pos_id,
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

                # Generate unique ID for this closed position
                closed_pos_str = f"{pair}_LONG_{pos['entry_time']}_{time.isoformat()}_{quantity}_{deal_price}"
                closed_pos_id = hashlib.md5(closed_pos_str.encode()).hexdigest()[:16]

                position = {
                    **pos,
                    'id': closed_pos_id,  # Override with unique closed position ID
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

                # Generate unique ID for this closed position
                closed_pos_str = f"{pair}_SHORT_{pos['entry_time']}_{time.isoformat()}_{quantity}_{deal_price}"
                closed_pos_id = hashlib.md5(closed_pos_str.encode()).hexdigest()[:16]

                position = {
                    **pos,
                    'id': closed_pos_id,  # Override with unique closed position ID
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
                # Generate unique ID based on trade characteristics
                unique_str = f"{symbol}_LONG_{time.isoformat()}_{price}_{qty}"
                pos_id = hashlib.md5(unique_str.encode()).hexdigest()[:16]
                open_positions[key] = {
                    'id': pos_id,
                    'symbol': symbol,
                    'pair': symbol,
                    'direction': 'LONG',
                    'entry_time': time.isoformat(),
                    'entry_price': price,
                    'quantity': qty,
                    'entry_fee': fee,
                    'leverage': 1,
                }
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

        # Determine file type and parse - try Excel first (BingX uses .csv extension for Excel files)
        df = None

        # Try Excel format first
        try:
            # Use openpyxl with data_only mode to avoid style parsing issues
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True, read_only=True)
            df = pd.DataFrame(wb.active.values)
            # Set first row as headers
            df.columns = df.iloc[0]
            df = df[1:]
            df.reset_index(drop=True, inplace=True)
        except Exception:
            # If Excel fails, try CSV with multiple encodings
            if file.filename.endswith('.csv'):
                for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin1']:
                    try:
                        df = pd.read_csv(io.BytesIO(contents), encoding=encoding)
                        break
                    except (UnicodeDecodeError, Exception):
                        continue

        if df is None:
            raise HTTPException(status_code=400, detail="Could not read file. Unsupported format or encoding.")

        # Parse positions
        positions = parse_binance_csv(df)

        # Save to database
        new_positions = 0
        for position in positions:
            if db.insert_position(position):
                new_positions += 1

        return {
            "message": "File processed successfully",
            "trades_processed": len(positions),
            "new_positions": new_positions,
            "duplicates_skipped": len(positions) - new_positions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/stats")
def get_stats():
    """Get trading statistics"""
    positions = db.get_all_positions()
    return calculate_stats(positions)


@app.get("/api/chart-data")
def get_chart_data():
    """Get chart data"""
    positions = db.get_all_positions()
    return calculate_chart_data(positions)


@app.get("/api/positions")
def get_positions(limit: int = 100, offset: int = 0):
    """Get positions list"""
    positions = db.get_all_positions(limit=limit, offset=offset)
    total = db.get_total_positions_count()
    return {
        "positions": positions,
        "total": total,
    }


@app.post("/api/scan-folder")
async def scan_folder(folder_path: str = None):
    """Scan a folder for CSV files and process all new files"""
    try:
        path = folder_path or CSV_FOLDER

        # Create folder if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)

        # Find all CSV and Excel files
        csv_files = list(Path(path).glob("*.csv"))
        excel_files = list(Path(path).glob("*.xlsx")) + list(Path(path).glob("*.xls"))
        all_files = csv_files + excel_files

        if not all_files:
            return {
                "message": f"No CSV or Excel files found in {path}",
                "processed": 0,
                "skipped": 0,
                "total_positions": 0,
            }

        processed = 0
        skipped = 0
        total_new_positions = 0

        for file_path in all_files:
            filename = file_path.name

            # Skip if already processed
            if db.is_file_processed(filename):
                skipped += 1
                continue

            try:
                # Read and parse file - try Excel first (BingX uses .csv extension for Excel files)
                df = None

                # Try Excel format first (BingX exports as Excel with .csv extension)
                try:
                    # Use openpyxl with data_only mode to avoid style parsing issues
                    # Read file as bytes to bypass extension check
                    import openpyxl
                    with open(file_path, 'rb') as f:
                        wb = openpyxl.load_workbook(f, data_only=True, read_only=True)
                    df = pd.DataFrame(wb.active.values)
                    # Set first row as headers
                    df.columns = df.iloc[0]
                    df = df[1:]
                    df.reset_index(drop=True, inplace=True)
                except Exception:
                    # If Excel fails, try CSV with multiple encodings
                    if filename.endswith('.csv'):
                        for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin1']:
                            try:
                                df = pd.read_csv(file_path, encoding=encoding)
                                break
                            except (UnicodeDecodeError, Exception):
                                continue

                if df is None:
                    raise ValueError(f"Could not read file {filename}")

                positions = parse_binance_csv(df)

                # Save to database
                new_positions = 0
                for position in positions:
                    if db.insert_position(position):
                        new_positions += 1

                # Mark file as processed
                db.mark_file_processed(filename, str(file_path), len(positions))

                processed += 1
                total_new_positions += new_positions

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue

        return {
            "message": f"Folder scan complete",
            "processed": processed,
            "skipped": skipped,
            "total_files": len(all_files),
            "new_positions": total_new_positions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning folder: {str(e)}")


@app.get("/api/processed-files")
def get_processed_files():
    """Get list of processed files"""
    return {
        "files": db.get_processed_files()
    }


@app.delete("/api/clear")
def clear_data():
    """Clear all data (for testing/reset)"""
    try:
        db.clear_all_data()
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
