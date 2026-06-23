"""HTML body fragments for build_site.py"""

HOME_KEEPER_BODY = """
<div class="prod-hero reveal prod-hero--pink">
<div class="prod-hero__img"><img src="../assets/images/products/home-keeper.png" alt="마이안심이"></div>
<div class="prod-hero__info"><span class="model">My Ansim-i · 실용신안 KR 20-0498161</span><h2>마이안심이</h2>
<p><strong>감시가 아닌 위안, 불안이 아닌 평온.</strong> 1인 여성 가구의 평온한 일상을 지키는 라이프스타일 안심 오브제입니다. 위압적인 CCTV·비상벨이 아닌, 조명·디퓨저처럼 집안에 자연스럽게 스며드는 홈 안전 솔루션입니다.</p>
<a href="../support/inquiry.html" class="btn btn--pink">도입 문의</a></div></div>

<div class="content-block reveal"><h2>왜 마이안심이인가</h2>
<div class="compare-row">
<div class="compare-box compare-box--old"><h4>기존 보안 기기</h4><ul>
<li>감시·경고 중심 — 심리적 압박</li><li>투박한 디자인, 인테리어 훼손</li><li>클라우드 전송 — 사생활 우려</li></ul></div>
<div class="compare-box compare-box--new"><h4>마이안심이</h4><ul>
<li>위안·평온 — 일상의 오브제</li><li>감성 디자인, 인테리어 친화</li><li>On-Device AI — 데이터 외부 유출 없음</li></ul></div>
</div></div>

<div class="content-block reveal" style="text-align:center">
<img src="../assets/images/products/app-mockup.png" alt="마이안심이 앱" class="ansimi-app-img" loading="lazy"></div>

<div class="content-block reveal"><h2>핵심 기술</h2>
<div class="feature-grid">
<div class="feature-box"><h4>99% 인식률</h4><p>삼성 에스원 협력 10여 년 · 3,000대+ 현장 검증</p></div>
<div class="feature-box"><h4>On-Device AI</h4><p>0.1초 비명 인식 · 클라우드 전송 없음</p></div>
<div class="feature-box"><h4>독립 설치형</h4><p>홈네트워크·월패드 불필요 · 기축 원룸·다세대 OK</p></div>
</div></div>

<div class="content-block reveal"><h2>3단계 보호 시스템</h2>
<div class="flow">
<div class="flow__step"><div class="num">1</div><h4>감지</h4><p>Mic×2 + 자석감지기<br>(창문·현관)</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">2</div><h4>AI 판단</h4><p>0.1초 비명 인식<br>민감·보통·둔감 3단계</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">3</div><h4>대응</h4><p>110dB↑ 사이렌<br>SOS · 보호자 호출</p></div></div></div>

<div class="content-block reveal"><h2>실용신안 기반 알고리즘</h2>
<p>택배기사 사칭 범죄를 막는 1인 가구 맞춤형 독립 방범 시스템. 실용신안 <strong>KR 20-0498161</strong> (2024.07 등록)</p>
<div class="feature-grid">
<div class="feature-box"><h4>개인 맞춤 인식</h4><p>사용자별 민감·보통·둔감 3단계 — 오인식 최소화</p></div>
<div class="feature-box"><h4>2중 시간 게이트</h4><p>제1: 20~60초(택배 사칭) · 제2: 30분~(침입)</p></div>
<div class="feature-box"><h4>5분 해제 스위치</h4><p>지인 방문 시 방범 일시 정지</p></div>
</div>
<p style="margin-top:14px">전원 차단 시 배터리 5분 작동 · 외출·재택 모드 지원 · 3G/LTE·BLE/WiFi 통신</p></div>

<div class="content-block reveal"><h2>기술 사양</h2>
<table class="spec-table">
<tr><th>제품명</th><td>마이안심이 (My Ansim-i)</td></tr>
<tr><th>인식 방식</th><td>On-Device AI 비명 인식 (음원 패턴만 분석)</td></tr>
<tr><th>인식률</th><td>99% (10년+ 현장 검증)</td></tr>
<tr><th>마이크</th><td>2 MIC + 무선 자석감지기</td></tr>
<tr><th>알람</th><td>110dB 이상 사이렌 + SOS 비상호출</td></tr>
<tr><th>통신</th><td>3G/LTE · BLE · WiFi</td></tr>
<tr><th>특허</th><td>실용신안 제20-0498161호 (2024.07)</td></tr>
<tr><th>설치</th><td>홈네트워크 불필요 · 독립 설치형</td></tr></table></div>"""

