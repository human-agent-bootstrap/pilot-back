# pilot-back

협업 템플릿 검증용 팀 작업 보드의 backend 저장소입니다.

- Root: https://github.com/human-agent-bootstrap/pilot-coordination
- 실습 안내: https://github.com/human-agent-bootstrap/pilot-coordination/blob/main/PILOT.md
- 예정 스택: FastAPI + SQLite
- 첫 Change: 작업 등록·조회 API와 SQLite 저장
- 다음 Change: 작업 완료 처리 API

## 현재 상태

최초 기준 commit을 제공하는 실습용 저장소입니다. 제품 코드, 테스트, 실행 명령은 아직 구현되지 않았습니다.

Root에서 계획과 API 계약을 작성하고 독립 리뷰를 거쳐 병합한 뒤, 발급받은 작업 지시서의 정확한 base SHA와 전용 workspace에서 구현을 시작합니다. 첫 구현 작업은 최소 프로젝트 구조, `.gitignore`, lockfile, 테스트와 서비스 CI를 포함합니다.

Root에서 `python -m pytest`, `python -m ruff check .`를 첫 구현 작업의 요구사항으로 승인하세요. 가상환경 및 의존성 설치 방법도 계획에 명시해야 합니다. 지금 이 저장소에서 실행할 수 있는 명령이라는 뜻은 아닙니다.

Agent는 로컬 구현·검증·commit·handoff까지만 수행합니다. Push, PR, 승인, 병합은 사람이 담당합니다. 응답 객체, 상태 코드, 입력 오류, 브라우저 origin CORS를 승인된 Root 계약에 맞게 구현하세요. 실제 개인정보나 운영 데이터는 사용하지 않습니다.
