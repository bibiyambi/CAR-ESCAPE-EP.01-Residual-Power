# 공개 제출 전 점검 기록

검토일: 2026-11-15. 로컬 작업 파일을 기준으로 검토했으며 커밋·푸시·저장소 공개 전환·Release 게시는 수행하지 않았다.

## 결론과 검토 범위

현재 공개 후보와 생성된 development APK에서 **실제 인증키·토큰·서명 개인키는 발견되지 않았다**. 파일 이름만 보고 판단하지 않고 Gradle 설정, Android 소스·Manifest, 보조 스크립트, 웹 프로토타입, 기획 문서의 XML·메타데이터, Git 이력과 APK 압축 내부를 검사했다. 일반 비밀값 형식 탐지는 휴리스틱이므로 임의 형식의 모든 비밀값이 없음을 보증하지는 않는다.

이 환경에는 `private/pleos.properties`가 없어, 기존 검사 스크립트의 로컬 자격정보 값 대조만으로는 검토 근거가 부족했다. 스크립트에 일반적인 키·토큰 형식과 공개 금지 경로 검사를 추가했고, 로컬 자격정보가 없으면 값 대조를 건너뛰었다고 명시하도록 수정했다. 키 값은 오류 출력에 표시하지 않는다.

## 파일별 공개 판단

| 파일 / 종류 | 판단 | 확인 내용 / 처리 |
|---|---|---|
| [gradle.properties](../gradle.properties) | 공개 가능 | JVM 메모리·Android/Kotlin 옵션과 `gameSource=game-assets`만 있다. 비밀번호, 사용자명, SDK 절대 경로, 인증키 없음. 향후 저장소 인증정보는 이 파일에 넣지 않는다. |
| [settings.gradle.kts](../settings.gradle.kts) | 공개 가능 | Google/Maven Central/Pleos 저장소 주소와 도구 체인 resolver 설정. URL에 인증정보가 없고 `credentials` 블록도 없음. |
| [build.gradle.kts](../build.gradle.kts), [앱 빌드 설정](../app/build.gradle.kts), [core 빌드 설정](../core/build.gradle.kts) | 공개 가능 | 플러그인·SDK 의존성 버전, 빌드 flavor, 패키지 ID는 비밀정보가 아니다. BuildConfig에는 모의 정차 여부만 선언하며 자격정보·release 서명 비밀번호 설정 없음. |
| [gradle/](../gradle/), [gradlew](../gradlew), [gradlew.bat](../gradlew.bat) | 공개 필요 | 빌드 재현에 필요한 Wrapper와 공용 JDK 다운로드 설정이다. `gradle-wrapper.jar`는 SDK 바이너리 제외 규칙의 명시적 예외로 유지한다. Foojay URL의 배포물 ID는 인증 토큰이 아니다. |
| `local.properties` | 공개 제외 | 개인 Android SDK 절대 경로(`sdk.dir`)만 포함한다. 현재 Git 미추적·ignore 적용 확인. 각 개발자 환경에서 생성한다. |
| `.gradle/`, `.kotlin/`, `.idea/`, `**/build/`, `.local/` | 공개 제외 | 로컬 캐시·IDE 설정·빌드 산출물·이식용 로컬 자산. ignore 적용 확인. Android SDK 설치 폴더와 AVD는 저장소 밖에 있다. |
| `private/`, `sdk/`, SDK AAR/JAR·비공개 SDK 정보 문서 | 공개 제외 | 현재 공개 후보에 없음. 의존성 좌표로 SDK를 받는 설정은 유지하며 SDK 원본 배포물·제공받은 비공개 문서를 추가하지 않는다. |
| `.env*`, 서명키·개인키, 서명/비밀값 properties | 공개 제외 | 현재 공개 후보에 없음. `.jks`, `.keystore`, `.p12`, `.pfx`, `.pem`, `.key`, `keystore.properties`, `signing.properties`, `secrets.properties`, `credentials.properties` 등을 제외한다. |
| APK/AAB/APKS, 로그·메모리 덤프·캡처 | 소스 커밋 제외 | 전체 경로에 적용되는 APK 제외 규칙과 로그·덤프 제외 규칙을 보강했다. `.DS_Store`도 전역 Git 설정에 의존하지 않도록 저장소에서 제외한다. 배포할 APK는 별도로 검증해 Release에 첨부한다. |
| [Android 소스](../app/src/), [core 소스](../core/src/) | 공개 가능 | Pleos typed 초기화·해제 경계와 개발판 모의 입력 구현이며 자격정보 하드코딩·임의 인증 요청 없음. Manifest에 비밀값 없음. |
| [game-assets/](../game-assets/) | 현재 비밀정보 발견 없음 | 이미지·음향·폰트·단서 자산. NanumGothic OFL 문서를 함께 유지한다. 공개 범위·공모전의 외부 자산/AI 활용 고지 조건은 별도 제출 규정에 맞춰야 한다. |
| 웹 프로토타입·기획 문서 | 현재 비밀정보 발견 없음 | 문서 XML/메타데이터에도 자격정보가 발견되지 않았다. 개발 계획의 개인 절대 링크는 상대 링크로 바꾸고 생성 이력의 클라우드 작업 경로는 파일명과 프롬프트를 보존하면서 정리했다. |
| [Mac 이관 문서](MAC_TRANSFER.md) | 정리 후 공개 가능 | 개인 계정명이 들어간 절대 경로를 홈 기준 예시로 변경하고 현행 빌드 환경을 반영했다. |