RESTROOM_BODY = """
<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/logo-watchdog.png" alt="워치독 화장실 비명감지기"></div>
<div class="prod-hero__info"><span class="model">워치독 WatchDog · WD 시리즈</span><h2>화장실 비명인식기</h2>
<p>승강기용 워치독과 <strong>동일한 비명인식 기술</strong>입니다. 노출형·매입형(다운라이트형)으로 설치하며, 화장실 내 대화는 녹음·전송되지 않고 비명 발생 시에만 경보합니다. (3G/LTE 모델 제외 별도 이용료 없음)</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>

<div class="content-block reveal"><h2>개발 배경</h2>
<p>공공 화장실은 개인정보보호법상 CCTV 설치가 불가능한 <strong>안전 사각지대</strong>입니다. 몰카·성범죄·폭행 등 여성·아동 대상 강력범죄가 빈번하며, 기존 비상벨은 제압당하거나 당황한 상황에서 버튼을 누르기 어렵습니다.</p>
<p>워치독은 "사람살려", "아악", "강도야" 등 <strong>비명만으로</strong> 위급 상황을 즉시 인지하여 경광등·경고방송을 울리고 112·경비실로 자동 호출합니다.</p></div>

<div class="content-block reveal"><h2>시스템 구성</h2>
<p>화장실 비명감지기(노출형/매입형) → 유선·RF 중계기 또는 3G/LTE → 112 상황실 · 경비실 · 관제센터 · 스마트폰</p>
<div class="content-img"><img src="../assets/images/diagrams/restroom-system-diagram.png" alt="화장실 비명감지기 시스템 구성도"></div></div>

<div class="content-block reveal"><h2>제품 유형</h2>
<div class="feature-grid">
<div class="feature-box"><h4>노출형</h4><p>천정·벽면 표면 부착, 원통형 디자인</p></div>
<div class="feature-box"><h4>매입형</h4><p>다운라이트 홀 규격 매립, 미관 우수</p></div>
<div class="feature-box"><h4>유·무선 연동</h4><p>접점식 유선 / RF 무선 / 3G·LTE 직접 연동</p></div>
</div></div>

<div class="content-block reveal"><h2>동작 흐름</h2><div class="flow">
<div class="flow__step"><div class="num">1</div><h4>비명 대기</h4><p>365일 24시간</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">2</div><h4>AI 판별</h4><p>비명 vs 일상소음</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">3</div><h4>경광등·방송</h4><p>범행 억제</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">4</div><h4>비상호출</h4><p>유선·무선 전파</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">5</div><h4>출동·대응</h4><p>음성통화·긴급출동</p></div></div></div>

<div class="content-block reveal"><h2>제품 특징</h2>
<div class="feature-grid">
<div class="feature-box"><h4>딥러닝 AI</h4><p>일상소음과 비명 정밀 구분</p></div>
<div class="feature-box"><h4>고성능 CPU</h4><p>내장형 CPU로 안정적 실시간 처리</p></div>
<div class="feature-box"><h4>간편 설치</h4><p>매입형 다운라이트 홀 규격 호환</p></div>
<div class="feature-box"><h4>탬퍼 스위치</h4><p>강제 해체 시 즉시 비상통보</p></div>
</div></div>

<div class="content-block reveal"><h2>적용 사례</h2>
<div class="feature-grid">
<div class="feature-box"><h4>부산대학교</h4><p>여자화장실 400개소</p></div>
<div class="feature-box"><h4>여의도 파크원</h4><p>217개소 설치</p></div>
<div class="feature-box"><h4>서울고속터미널</h4><p>주차장·파미에스테이션</p></div>
</div></div>

<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>제품군</th><td>워치독 WatchDog (승강기용과 동일 기술)</td></tr>
<tr><th>적용기술</th><td>딥러닝, 멀티트리거, 실시간 고속인식</td></tr>
<tr><th>인식방식</th><td>음원인식 — 여성·아동 음성 최적화</td></tr>
<tr><th>마이크</th><td>2 MIC (DIGITAL)</td></tr>
<tr><th>인식 단어</th><td>아악, 꺄악, 강도야, 사람살려, 도와주세요</td></tr>
<tr><th>프라이버시</th><td>녹음·감청 없음, 소리 패턴만 분석</td></tr>
<tr><th>설치장소</th><td>화장실, 탈의실, 독서실 등</td></tr></table></div>
<div class="content-block reveal"><p class="note-box">※ <a href="elevator.html">승강기 비명감지기</a>와 동일 워치독 제품군입니다. 세대 현관용은 <a href="light-switch.html">비명인식 일괄소등스위치</a>를 참고하세요.</p></div>"""

