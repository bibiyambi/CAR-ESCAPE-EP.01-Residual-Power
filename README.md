# CAR-ESCAPE — EP.01: Residual Power

**차량 밀실에 남은 단서를 조사하고 아이템과 장치 입력을 조합해 탈출하는 미스터리 퍼즐 게임입니다.**

## 실행 방법

1. Android Studio에서 저장소 루트를 엽니다.
2. SDK Manager에서 **Android SDK Platform 37(API 37 / Android 17)**, **Build Tools 36.0.0**, **Platform-Tools**를 설치합니다.
3. Gradle JVM을 **JDK 21(JetBrains)**로 설정하고, Kotlin/JVM 도구 체인용 **JDK 17**도 준비합니다. Gradle은 [데몬 설정](gradle/gradle-daemon-jvm.properties)과 Foojay resolver를 통해 필요한 JDK를 내려받을 수 있으므로 최초 빌드에는 네트워크 접근이 필요합니다.
4. Android Studio가 생성하는 `local.properties`에 본인 환경의 Android SDK 경로(`sdk.dir`)가 설정되어 있는지 확인합니다. 이 파일은 Git에 포함하지 않습니다.
5. 터미널에서 다음을 실행합니다. Windows에서는 `./gradlew` 대신 `gradlew.bat`을 사용합니다. 자산 준비와 검사는 Python 3가 필요합니다.

```sh
./gradlew :core:test :app:assembleDevelopmentDebug
python3 tools/check_private_material.py --apk app/build/outputs/apk/development/debug/app-development-debug.apk
```

게임 이미지·음향·단서 데이터는 저장소에 포함된 [game-assets/](game-assets/)를 사용합니다(`gameSource=game-assets`). 별도 원본 저장소 없이 빌드할 수 있으며, 다른 소스팩을 사용할 때만 `-PgameSource=/absolute/path/to/source-pack`을 지정합니다.

에뮬레이터를 실행한 뒤 개발용 APK를 설치하고 실행합니다. 여러 장치가 연결되어 있다면 `adb -s <serial>`로 대상 장치를 지정합니다.

```sh
adb install -r app/build/outputs/apk/development/debug/app-development-debug.apk
adb shell am start -n io.bibiyambi.residualpower.development/io.bibiyambi.residualpower.GameActivity
```

앱에서 **개발용 가상 정차**를 켠 뒤 **눈을 뜬다**를 누릅니다. 이 빌드는 화면 모의 입력으로 플레이하며 차량 SDK 연결을 요구하지 않습니다. 창 포커스·오디오 포커스 상실 또는 백그라운드 전환 시 게임이 중단되며 직접 재개해야 합니다.

### Pleos 차량 연동 빌드

Android Studio의 Build Variants에서 `pleosDebug`를 선택하거나 다음 명령을 실행합니다.

```sh
./gradlew :app:assemblePleosDebug
```

이 flavor는 `ai.pleos.playground:Vehicle:2.3.2`와 [Pleos Maven 저장소](https://nexus-playground.pleos.ai/repository/maven-releases/) 접근이 필요합니다. SDK 초기화·해제 경계만 연결되어 있고, 실제 정차 근거·권한·capability·차량 입력 매핑 검증 전에는 플레이가 차단됩니다. SDK 버전 **2.3.2**는 아래 에뮬레이터 버전 **2.1.0**과 별개입니다. SDK 배포물과 자격정보는 저장소에 복사하지 않습니다.

## 테스트 환경 및 필요한 설정

| 항목 | 현재 설정 / 확인 환경 |
|---|---|
| 호스트 | macOS 26.6.2, Apple Silicon(aarch64) |
| 앱 버전 | `0.1.0-native` (`versionCode=1`) |
| Gradle / Android Gradle Plugin | 9.6.0 / 9.5.1 |
| Java | Gradle 데몬: JDK 21(JetBrains), Kotlin/JVM 도구 체인 및 앱 바이트코드: Java 17 |
| Android SDK | compileSdk 37, targetSdk 37, minSdk 28 |
| Build Tools | 36.0.0 |
| 기타 도구 | Python 3, Android SDK Platform-Tools(`adb`) |
| 게임 자산 | 저장소의 `game-assets/`, 별도 다운로드 불필요 |
| 개발판 입력 | `developmentDebug`의 **개발용 가상 정차**와 화면 모의 입력 |
| Pleos 연동 | SDK Maven 접근 및 차량 권한·신호 검증 필요 |


## Pleos Connect 에뮬레이터 버전과 화면 규격

| 항목 | 개발 환경에서 확인한 값 |
|---|---|
| Pleos Connect | **v2.1.0** |
| AVD 이름 | `Pleos_Connect_v2.1.0` |
| 시스템 이미지 | Android Automotive, Android 14 / API 34, arm64-v8a |
| 전체 화면 해상도 | **2560 × 1440 px** (가로, 16:9) |
| 화면 밀도 | **160 dpi** (`mdpi`) |
| Android Emulator 도구 버전 | 37.2.13 |

위 수치는 에뮬레이터 전체 디스플레이 기준입니다. 시스템 바나 창 배치에 따라 앱이 사용하는 영역은 달라질 수 있습니다. 빌드용 compileSdk 37과 에뮬레이터 실행 OS의 API 34를 구분합니다.

## APK 파일 위치

```text
/apk/bibiyambi_CAR-ESCAPE_release.apk
```