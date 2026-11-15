# 통합 구현과 호스트 연결 계약

## 퍼즐와 완료 조건

| P | 화면 | 입력 또는 조작 | 입력 이후 판단 / 보상 |
|---|---|---|---|
| 01 | S01 | V01 정지→작동 | 프레임 04와 카메라를 직접 조사. 선택 단서 |
| 02 | S03 | 게임 외투→가방 끈→가방 이동 | 내용물 조사: 사진·안내서 A·카드 |
| 03 | S02 | 서랍·카드+리더기·안내서 A+B | USB 연결·인수 기록·맞춘 안내서 |
| 04 | S04A | 게임 녹음 L/R ±80 이상으로 각각 끝까지 청취 | “흔적은 지워도 남아.” / “끝까지 밀어. 그 아래.” 선택 단서 |
| 05 | S02/S04B | V02 낮음 안정 수신 | 게임 미러를 14±4로 맞춰 유리 문장·레일 그림 기록 |
| 06 | S05/S02 | 게임 시트 100%·도구·접기 표시 | 안내서 왼쪽→아래 접기. 도구는 미리 찾아도 수용 |
| 07 | S06 | 삼각 도구·반시계90→시계180·게임 선루프 | 1막 완료, 2막으로 계속 |
| 08 | S07 | 단말기 활성화 후 V01 작동→정지 | CCTV 장면 05→04 정렬. 진단 스트립 |
| 09 | S08 | V02 낮음→중간 | 원본 M05 02:05와 수정 M05 02:18 연결. 원본 장부·L/R 조각 |
| 10 | S09 | 조각 L/R 원본 슬롯 배치·두 채널 확인 | 명단 송신→회수함 조사. 자막만으로도 해독 가능 |
| 11 | S10 | 사진 A/B/C·원본 화물 표식 | A=M01 B=M03 C=M04, 윤서 수정 이력 첨부→송신→회수함 키·토큰 |
| 12 | S11 | 게임 토큰 삽입 후 새 V01 정지→작동→정지 | 가운데 연결 잠금쇠 선택 |
| 13 | S12 | V02 중간→낮음 | 두 회로의 공통 삼각 접점. 프레임 해제·출구 도면 |
| 14 | S13 | V01 정지→작동→정지→작동→정지 | 두 기록 층과 개방 도면이 겹치는 경로 C. 출구 승인 |
| 15 | S14 | 게임 스마트키·승인 토큰·시동 버튼 | 명단·프레임·출구·키 4개 조건 + 슬롯/토큰 확인. 탈출 성공 |

안정 수신은 제안값 700ms, V00 신선도는 제안값 2000ms입니다. 모두 플레이테스트와 차량 검증 후 조정해야 합니다. 연속 입력 제한 시간은 없습니다. 실제 와이퍼 왕복 횟수나 AUTO를 해석하지 않습니다.

## 입력 모드와 정차

`InputSession`이 SIMULATION/VEHICLE의 한 출처만 받습니다. 단말기를 활성화할 때 `puzzleId`, `armed.at`, 단계, 후보 상태를 새로 만듭니다. 모드 변경 때 `epoch`를 증가시키고 미완료 단계·후보·이전 기준을 버립니다. 새 소스·새 epoch·새 시각·현재 단계가 맞는 패킷만 받습니다. 중복 상태는 진행하지 않고 잘못된 순서는 현재 시퀀스만 초기화합니다. 완료 후에도 별도 추리 조작이 필요합니다.

기본 `DEVELOPMENT` 빌드는 모의 정차임을 화면과 시작 화면에 표시합니다. 실제 앱은 브라우저가 아닌 검증된 네이티브 호스트에서 아래 읽기 전용 경계를 연결해야 합니다. 엔진과 UI에는 차량 쓰기 메서드가 없습니다. HTML은 실차 연결이 완료된 제품이 아닙니다.

### 호스트 호출

`window.residualGame.hostReadOnly`:

1. `configure(profile)`에 실차 확인이 끝난 프로필을 전달합니다.
2. `activateVehicleBuild()`로 개발 모의 정차를 제거합니다. 이 순간 실행은 차단됩니다.
3. `receiveSafety(packet)`에 신선한 실제 V00 허용 판정을 전달합니다. 안전해져도 플레이어의 재개 버튼이 필요합니다.
4. 플레이어가 설정에서 OFF를 선택하면 전제 조건을 검사합니다. 미충족이면 ON을 유지합니다.
5. 실제 상태 변경을 `receiveRaw(signalKey, rawValue, meta)`로 전달합니다. 와이퍼는 `wiper`, 풍량은 `fan`을 사용합니다.

