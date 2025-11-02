# Trading Journal - HTML 기반 클라이언트 사이드 전환 TODO

## 목표
백엔드 서버 없이 브라우저에서 직접 CSV 파일을 파싱하고 대시보드를 표시하는 순수 클라이언트 사이드 애플리케이션으로 전환

## 현재 상태
- ✅ Next.js 16 + React 19 프론트엔드
- ✅ FastAPI 백엔드 (로컬에서 작동 중)
- ✅ SQLite 데이터베이스
- ❌ Vercel 배포 시 백엔드 없어서 작동 안 함

## 변경 후 구조
- ✅ Next.js 프론트엔드만 사용
- ✅ 브라우저에서 CSV 파일 직접 파싱
- ✅ LocalStorage 또는 IndexedDB에 데이터 저장
- ✅ Vercel에 배포 시 즉시 작동

---

## Phase 1: 라이브러리 설치 및 설정

### 1.1 CSV 파싱 라이브러리 설치
```bash
npm install papaparse
npm install --save-dev @types/papaparse
```

**설명:** PapaParse는 브라우저에서 CSV 파일을 파싱하는 가장 인기 있는 라이브러리

### 1.2 Excel 파일 지원 추가 (선택사항)
```bash
npm install xlsx
npm install --save-dev @types/xlsx
```

**설명:** BingX CSV가 실제로 Excel 형식일 수 있으므로 XLSX 라이브러리 추가

---

## Phase 2: 유틸리티 함수 작성

### 2.1 CSV 파싱 유틸리티 생성
**파일:** `lib/utils/csv-parser.ts`

**기능:**
- BingX CSV 파일 읽기
- Trade 데이터 파싱
- Position 계산 (OPEN/CLOSE 매칭)
- 에러 핸들링

**주요 함수:**
```typescript
- parseBingXCSV(file: File): Promise<Trade[]>
- calculatePositions(trades: Trade[]): Position[]
- validateCSVFormat(data: any[]): boolean
```

### 2.2 통계 계산 유틸리티 생성
**파일:** `lib/utils/statistics.ts`

**기능:**
- Stats 계산 (총 포지션, 승률, P&L 등)
- ChartData 생성 (equity curve, daily P&L 등)
- 날짜별 집계

**주요 함수:**
```typescript
- calculateStats(positions: Position[]): Stats
- generateChartData(positions: Position[]): ChartData
- calculateEquityCurve(positions: Position[]): EquityCurvePoint[]
- calculateDailyPnL(positions: Position[]): DailyPnLPoint[]
```

### 2.3 로컬 스토리지 유틸리티 생성
**파일:** `lib/utils/storage.ts`

**기능:**
- 거래 데이터 저장/불러오기
- 데이터 초기화
- 스토리지 용량 체크

**주요 함수:**
```typescript
- savePositions(positions: Position[]): void
- loadPositions(): Position[] | null
- clearAllData(): void
- getStorageSize(): number
```

---

## Phase 3: 컴포넌트 수정

### 3.1 FileUpload 컴포넌트 수정
**파일:** `lib/components/file-upload.tsx`

**변경사항:**
- ❌ 삭제: Axios API 호출
- ✅ 추가: 브라우저에서 파일 읽기
- ✅ 추가: PapaParse로 CSV 파싱
- ✅ 추가: 파싱 결과 콜백

**새로운 로직:**
```typescript
const handleFileUpload = async (file: File) => {
  // 1. 파일 읽기
  // 2. PapaParse로 파싱
  // 3. Trade 객체 변환
  // 4. Position 계산
  // 5. LocalStorage 저장
  // 6. 부모 컴포넌트에 알림
}
```

### 3.2 Dashboard 페이지 수정
**파일:** `app/page.tsx`

**변경사항:**
- ❌ 삭제: fetch API 호출
- ❌ 삭제: API_URL 환경변수
- ✅ 추가: LocalStorage에서 데이터 읽기
- ✅ 추가: 클라이언트 사이드 계산

