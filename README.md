# pilot-back

협업 템플릿 검증용 팀 작업 보드의 backend 저장소입니다.

- Root: https://github.com/human-agent-bootstrap/pilot-coordination
- 실습 안내: https://github.com/human-agent-bootstrap/pilot-coordination/blob/main/PILOT.md
- 예정 스택: FastAPI + SQLite
- 첫 Change: 작업 등록·조회
- 다음 Change: 작업 완료 처리

## 현재 상태

제품 코드가 없는 최초 기준 저장소입니다. Root에서 계획·계약·검증 명령을 작성하고, CI와 내용을 사람이 확인해 계획 PR을 병합한 뒤 작업 지시서를 발급합니다. 작성자 본인이 확인·병합할 수 있고 다른 리뷰어 계정이나 파일 소유자 승인은 필요하지 않습니다.

첫 구현은 최소 프로젝트, `.gitignore`, lockfile, 테스트와 자체 CI를 포함합니다. 현재 이 저장소에는 실행·테스트·빌드 명령이 아직 없습니다. Agent는 로컬 구현·검증·commit·handoff를 수행하고, push·PR·병합은 사람의 작업 또는 명시적 승인에 따릅니다. 승인된 Root 계약만 사용하고 실제 개인정보나 운영 데이터는 사용하지 않습니다.