LIGHT_SWITCH_BODY = """
<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/control-panel.png" alt="비명인식 일괄소등스위치"></div>
<div class="prod-hero__info"><span class="model">5&quot; FTS · 홈네트워크 연동</span><h2>비명인식 일괄소등스위치</h2>
<p>신축 아파트 세대현관에 설치되는 스마트 터치패널입니다. 일괄소등·엘리베이터 호출 등 생활편의 기능과 함께, 방문자 대면 중 침입 위협 시 비명을 감지하여 HN 월패드·경비실·휴대폰으로 즉시 통보합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>

<div class="content-block reveal"><h2>개발 배경</h2>
<p>기존 아파트 방범은 <strong>외출 시 도난 방지</strong>에 초점이 맞춰져 있습니다. 택배·배달원 위장 침입, 귀가 직후 도어락 래그 범죄 등 재실 중 대면 범죄에 취약합니다.</p>
<p>현관문을 열고 접객하는 순간 범죄가 발생할 수 있으며, SOS 버튼은 범인에게 밀린 상태에서 누르기 어렵습니다. 비명만으로 경비실·월패드에 비상호출하는 것이 핵심입니다.</p></div>

<div class="content-block reveal"><h2>시스템 구성</h2>
<p>세대카메라(방문호출) + 자석감지기(현관문 OPEN) → 5&quot; 일괄소등스위치(비명인식) → HN 월패드 → 단지서버 → 경비실 · 휴대폰 · 인접세대 월패드</p>
<div class="content-img"><img src="../assets/images/diagrams/light-switch-system-diagram.png" alt="일괄소등스위치 시스템 구성도"></div></div>

<div class="content-block reveal"><h2>동작 흐름</h2><div class="flow">
<div class="flow__step"><div class="num">1</div><h4>음향 수집</h4><p>상시 대기</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">2</div><h4>방문자 호출</h4><p>세대카메라 연동</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">3</div><h4>현관문 OPEN</h4><p>자석감지기 작동</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">4</div><h4>비명 인식</h4><p>AI 즉시 판별</p></div><span class="flow__arrow">→</span>
<div class="flow__step"><div class="num">5</div><h4>비상호출</h4><p>경비실·월패드 경보</p></div></div>
<p style="margin-top:14px">평상시 비명인식 비활성 → <strong>외부인 대면 시에만 활성화</strong> (특허 제10-2132316호, 제10-2237852호)</p></div>

<div class="content-block reveal"><h2>제품 특징</h2>
<div class="feature-grid">
<div class="feature-box"><h4>일괄 소등</h4><p>외출 시 세대 조명 일괄 제어</p></div>
<div class="feature-box"><h4>엘리베이터 호출</h4><p>외출 전 승강기 미리 호출</p></div>
<div class="feature-box"><h4>비명인식 보안</h4><p>HN 월패드·경비실 자동 연동</p></div>
<div class="feature-box"><h4>오동작 방지</h4><p>TV·생활소음 원천 차단 특허</p></div>
</div></div>

<div class="content-block reveal"><h2>적용 실적</h2>
<div class="feature-grid">
<div class="feature-box"><h4>진주 아너스</h4><p>840세대 (2024.08)</p></div>
<div class="feature-box"><h4>유승한내들</h4><p>444세대</p></div>
<div class="feature-box"><h4>협력사</h4><p>(주)스필 배선기구 전문</p></div>
</div></div>

<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>디스플레이</th><td>5&quot; Full Touch LCD (정전식)</td></tr>
<tr><th>전원</th><td>AC 220V / 60Hz</td></tr>
<tr><th>통신</th><td>RS-485 (홈넷 연동)</td></tr>
<tr><th>인식 단어</th><td>강도야, 사람살려, 도와주세요</td></tr>
<tr><th>특허</th><td>제10-2132316호, 제10-2237852호</td></tr>
<tr><th>설치위치</th><td>세대현관문 내측</td></tr></table></div>"""

