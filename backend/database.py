"""
SQLite Database Manager for Trading Journal
Handles persistent storage of trading positions and metadata
"""

import sqlite3
import json
from typing import List, Dict, Any
from datetime import datetime
import os


class TradingDatabase:
    def __init__(self, db_path: str = "trading_journal.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                pair TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                closed_at TEXT,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                leverage INTEGER DEFAULT 1,
                entry_fee REAL DEFAULT 0,
                exit_fee REAL DEFAULT 0,
                fees REAL DEFAULT 0,
                net_pnl REAL DEFAULT 0,
                roi_percent REAL DEFAULT 0,
                duration_seconds INTEGER DEFAULT 0,
                status TEXT DEFAULT 'OPEN',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Processed files table (to track which CSV files have been imported)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                filename TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                positions_count INTEGER DEFAULT 0
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_positions_closed_at
            ON positions(closed_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_positions_status
            ON positions(status)
        """)

        conn.commit()
        conn.close()

    def is_file_processed(self, filename: str) -> bool:
        """Check if a file has already been processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT filename FROM processed_files WHERE filename = ?",
            (filename,)
        )
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def mark_file_processed(self, filename: str, file_path: str, positions_count: int):
        """Mark a file as processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO processed_files
            (filename, file_path, processed_at, positions_count)
            VALUES (?, ?, ?, ?)
        """, (filename, file_path, datetime.now().isoformat(), positions_count))

        conn.commit()
        conn.close()

    def get_processed_files(self) -> List[Dict[str, Any]]:
        """Get list of processed files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT filename, file_path, processed_at, positions_count
            FROM processed_files
            ORDER BY processed_at DESC
        """)

        files = []
        for row in cursor.fetchall():
            files.append({
                'filename': row[0],
                'file_path': row[1],
                'processed_at': row[2],
                'positions_count': row[3],
            })

        conn.close()
        return files

    def insert_position(self, position: Dict[str, Any]) -> bool:
        """Insert a new position (skip if duplicate based on unique characteristics)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for duplicate based on key fields
        cursor.execute("""
            SELECT id FROM positions
            WHERE symbol = ? AND entry_time = ? AND entry_price = ? AND quantity = ?
        """, (
            position.get('symbol'),
            position.get('entry_time'),
            position.get('entry_price'),
            position.get('quantity')
        ))

        if cursor.fetchone():
            conn.close()
            return False  # Duplicate, skip

        now = datetime.now().isoformat()

        try:
            cursor.execute("""
                INSERT INTO positions (
                    id, symbol, pair, direction, entry_time, exit_time, closed_at,
                    entry_price, exit_price, quantity, leverage, entry_fee, exit_fee,
                    fees, net_pnl, roi_percent, duration_seconds, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                position.get('id'),
                position.get('symbol'),
                position.get('pair'),
                position.get('direction'),
                position.get('entry_time'),
                position.get('exit_time'),
                position.get('closed_at'),
                position.get('entry_price'),
                position.get('exit_price'),
                position.get('quantity'),
                position.get('leverage', 1),
                position.get('entry_fee', 0),
                position.get('exit_fee', 0),
                position.get('fees', 0),
                position.get('net_pnl', 0),
                position.get('roi_percent', 0),
                position.get('duration_seconds', 0),
                position.get('status', 'OPEN'),
                now,
                now
            ))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Duplicate ID or constraint violation, skip
            conn.close()
            return False

    def get_all_positions(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all positions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT id, symbol, pair, direction, entry_time, exit_time, closed_at,
                   entry_price, exit_price, quantity, leverage, entry_fee, exit_fee,
                   fees, net_pnl, roi_percent, duration_seconds, status
            FROM positions
            ORDER BY entry_time DESC
        """

        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"

        cursor.execute(query)

        positions = []
        for row in cursor.fetchall():
            positions.append({
                'id': row[0],
                'symbol': row[1],
                'pair': row[2],
                'direction': row[3],
                'entry_time': row[4],
                'exit_time': row[5],
                'closed_at': row[6],
                'entry_price': row[7],
                'exit_price': row[8],
                'quantity': row[9],
                'leverage': row[10],
                'entry_fee': row[11],
                'exit_fee': row[12],
                'fees': row[13],
                'net_pnl': row[14],
                'roi_percent': row[15],
                'duration_seconds': row[16],
                'status': row[17],
            })

        conn.close()
        return positions

    def get_total_positions_count(self) -> int:
        """Get total count of positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM positions")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def clear_all_data(self):
        """Clear all positions and processed files (for testing/reset)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM positions")
        cursor.execute("DELETE FROM processed_files")

        conn.commit()
        conn.close()
