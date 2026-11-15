# 네이티브 Android 개발 기록

기준일: 2026-11-15 KST. Android 전환 계획 v1.0을 읽은 뒤 사용자의 변경 요청에 따라 WebView 권고안을 Kotlin 네이티브 방식으로 변경했다. 원본 계획·SDK 정보 문서는 source 저장소에 그대로 보존했다.

## Mac 환경 공개 제출 점검 추가 기록

아래 본문은 앞서 클라우드에서 수행한 개발·검증 이력이다. 현재 Mac에서는 Gradle 9.6.0 / AGP 9.5.1, 데몬 JDK 21(JetBrains) / JVM 도구 체인 17, compileSdk·targetSdk 37, Build Tools 36.0.0과 저장소의 `game-assets/`를 사용한다. 2026-11-15 재검사에서 `:core:test` 20개와 `:app:assembleDevelopmentDebug`가 통과했다. 이전 APK 해시·크기는 현재 산출물과 다르며 최신 검사는 [공개 제출 점검 기록](PUBLIC_RELEASE_REVIEW.md)에 있다.

연결된 장치와 AVD 설정에서 Pleos Connect v2.1.0, Android 14(API 34), 2560×1440, 160 dpi를 확인했다. 이 작업에서 앱 UI 완주 또는 Pleos 신호 연동 시험은 수행하지 않았다. 아래 클라우드 403·에뮬레이터 장애 기록은 당시 관찰이며 현재 Mac에서 같은 제약을 재현했다는 뜻이 아니다.

## 구현 구조

- `core`: Android에 의존하지 않는 Kotlin 1막 규칙, 입력 세션, 정차 허용 게이트, JSON 저장 형식. JUnit으로 검증한다.
- `app`: Jetpack Compose 화면, 장면 이미지와 조사 목록, 소지품 선택·조합·도면 접기, 수첩, 게임 시트·거울·수동 소켓, 로컬 WAV 채널 재생과 자막.
- `SaveRepository`: 앱 내부 AtomicFile 저장, SHA-256 손상 감지, 이전 정상본. 손상 시 쓰기를 잠그고 명시적 복구/새 게임 전에 원본을 별도 파일로 보존한다. SHA-256은 손상 감지용이다.
- `InputSession`: monotonic clock, 700ms 안정화, 2000ms 신선도, source·epoch·puzzle·step 확인. 요청 시점의 context를 보존해야 하며 콜백 직전에 새 context로 덧씌우지 않는다.
- `SafetyGate`: 포그라운드·창 포커스·AAOS UX 허용·새 정차 근거가 모두 필요하다. UX 제한이 없다는 사실만으로 정차를 만들어내지 않는다. 저장에는 정차·SDK 연결·권한·미완료 입력을 넣지 않는다.
- `CarSafetyMonitor`: AAOS restriction listener, 서비스 소실과 오래된 연결 세대 콜백 차단. 앱은 distraction optimized로 선언하지 않는다.
- `PlatformVehicle`: flavor별 SDK 경계. development는 SDK 미연결을 명시한다. pleos는 공식 SDK typed 수명주기만 사용하며 실제 읽기 연결은 대기 중이다.

## 첫 이식 범위

1막 S01–S06을 이식했다. 가방/서랍 순서 교환, 중복 아이템 방지, 카드+리더기와 안내서 조합, 도면 접기, 게임 시트와 도구·소켓·선루프 조작을 구현했다. 단서를 먼저 열람하지 않아도 추리한 조작을 받아들인다.

P01 와이퍼 정지→작동은 선택 입력이다. P05 풍량 LOW의 700ms 안정 입력 완료 상태를 영속 보관하며, 최종 탈출은 그 상태와 열린 선루프를 모두 요구한다. 유리 단서 열람 자체를 강제하지 않는다. 패널을 닫거나 장면을 옮기거나 앱이 중단되면 미완료 입력을 버린다.

화면은 장면 아트를 contain으로 표시하고 네이티브 조사 목록으로 접근한다. 원본 SVG의 불규칙 터치 윤곽은 아직 네이티브로 이식하지 않았다. 녹음은 Android Audio Focus와 MediaPlayer로 처리하며, 포커스 손실·패널 닫기·중단 시 재생 및 완료 콜백을 무효화한다. 접근성용 좌우 자막 경로를 제공한다.

## 원본과의 차이

네이티브 저장 형식은 `residual-native-v1`이며 웹 `schemaVersion:2`와 별개다. Chrome/localStorage 기록을 자동으로 이전하지 않는다. 2·3막, 12개 창 프로필 전수 검증, 배경 환경음, 정밀 SVG 조사 영역, 최종 release 서명·제출 APK는 아직 후속 작업이다. 개발판을 3막 완성 앱이나 Pleos 시연 완료로 표시하지 않는다.