BUSINESS_BODY = """
<div class="content-block reveal"><p>㈜아성보이스는 2015년 설립 이후 AI On-Device 비명 인식 기술을 기반으로 승강기·화장실·세대현관·1인 가구 등 <strong>범죄 사각지대</strong>를 보호하는 언택트 방범 솔루션을 제공합니다.</p></div>

<div class="content-block reveal"><h2>사업 영역</h2>
<div class="biz-grid">
<div class="biz-card neu-card"><div class="biz-card__img"><img src="../assets/images/products/elevator.png" alt=""></div><div class="biz-card__body"><h3>B2B · 승강기 비명감지</h3><p>아파트·오피스텔 엘리베이터 범죄 예방. 삼성 에스원·미쓰비시엘리베이터 협력. WD-600MD 3,000대+ 납품.</p><a href="../products/elevator.html" class="btn btn--blue btn--sm" style="margin-top:12px">자세히</a></div></div>
<div class="biz-card neu-card"><div class="biz-card__img"><img src="../assets/images/products/logo-watchdog.png" alt=""></div><div class="biz-card__body"><h3>B2B · 화장실 비명감지</h3><p>CCTV 설치 불가 공간 보호. 부산대 400개소, 여의도 파크원 217개소 등 공공·민간 납품.</p><a href="../products/restroom.html" class="btn btn--blue btn--sm" style="margin-top:12px">자세히</a></div></div>
<div class="biz-card neu-card"><div class="biz-card__img"><img src="../assets/images/products/control-panel.png" alt=""></div><div class="biz-card__body"><h3>B2B · 일괄소등스위치</h3><p>신축 아파트 HN 연동형. 진주아너스 840세대, (주)스필 협력. 택배 사칭 침입 예방.</p><a href="../products/light-switch.html" class="btn btn--blue btn--sm" style="margin-top:12px">자세히</a></div></div>
<div class="biz-card neu-card"><div class="biz-card__img"><img src="../assets/images/products/pcb-module.png" alt=""></div><div class="biz-card__body"><h3>B2B · 비명인식 모듈</h3><p>지하주차장 비상벨·안심귀갓길 OEM/ODM. 기존 인프라 업그레이드.</p><a href="../products/module.html" class="btn btn--blue btn--sm" style="margin-top:12px">자세히</a></div></div>
<div class="biz-card neu-card"><div class="biz-card__img"><img src="../assets/images/products/home-keeper.png" alt=""></div><div class="biz-card__body"><h3>B2C · 마이안심이</h3><p>1인 여성 가구 라이프스타일 안심 오브제. On-Device AI, 실용신안 KR 20-0498161.</p><a href="../products/home-keeper.html" class="btn btn--pink btn--sm" style="margin-top:12px">자세히</a></div></div>
</div></div>

<div class="content-block reveal"><h2>핵심 역량</h2>
<div class="stats-row" style="margin-top:16px">
<div class="stat-box neu-stat"><div class="stat-box__num">99%</div><div class="stat-box__label">비명 인식률</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">3,000+</div><div class="stat-box__label">누적 납품</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">10년+</div><div class="stat-box__label">현장 검증</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">3건</div><div class="stat-box__label">특허·실용신안</div></div>
</div></div>

<div class="content-block reveal"><h2>협력 파트너</h2>
<p>삼성 에스원 · 미쓰비시엘리베이터 · 후지테크코리아 · (주)스필 · 셀텍월드 · (주)유니콤</p></div>

<div class="content-block reveal"><h2>적용 분야</h2>
<div class="feature-grid">
<div class="feature-box"><h4>공동주택</h4><p>승강기·세대현관·지하주차장</p></div>
<div class="feature-box"><h4>공공시설</h4><p>화장실·안심귀갓길·버스정류장</p></div>
<div class="feature-box"><h4>상업시설</h4><p>편의점·1인 점포·독서실</p></div>
<div class="feature-box"><h4>1인 가구</h4><p>마이안심이 홈 안전</p></div>
</div></div>

<div class="content-block reveal"><h2>판매 전략</h2>
<p><strong>B2B</strong> — 10년간 구축한 에스원·스필·유니콤 영업망을 통한 신축·기축 아파트·공공 납품</p>
<p style="margin-top:8px"><strong>B2C/B2G</strong> — 마이안심이 자사몰·온라인 유통 및 지자체 시범사업 (금천구 100호 등)</p></div>"""