**새로운 로직:**
```typescript
useEffect(() => {
  // 1. LocalStorage에서 positions 불러오기
  // 2. Stats 계산
  // 3. ChartData 생성
  // 4. State 업데이트
}, []);

const handleUploadSuccess = (positions: Position[]) => {
  // 1. Stats 재계산
  // 2. ChartData 재생성
  // 3. UI 업데이트
}
```

---

## Phase 4: 백엔드 코드 제거 (선택사항)

### 4.1 백엔드 폴더 삭제 또는 무시
```bash
# backend 폴더를 삭제하거나 .gitignore에 추가
echo "backend/" >> .gitignore
```

### 4.2 환경변수 파일 삭제
```bash
rm .env.local
```

### 4.3 Vercel 환경변수 제거
```bash
vercel env rm NEXT_PUBLIC_API_URL
```

---

## Phase 5: 테스트 및 검증

### 5.1 로컬 테스트
- [ ] CSV 파일 업로드 테스트
- [ ] Position 계산 정확성 검증
- [ ] Stats 계산 검증
- [ ] 차트 데이터 표시 확인
- [ ] LocalStorage 저장/불러오기 확인

### 5.2 에러 케이스 테스트
- [ ] 잘못된 CSV 형식
- [ ] 빈 CSV 파일
- [ ] 너무 큰 CSV 파일 (스토리지 제한)
- [ ] 중복 데이터 업로드

### 5.3 UI/UX 개선
- [ ] 업로드 진행 상태 표시
- [ ] 에러 메시지 표시
- [ ] 데이터 초기화 버튼 추가
- [ ] 파일 형식 안내

---

## Phase 6: Vercel 재배포

### 6.1 코드 커밋
```bash
git add .
git commit -m "Convert to client-side CSV parsing - no backend needed"
git push origin master
```

### 6.2 Vercel 자동 배포 확인
- Vercel이 자동으로 새 커밋 감지
- 빌드 성공 확인
- 배포된 URL에서 테스트

### 6.3 프로덕션 테스트
- [ ] Vercel URL에서 CSV 업로드
- [ ] 대시보드 표시 확인
- [ ] 새로고침 후 데이터 유지 확인

---

## 추가 개선사항 (선택사항)

### 7.1 데이터 내보내기 기능
- [ ] JSON 형식으로 데이터 다운로드
- [ ] CSV 형식으로 결과 내보내기

### 7.2 데이터 필터링
- [ ] 날짜 범위 필터
- [ ] 페어별 필터
- [ ] Long/Short 필터

### 7.3 다크모드 지원
- [ ] 다크모드 토글 버튼
- [ ] 차트 색상 테마 변경

### 7.4 모바일 최적화
- [ ] 반응형 디자인 개선
- [ ] 터치 제스처 지원

---

## 예상 작업 시간
- Phase 1-2: 1-2시간 (라이브러리 설치 및 유틸리티 작성)
- Phase 3: 2-3시간 (컴포넌트 수정)
- Phase 4: 30분 (백엔드 제거)
- Phase 5: 1-2시간 (테스트)
- Phase 6: 30분 (배포)

**총 예상 시간: 5-8시간**

---

## 참고 자료

### PapaParse 문서
- https://www.papaparse.com/docs

### LocalStorage API
- https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

### Next.js 클라이언트 컴포넌트
- https://nextjs.org/docs/app/building-your-application/rendering/client-components

---

## 주의사항

### 데이터 보안
- LocalStorage는 암호화되지 않음
- 민감한 데이터는 저장하지 않기
- 필요시 IndexedDB + 암호화 고려

### 브라우저 제한
- LocalStorage 용량: 약 5-10MB
- 큰 CSV 파일은 메모리 문제 발생 가능
- 필요시 청크 단위 처리 고려

### 데이터 백업
- LocalStorage 데이터는 브라우저 캐시 삭제 시 사라짐
- 중요한 데이터는 정기적으로 내보내기 권장

---

## 문제 발생 시 롤백 계획

1. 현재 상태 브랜치 생성
```bash
git checkout -b backup-with-backend
git push origin backup-with-backend
```

2. 문제 발생 시 롤백
```bash
git checkout master
git reset --hard backup-with-backend
git push -f origin master
```

---

**작성일:** 2025-11-03
**작성자:** Claude Code
**프로젝트:** Trading Journal - BingX
