# Trading Journal

BingX 거래 내역을 분석하는 웹 대시보드입니다. 자동으로 CSV 파일을 파싱하여 거래 통계, 수익률 곡선, 차트 등을 제공합니다.

## 주요 기능

- **자동 CSV 파싱** - BingX 거래 내역 CSV를 자동으로 분석
- **실시간 대시보드** - KPI, 승률, 샤프 비율 등 주요 지표 표시
- **데이터 영구 저장** - SQLite로 거래 내역 누적 관리
- **일괄 업데이트** - 폴더에 CSV 추가 후 BAT 파일로 원클릭 업데이트
- **차트 시각화**:
  - 수익률 곡선 (Equity Curve)
  - 일별 손익 (Daily PnL)
  - 페어별 분포 (Pair Distribution)
  - 롱/숏 성과 비교
- **포지션 관리** - 전체 거래 내역 테이블 (정렬, 페이지네이션)

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

**방법 1: BAT 파일 사용 (Windows 추천)**

1. **백엔드 시작**
```bash
start-backend.bat
```

2. **프론트엔드 시작** (새 터미널)
```bash
npm run dev
```

3. 브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

**방법 2: 직접 실행**

1. **백엔드 서버 시작** (Terminal 1)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **프론트엔드 시작** (Terminal 2)
```bash
npm run dev
```

## 사용 방법

### 자동 업데이트 (추천)

1. **CSV 파일 저장**
   - `backend/csv_data` 폴더에 BingX CSV 파일 복사
   - 파일 예시: `Perp_Futures_Order_History_2025_11_03.csv`

2. **대시보드 업데이트**
   ```bash
   update-dashboard.bat
   ```
   - 모든 새 CSV 파일 자동 스캔
   - 중복 방지 (이미 처리된 파일은 건너뜀)
   - 데이터베이스 자동 업데이트

3. **브라우저 새로고침**
   - 최신 거래 데이터 확인

### 수동 업로드

1. 웹 대시보드 접속
2. "Upload CSV/Excel" 버튼 클릭
3. CSV/Excel 파일 선택 또는 드래그 앤 드롭
4. 자동 분석 및 차트 표시

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

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/` | 헬스체크 |
| POST | `/api/upload` | CSV 파일 업로드 |
| POST | `/api/scan-folder` | 폴더 스캔 및 일괄 처리 |
| GET | `/api/stats` | 거래 통계 조회 |
| GET | `/api/chart-data` | 차트 데이터 조회 |
| GET | `/api/positions` | 포지션 목록 조회 |
| GET | `/api/processed-files` | 처리된 파일 목록 |
| DELETE | `/api/clear` | 모든 데이터 초기화 |

## 환경 설정

`backend/.env` 파일을 생성하여 설정 커스터마이징:

```env
# CSV 폴더 경로
CSV_FOLDER_PATH=./csv_data

# 또는 절대 경로 사용
# CSV_FOLDER_PATH=C:\Users\YourName\Documents\BingX_Exports
```

## 배포

### 프론트엔드 (Vercel)

1. GitHub 저장소와 Vercel 연결
2. 프로젝트 import
3. 환경 변수 설정:
   - `NEXT_PUBLIC_API_URL`: 백엔드 URL (예: `http://localhost:8000`)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### 백엔드

**로컬 실행 (추천)**
- CSV 폴더 접근이 필요하므로 로컬에서 실행
- `start-backend.bat` 사용

**클라우드 배포 (Render/Railway)**
- 파일 업로드 방식만 지원
- 폴더 스캔 기능은 로컬 전용

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