INQUIRY_BODY = """
<div class="inquiry-intro reveal">
<div class="inquiry-card neu-card"><strong>전화 상담</strong><p><a href="tel:07087099911">070-8709-9911</a></p><span>평일 09:00–18:00</span></div>
<div class="inquiry-card neu-card"><strong>카카오 플러스친구</strong><p>아성보이스</p><span>실시간 상담</span></div>
<div class="inquiry-card neu-card"><strong>팩스</strong><p>02-6203-1689</p><span>견적·서류 송부</span></div>
</div>

<div class="form-wrap neu-card reveal">
<h2 class="form-wrap__title">온라인 제품 문의</h2>
<p class="form-wrap__sub">워치독 비명감지기 도입·시범설치·OEM/ODM 협업 상담을 환영합니다.</p>
<form class="form" action="http://www.asungvoice.com/module/online/online_evn.php" method="post" target="_blank">
<input type="hidden" name="evnMode" value="join">
<input type="hidden" name="o_type" value="1">
<input type="hidden" name="returnURL" value="/sub/sub04_01.php">
<div class="form__section"><h3>기본 정보</h3>
<div class="form__row"><div class="form__group"><label class="form__label">회사명 / 단지명 <span class="req">*</span></label><input class="form__input" name="company" required></div>
<div class="form__group"><label class="form__label">승강기 설치대수</label><input class="form__input" name="serial" placeholder="대"></div></div>
<div class="form__row"><div class="form__group"><label class="form__label">성명 <span class="req">*</span></label><input class="form__input" name="user_name" required></div>
<div class="form__group"><label class="form__label">직위</label><input class="form__input" name="duty"></div></div></div>
<div class="form__section"><h3>연락처</h3>
<div class="form__group"><label class="form__label">연락처 <span class="req">*</span></label>
<div class="form__row form__row--phone"><select name="phone_1" class="form__input"><option>010</option><option>02</option><option>070</option></select>
<input class="form__input" name="phone_2" placeholder="국번" required><input class="form__input" name="phone_3" placeholder="번호" required></div></div>
<div class="form__group"><label class="form__label">이메일</label>
<div class="form__row form__row--email"><input class="form__input" name="email_id" placeholder="계정"><span>@</span><input class="form__input" name="email_domain" placeholder="도메인"></div></div></div>
<div class="form__section"><h3>문의 내용</h3>
<div class="form__group"><label class="form__label">관심분야</label>
<div class="form__checks form__checks--grid">
<label class="form__check neu-chip-check"><input type="checkbox" name="field[]" value="1"> 승강기 보안설비</label>
<label class="form__check neu-chip-check"><input type="checkbox" name="field[]" value="2"> 택배/배달 사칭 현관문보안</label>
<label class="form__check neu-chip-check"><input type="checkbox" name="field[]" value="3"> 화장실 보안설비</label>
<label class="form__check neu-chip-check"><input type="checkbox" name="field[]" value="4"> 비명인식 협업·OEM</label>
<label class="form__check neu-chip-check"><input type="checkbox" name="field[]" value="5"> 마이안심이</label>
</div></div>
<div class="form__group"><label class="form__label">문의사항 <span class="req">*</span></label><textarea class="form__textarea" name="contents" required placeholder="설치 환경, 대수, 일정 등을 적어주세요."></textarea></div></div>
<div class="form__privacy neu-inset">
<p><strong>개인정보 수집 및 이용 안내</strong></p>
<ul><li>이용 목적: 상담 및 진행</li><li>수집 항목: 이름, 연락처, 이메일, 상담내용</li><li>보유 기간: 상담 종료 후 6개월</li><li>담당: 070-8709-9912 / webmaster@asungvoice.com</li></ul>
<label class="form__check"><input type="checkbox" name="agree" value="Y" required> 개인정보 수집 및 이용에 동의합니다.</label>
</div>
<div class="form__actions"><button type="submit" class="btn btn--blue neu-btn">문의 제출</button>
<a href="tel:07087099911" class="btn btn--ghost">전화 문의</a></div>
</form></div>"""