프로필은 `{id, verified:true, connected:true, permission:'GRANTED', wiper:{off:[검증된원시값],active:[검증된원시값]},fan:{low:[검증된원시값],mid:[검증된원시값]}}` 형식입니다. 이 객체 자체는 인증이나 SDK 검증의 대체물이 아닙니다. `verified`는 차량/SDK/권한 조합의 실제 검증 기록이 있는 호스트만 설정해야 합니다. 원시값을 이 문서에서 임의로 정하지 않았습니다. 두 풍량 배열은 비어 있거나 겹치면 안 됩니다. AUTO는 작동으로 매핑할 수 없습니다.

V00 패킷: `{parked:true|false, quality:'VALID'|'UNKNOWN',timestamp:epoch밀리초,sourceMode:'VEHICLE'}`. 실제 속도/주차 판정 조합은 플랫폼 담당자가 정의해야 합니다. 기어 P만으로 모든 차종을 보장하지 않습니다. 네이티브 호스트와 JS 시각 기준은 epoch 밀리초로 맞춰야 합니다.

이벤트 메타: `{sourceMode:'VEHICLE',sessionEpoch,timestamp,quality:'VALID',puzzleId,stepIndex,capabilityProfileId}`. 현재 입력 컨텍스트는 엔진의 `input.epoch`, `input.armed?.id`, `input.step`입니다. 실제 호스트는 활성 단말 컨텍스트를 받아 이후 이벤트에만 붙여야 합니다. 이전 이벤트를 새 시각으로 다시 포장하면 안 됩니다. 원시 신호의 품질이 불명일 때는 VALID로 전달하지 말고 입력을 중단해야 합니다.

`setHostState({visible,obscured,insets})`는 가용 영역·화면 가림 정보를 전달합니다. V00 불명/만료, 연결 끊김, 화면 가림에서 입력과 음향을 중지하고 저장합니다. 정차 허용은 저장에서 복원하지 않습니다. 주행/정차 이벤트 수신 주기와 실제 네이티브 포그라운드 정책은 별도 실차 검증 대상입니다.

## 저장

`residual-power-save-v2`와 백업을 사용합니다. schemaVersion, chapter, currentScreen, screenControlAssist/mode, inventory, clues/observedClues, completedPuzzles, storyFlags/puzzleFlags를 저장합니다. 읽기 전용 상태나 미완료 입력은 저장하지 않습니다. 이전 v1 키는 읽기만 하고 삭제하지 않습니다. 완성한 1막·아이템·수첩은 옮기며, 미완료 가방 끈과 새 풍량 판독은 다시 확인합니다. 손상된 기록은 자동 덮어쓰지 않습니다.

## 남은 네이티브 작업

Pleos SDK 바인딩·권한 요청·차종별 원시값·구독 및 타임스탬프 신뢰성·V00 판정은 연결 전입니다. 차종별 검증 로그 없이 OFF를 출시 기능으로 표시하지 마세요. 공식 문서는 도메인과 화면 설계의 참고 자료이며 특정 차량의 읽기 지원을 보증하지 않습니다.

- https://document.pleos.ai/docs/connect/guide/docs-design/getting-started/layout
- https://document.pleos.ai/en/docs/pleos-only/connect-sdk-pleos/Vehicle/intro
- https://github.com/Pleos-Playground/pleos-sample-vehicle-app

## v2.1 입력 세션 보완

`InputSession.suspend(now, resetSequence)`는 미완료 안정화 후보를 버리고 epoch를 바꿔 일시정지 전 이벤트를 차단합니다. 일반 메뉴 정지는 이미 확인한 순서 단계를 유지하고, 정차 불명은 입력 순서까지 초기화합니다. `resume(now)`는 신선한 V00를 요구하며 새 활성 시각 이전 이벤트는 받지 않습니다. 장면 변경은 `disarm()`으로 이전 단말을 해제합니다.

`receiveRaw`는 VEHICLE 출처를 명시한 메타데이터만 전달하며, AUTO 또는 매핑되지 않은 값도 같은 세션의 불명 상태로 전달해 진행 중인 유지 판정을 취소합니다. 서로 다른 단말·순서·epoch의 불명 패킷은 현재 후보를 취소하지 않습니다. 권한·프로필이 유지 시간 도중 바뀌면 완료 시점에도 재확인합니다.

호스트 호출 전 `hostReadOnly.getContext()`를 읽어 현재 sessionEpoch, puzzleId, stepIndex, capabilityProfileId를 얻습니다. 실제 SDK 접속과 실차 검증이 완료된 것은 아닙니다.
