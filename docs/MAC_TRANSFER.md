# Mac 로컬 폴더로 옮기기

클라우드와 Mac은 서로 다른 컴퓨터다. 다운로드 ZIP을 Mac에서 풀고 가져오기 스크립트를 실행해야 Mac 폴더에 반영된다. 이 과정은 Git 커밋·스테이징·푸시를 하지 않는다.

내보낸 ZIP의 `Import-to-Mac.command`를 실행하면 기본 목적지는 다음과 같다.

`~/Documents/GitHub/CAR-ESCAPE-EP.01-Residual-Power`

스크립트는 먼저 포함 파일의 SHA-256을 검증한다. 기존 파일과 충돌하면 기존 파일을 저장소 밖의 날짜별 백업 폴더에 보존한 뒤 복사한다. 기존 `.gitignore`는 보존하면서 새 제외 규칙을 덧붙인다. `.git` 및 기존 SDK 자격 정보·서명키는 건드리지 않는다.

ZIP에는 소스·검사·문서·Gradle Wrapper와 필요한 게임 이미지/음향의 로컬 복사본이 들어 있다. `.local/native-assets/`는 Git에서 제외된다. SDK 바이너리·SDK 정보 문서·자격 정보·서명키·클라우드용 `local.properties`·빌드 캐시는 포함하지 않는다. 개발 APK는 별도 파일이다.

복사 후 Android Studio에서 목적지 폴더를 연다. 현재 저장소는 Gradle 데몬용 JDK 21(JetBrains), Kotlin/JVM 도구 체인용 JDK 17, Android SDK Platform 37과 Build Tools 36.0.0을 사용한다. 게임 자산은 저장소의 `game-assets/`를 기본으로 사용한다. 다음 명령으로 검증한다.

```sh
./gradlew :core:test :app:assembleDevelopmentDebug
```

SDK 연동과 UI 실행 검증이 아직 완료되지 않았다는 상태는 [개발 기록](NATIVE_DEVELOPMENT.md)을 따른다.