AS_INQUIRY_BODY = """
<div class="inquiry-intro reveal">
<div class="inquiry-card neu-card"><strong>A/S 전화</strong><p><a href="tel:07087099911">070-8709-9911</a></p><span>평일 09:00–18:00</span></div>
<div class="inquiry-card neu-card"><strong>팩스</strong><p>02-6203-1689</p><span>A/S 접수 서류</span></div>
<div class="inquiry-card neu-card"><strong>이메일</strong><p><a href="mailto:webmaster@asungvoice.com">webmaster@asungvoice.com</a></p><span>고장 증상·사진 첨부</span></div>
</div>

<div class="form-wrap neu-card reveal">
<h2 class="form-wrap__title">A/S 접수 안내</h2>
<p class="form-wrap__sub">워치독 비명감지기 A/S는 전화·팩스·이메일로 접수해 주세요. 현장 방문 전 증상과 설치 위치를 알려주시면 신속히 대응합니다.</p>

<div class="as-steps">
<div class="flow__step neu-card"><div class="num">1</div><h4>접수</h4><p>전화·팩스·이메일</p></div>
<div class="flow__step neu-card"><div class="num">2</div><h4>상담</h4><p>증상·설치환경 확인</p></div>
<div class="flow__step neu-card"><div class="num">3</div><h4>방문/원격</h4><p>기술지원·부품 교체</p></div>
<div class="flow__step neu-card"><div class="num">4</div><h4>완료</h4><p>동작 테스트·보고</p></div>
</div>

<div class="content-block" style="margin-top:28px"><h3>접수 시 준비 사항</h3>
<ul class="info-list">
<li>설치 장소 (단지명·동·호 또는 시설명)</li>
<li>제품 종류 (승강기/화장실/일괄소등/마이안심이/모듈)</li>
<li>증상 (오동작·무응답·경보 미작동 등)</li>
<li>설치 일자 또는 납품 정보</li>
</ul></div>

<div class="form__actions" style="margin-top:24px">
<a href="tel:07087099911" class="btn btn--blue neu-btn">A/S 전화 접수</a>
<a href="mailto:webmaster@asungvoice.com" class="btn btn--ghost">이메일 문의</a>
</div>
</div>"""
