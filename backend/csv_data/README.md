# CSV Data Folder

이 폴더에 BingX CSV 파일을 저장하세요.

## 사용 방법

1. BingX에서 거래 내역 다운로드
   - 파일 형식: CSV 또는 Excel (.xlsx, .xls)
   - 예시 파일명: `Perp_Futures_Order_History_2025_11_03.csv`

2. 다운로드한 파일을 이 폴더에 복사

3. 루트 디렉토리에서 `update-dashboard.bat` 실행
   ```bash
   cd ..
   ..\update-dashboard.bat
   ```

4. 웹 브라우저에서 대시보드 새로고침

## 주의사항

- CSV 파일은 `.gitignore`에 의해 Git에 커밋되지 않습니다
- 거래 데이터는 로컬에만 저장되며, 외부로 전송되지 않습니다
- 한 번 처리된 파일은 자동으로 건너뜁니다 (중복 방지)

## 지원하는 파일 형식

### BingX Perpetual Futures
- 파일명 패턴: `Perp_Futures_Order_History_*.csv`
- 필수 컬럼:
  - Time(UTC+8)
  - Pair
  - Type
  - Leverage
  - DealPrice
  - Quantity
  - Fee
  - Realized PNL