SDK의 실제 재배포 허용 범위는 공급자가 제공하는 약관에 따른다. 이번 검토는 비공개 SDK 자료나 바이너리를 소스에 포함하지 않았음을 확인한 것이며, 제공받지 않은 약관의 재배포 권한을 판단한 것은 아니다.

## Git 이력

검토 시점의 일반 브랜치(`main`, `dev`)와 origin 추적 브랜치에는 최초 README 커밋만 있었다. 새 Android 프로젝트는 아직 미추적 상태였다. 로컬 에이전트 체크포인트를 포함해 참조 가능한 이력에도 일반적인 키·토큰·개인키 형식이 발견되지 않았다.

로컬 에이전트 체크포인트에는 정리 전 개인 경로가 남아 있다. 해당 체크포인트는 일반 브랜치 이력이 아니며 통상적인 브랜치 push 대상에 포함되지 않는다. 작업 파일 수정으로 기존 이력이 지워지는 것은 아니고, 이력 재작성은 수행하지 않았다.

`.gitignore`는 이미 추적된 파일이나 과거 커밋의 내용을 제거하지 않는다. 향후 실제 비밀값을 커밋했다면 키 폐기·재발급과 이력 정리가 별도로 필요하다.

## 실행한 검증

```sh
./gradlew :core:test :app:assembleDevelopmentDebug
python3 tools/check_private_material.py --apk app/build/outputs/apk/development/debug/app-development-debug.apk
git ls-files --cached --others --exclude-standard
git status --short --ignored
```

- 현재 Mac 환경에서 단위 테스트 **20개 통과**, development debug APK 빌드 성공.
- 공개 후보와 APK의 일반 비밀값 형식·공개 금지 경로 검사 통과. APK assets에 HTML/JavaScript 런타임이나 SDK 정보 문서가 없는지도 확인했다.
- 임시 Git 저장소에서 검사 도구의 정상 입력, 토큰 검출·값 비노출, 강제 추적된 로컬 설정 검출, 미추적 로컬 설정 제외, 로컬 자격정보 일치 검출, 압축 문서 내부 검사, Wrapper 예외, APK 내부 검출 등 **8개 시나리오 통과**.
- AVD 설정 및 연결 장치 조회에서 **Pleos Connect v2.1.0 / Android 14(API 34) / 2560×1440 / 160 dpi** 확인. 앱 UI나 차량 신호 연동 시험을 수행한 결과는 아니다.

생성된 development APK는 67,155,846 bytes이며 SHA-256은 다음과 같다. 다시 빌드하면 달라질 수 있다.

```text
173f026bdd98329524c672761d8f768d0ff4ee355f5a89a14b8ec6b2d31b9491
```

검사 스크립트는 현재 작업 파일과 선택한 APK를 검사하며 Git 이력은 자동 검사하지 않는다. 이번 이력 검사는 별도로 수행했다. 실제 APK 서명 인증서의 공개 정보와 제3자 라이브러리의 일반 리소스는 개인 서명키와 다르다.

## 공모전 제출 전에 남은 항목

- Pleos 연동·앱 UI 완주 검증과 Android 2·3막 이식은 미완료다. 공개 가능 여부와 앱 완성 여부를 구분한다.
- 현재 APK는 개발용 debug 빌드다. release 서명과 최종 제출 APK 준비가 남아 있다.
- README에는 빌드 산출물 위치를 기재했다. 심사자가 받을 수 있는 검증된 APK를 GitHub Release에 첨부한 뒤 README에 해당 릴리스 고정 링크를 추가해야 한다. 현재 배포 완료를 주장하지 않는다.
