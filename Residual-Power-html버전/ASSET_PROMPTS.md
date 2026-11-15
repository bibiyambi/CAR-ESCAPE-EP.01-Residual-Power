# 이미지 제작 프롬프트와 사용

3막 확장 에셋은 모두 내장 이미지 생성으로 제작했습니다. 참조 이미지는 기존 `S01.png`(차량 정체성과 재질), `END.png`(시설과 조명)입니다. 새 배경 11개와 투명 아이템 5개를 개별 생성했으며, 하나의 합성 시트에서 잘라 사용하지 않았습니다.

공통 방향: premium hand-painted cinematic realism; graphite-blue electric sedan, cognac stitched leather, satin champagne brass, petrol-teal rainy industrial warehouse, warm amber practical lamps, lifted readable midtones. Wide 16:9 1672×941 background plates. No people/hands/logos/text/numbers/HUD or baked puzzle answers. Screens blank charcoal for exact code overlays.

투명 아이템 추가 조건: one separate centered inventory sprite, genuine transparent background, natural silhouette, no floor, fog, mist, bloom, external halo or drop shadow. Original alpha preserved; separate deterministic contour wrappers and white masks generated for interaction.

`source/v2-art-provenance.json`에는 각 파일의 개별 주제 프롬프트 또는 전체 프롬프트, 참조 역할, 생성 원본 경로가 들어 있습니다. 기존 1막 원본 제작 이력은 `source/act1-*`와 기존 파일에 보존했습니다. 여기의 주제와 공통 방향을 합쳐 후속 스타일 제작 기준으로 쓸 수 있습니다.

| 에셋 | 개별 주제 |
|---|---|
| S07 | 차량 보관 시설 감시실, 3개 모니터, 필름 판독기, 빗물 창 |
| S08 | 진단실 클로즈업, 큰 화면, 필름 리더, 원본 바인더 |
| S09 | 음성 기록실, 릴 테이프, 원본 채널 슬롯 |
| S10 | 송신실, 사진 보드, 송신 단말기, 회수함 |
| S11 | 동일 M-04 운전석 귀환, 앞유리 너머 세 잠금쇠 |
| S12 | 운송 프레임 진단 스테이션, 상하 회로 카드 홈 |
| S13 | 시설 출구 셔터와 경로 승인 단말기 |
| S14 | 동일 차량의 게임 대시보드, 키 슬롯과 시동 버튼 |
| FINAL | 열린 시설 출구와 새벽, 탈출하는 동일 차량 |
| film-05 | 운송 프레임이 완전히 빈 CCTV 스틸 |
| film-04 | 동일 차량이 들어온 프레임의 CCTV 스틸 |
| smartKey | 코냑 가죽과 황동 테두리의 그라파이트 스마트키 |
| frameToken | 삼각 홈과 세 접점이 있는 청록 프레임 토큰 |
| victimA/B/C | 같은 연구 작업장 조명의 가상 성인 인물 즉석 사진 3개 |