## SDK 근거와 외부 제약

참고 공식 샘플: `Pleos-Playground/pleos-sample-vehicle-app`, 확인 커밋 `959981d960ec71144accb27af5ae5d341e72a644`.

사용자 지정 가이드: <https://document.pleos.ai/docs/pleos-only/vehicle-app-developer-guide/intro>

Maven 저장소: <https://nexus-playground.pleos.ai/repository/maven-releases/>

현재 두 Pleos 호스트는 클라우드 프록시에서 403으로 차단된다. 허용 도메인 두 개만 환경 초안에 추가했으며 다른 설정을 변경하거나 환경을 게시하지 않았다. 실행 중인 정책 반영은 아직 확인되지 않았다. 공식 가이드 본문을 읽었다고 주장하지 않으며 로컬 전환 계획과 공식 GitHub 샘플만 확인했다.

`compilePleosDebugKotlin`은 SDK POM 다운로드 단계에서 403으로 실패했다. SDK를 임의 대체하거나 인증·TLS 검증을 끄지 않았다. 클라이언트 자격 정보만으로 Maven 접근 제한이 해결된다고 가정하지 않는다. SDK 정보의 테스트 장치 설정 명령은 연결된 Pleos 장치가 없으므로 실행하지 않았다.

접근이 반영되면 공식 가이드와 2.3.2 실제 타입을 대조하고 V00 의미, 와이퍼 switch getter와 motor state 구분, HVAC 영역·capability 및 LOW/MID를 검증한다. 검증 기록 전에는 `verified`를 설정하거나 가짜 V00를 전달하지 않는다.

## 검증 결과

실제 명령·결과는 마지막 검증 후 아래에 추가한다. 빌드 성공과 에뮬레이터 UI 검증, Pleos 검증을 구분한다.

- `:core:test`: 네이티브 규칙 11개와 입력·안전 검사 9개, 총 20개 통과.
- `:app:assembleDevelopmentDebug`: debug APK 생성 성공.
- `tools/check_private_material.py`: Git 후보와 APK에서 로컬 SDK 자격 정보가 없음을 확인. 최종 APK가 완성된 뒤 다시 검사한다.
- `:app:compilePleosDebugKotlin`: SDK POM 다운로드 프록시 403으로 차단. Kotlin SDK 호출부 컴파일 및 Pleos 실행은 미검증.

- 개발용 APK: `apk/잔류전원_native-development-debug.apk` (Git 제외), 60,965,275 bytes. SHA-256: `0ab02dce80617706a785e0c89560cbefd99cfa2881d9f05f02aa937d27d02995`. 제출용 signed release가 아니다.

- 최종 `:app:lintDevelopmentDebug`: 0 errors, 1 warning (`DataExtractionRules`). Manifest에 allowBackup=false, fullBackupContent=false 및 API 31+ dataExtractionRules가 있으나 lint가 legacy XML resource 지정을 권고한다.
- APK 압축 항목 검사: HTML/JavaScript 런타임 없음. 최종 APK와 Git 후보에 로컬 SDK 자격 정보가 없는지 재검사 통과.
- UI 검증 **미완료**: 이 클라우드에는 `/dev/kvm`이 없어 소프트웨어 에뮬레이션으로 시도했다. API 35 Google APIs 이미지는 첫 부팅 검증 창에서 준비되지 않아 종료했다. API 28 default 이미지는 부팅했으나 System UI ANR, 이어서 Watchdog의 ActivityManagerService lock 대기와 system_server 재시작을 관찰했다. 앱 실행 전에 package/activity Binder가 Broken pipe로 끊겼으며 앱 화면 검사에 도달하지 못했다. 따라서 native 1막 UI 완주, 저장 파일 복구, 음향, 라이프사이클 실제 동작을 통과로 기록하지 않는다. 이는 관찰한 플랫폼 장애이며 앱의 결함 유무 전체를 입증하지 않는다.
- UI 검사 스크립트: `python3 tools/adb_smoke.py --adb /path/to/adb --serial emulator-5554`. **폐기 가능한 AVD** `residual-native` 또는 `residual-native-api28`에서만 실행하며 development 앱 데이터를 초기화한다. 시작 차단, 조합·소켓, P05 전 탈출 거부, 탈출, 프로세스 재시작과 손상 저장 복구를 검사하도록 작성했지만 아직 성공한 실행 기록은 없다.
- 향후 실행 검증은 하드웨어 가속이 있는 Android Studio 장치에서 먼저 수행하고, 네트워크 접근과 SDK 실제 타입 확인 후 Pleos 에뮬레이터로 이어간다. 원본 source 저장소의 변경 없음, staging 없음, 커밋·푸시·환경 게시 없음.
