"""HTML body fragments for build_site.py — IR 자료 기반 HTML 콘텐츠"""


def _vs(title, subtitle, left_label, left_items, right_label, right_items, impact):
    left = "".join(f"<li><strong>{h}</strong><span>{p}</span></li>" for h, p in left_items)
    right = "".join(f"<li><strong>{h}</strong><span>{p}</span></li>" for h, p in right_items)
    return f'''<div class="content-block reveal"><h2>{title}</h2>
<p class="section-sub">{subtitle}</p>
<div class="vs-block">
<div class="vs-block__col vs-block__col--risk"><div class="vs-block__label">{left_label}</div><ul>{left}</ul></div>
<div class="vs-block__badge">VS</div>
<div class="vs-block__col vs-block__col--solve"><div class="vs-block__label">{right_label}</div><ul>{right}</ul></div>
</div>
<div class="vs-impact">{impact}</div></div>'''


def _flow(steps):
    parts = []
    for i, (h, p) in enumerate(steps, 1):
        parts.append(f'<div class="flow__step neu-card"><div class="num">{i}</div><h4>{h}</h4><p>{p}</p></div>')
        if i < len(steps):
            parts.append('<span class="flow__arrow">→</span>')
    return f'<div class="flow flow--wrap">{"".join(parts)}</div>'


def _features(items):
  boxes = "".join(f'<div class="feature-box neu-card"><h4>{h}</h4><p>{p}</p></div>' for h, p in items)
  return f'<div class="feature-grid">{boxes}</div>'


def _fig(file, alt, title=None, cap=None):
    h = f'<h2>{title}</h2>' if title else ''
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return f'''<div class="content-block reveal">{h}
<figure class="ir-figure neu-card"><img src="../assets/images/diagrams/{file}" alt="{alt}" loading="lazy">{c}</figure></div>'''


ELEVATOR_BODY = """
<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/elevator.png" alt="WD-600MD 승강기 비명감지기"></div>
<div class="prod-hero__info"><span class="model">WD-600MD Series · B2B 승강기</span><h2>승강기 비명인식기</h2>
<p><strong>AI도 인정한 국내 대표 브랜드.</strong> 승강기 및 공중화장실의 안전을 책임지는 프리미엄 비상 대응 솔루션입니다. 딥러닝 기반 실시간 비명 인식으로 경광등·경고방송·비상통화장치를 즉시 연동합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>
""" + _vs(
  "기존 시스템의 한계 vs 워치독 즉시 대응",
  "수동적 감시 시스템과 능동적 즉시 대응 시스템 비교",
  "CURRENT LIMITATIONS",
  [
    ("조작 불가능한 비상버튼", "피해자가 제압당하거나 당황하여 물리적 버튼 조작이 불가능한 상황 빈번"),
    ("CCTV의 수동적 한계", "단순 녹화 위주로 실시간 범죄 제지가 어려움"),
    ("골든타임 확보 실패", "밀폐 공간 특성상 신속한 외부 도움 요청 실패로 피해 확대"),
  ],
  "WATCHDOG SOLUTION",
  [
    ("비접촉 자동 감지", '"사람살려", "강도야" 등 비명만으로 즉시 작동 — 물리적 제약 극복'),
    ("능동적 현장 대응", "비명 인식 즉시 경광등 점멸 및 강력 경고방송으로 범죄자 심리 위축"),
    ("자동 구조 요청", "경비실·통합관제센터 자동 호출로 골든타임 내 신속한 구조 연계"),
  ],
  "KEY IMPACT — 범행 의지 사전 차단 &amp; 피해 최소화",
) + _fig("elevator-system.png", "승강기용 시스템 구성도", "시스템 구성", "비명 인식 → 현장 경광등·방송 → 방재실·경비실·112 연동") + _fig("elevator-flow.png", "승강기용 동작 흐름", "동작 흐름", "비명 인식부터 상황 종료까지 7단계 자동화 대응") + """
<div class="content-block reveal"><h2>제품 특징</h2>
""" + _features([
  ("딥러닝 &amp; 멀티 트리거", '"사람살려", "강도야", "도와주세요" 등 특정 비명 단어 정확 인식'),
  ("Digital 2-Mic", "노이즈 캔슬링·장거리 수음 최적화 디지털 듀얼 마이크"),
  ("자체 비명 DB", "어린이·여성·남성 등 다양한 계층 실제 비명 데이터 학습"),
  ("오인식 최소화", "단순 고성·생활 소음과 실제 위급 비명 구분"),
  ("Edge AI", "클라우드 전송 없이 단말기 내 연산 — 사생활 침해 원천 차단"),
  ("표준 호환성", "NO 무전원 접점 — 기존 비상통화장치·관제 시스템 완벽 호환"),
]) + """
</div>

<div class="content-block reveal"><h2>경쟁 기술 비교</h2>
<div class="table-scroll"><table class="spec-table compare-table">
<thead><tr><th>구분</th><th>워치독</th><th>승강기 업체</th><th>CCTV 업체</th></tr></thead>
<tbody>
<tr><td>적용기술</td><td>딥러닝 AI + 자체 DB</td><td>단순 dB 감지</td><td>영상 행동 분석</td></tr>
<tr><td>인식 단어</td><td>사람살려·강도야·아악 등</td><td>모든 큰 소리 반응</td><td>시각 정보 의존</td></tr>
<tr><td>오인식률</td><td>매우 낮음</td><td>높음 (생활소음)</td><td>환경 변화에 취약</td></tr>
<tr><td>지속 운영</td><td>안정적 지속 운영</td><td>잦은 오작동 중단</td><td>관리자 피로도 증가</td></tr>
</tbody></table></div></div>

<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>모델</th><td>WD-600MD / WD-100E</td></tr>
<tr><th>마이크</th><td>고성능 Digital 2-Mic 어레이</td></tr>
<tr><th>인식 단어</th><td>사람살려, 강도야, 도와주세요, 아악, 꺄악</td></tr>
<tr><th>인식레벨</th><td>90dB / 95dB / 100dB 3단계</td></tr>
<tr><th>출력</th><td>NO(Normal Open) 무전원 접점</td></tr>
<tr><th>경고방송</th><td>"비상상황입니다. 지금 즉시 출동합니다." (35초)</td></tr>
<tr><th>설치위치</th><td>승객버튼 조작반 직상부 벽면 또는 천정</td></tr></table></div>
<div class="content-block reveal"><p class="note-box">※ 동일 워치독 기술: <a href="restroom.html">화장실 비명감지기</a> · <a href="light-switch.html">일괄소등스위치</a> · <a href="module.html">비명인식 모듈</a></p></div>"""

RESTROOM_BODY = """
<div class="prod-hero reveal prod-hero--watchdog">
<div class="prod-hero__img prod-hero__img--logo"><img src="../assets/images/products/logo-watchdog.png" alt="워치독"></div>
<div class="prod-hero__info"><span class="model">워치독 WatchDog · WD 시리즈</span><h2>화장실 비명인식기</h2>
<p>승강기용 워치독과 <strong>동일한 비명인식 기술</strong>입니다. 노출형·매입형으로 설치하며, 화장실 내 대화는 녹음·전송되지 않고 비명 발생 시에만 경보합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>
""" + _vs(
  "안전 사각지대 vs 워치독 자동 호출",
  "여성 안전 사각지대 해소를 위한 능동형 솔루션",
  "SAFETY BLIND SPOTS",
  [
    ("CCTV 설치 법적 금지", "개인정보보호법상 화장실 내부 CCTV 불가 — 범죄 예방 사각지대"),
    ("여성 대상 강력범죄", "몰카·성범죄·폭행 등 여성 대상 범죄 빈번, 이용자 불안 증대"),
    ("비상벨 접근성 한계", "제압당하거나 당황한 상태에서 버튼 조작 불가"),
  ],
  "ACTIVE RESPONSE",
  [
    ("비명 인식 자동 호출", '"사람살려" 비명만으로 버튼 없이 즉시 구조 요청'),
    ("경보·경고방송", "감지 즉시 강력 경보음·경고방송으로 범행 의지 차단"),
    ("검증된 현장 적용", "부산대 400개소 · 여의도 파크원 217개소 등 대규모 납품"),
  ],
  "KEY IMPACT — CCTV 없는 공간도 24시간 안심 구역화",
) + _fig("restroom-system.png", "화장실용 시스템 구성도", "시스템 구성", "화장실 내부 → 유·무선 중계 → 경비실·112 출동") + _fig("restroom-flow.png", "화장실용 동작 흐름", "동작 흐름", "CCTV 없는 환경 특화 7단계 자동 대응") + """
<div class="content-block reveal"><h2>적용 기술</h2>
""" + _features([
  ("다양한 인식 단어", '"강도야", "사람살려", "도와주세요", "아악", "꺄악" 정확 식별'),
  ("멀티 트리거", "생활 소음과 위급 비명 선별 인식 — 오작동 원천 차단"),
  ("개인정보 보호", "녹음·감청 없이 소리 패턴만 분석"),
  ("음성인식 칩셋", "고성능 전용 칩셋으로 지연 없는 즉각 반응"),
  ("NO 접점 출력", "기존 비상벨·경광등·관제 시스템 손쉬운 연동"),
  ("여성·아동 최적화", "High Pitch 음성 톤에 최적화된 딥러닝 모델"),
]) + """
</div>

<div class="content-block reveal"><h2>적용 사례</h2>
<div class="stats-row">
<div class="stat-box neu-stat"><div class="stat-box__num">400</div><div class="stat-box__label">부산대 여자화장실</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">217</div><div class="stat-box__label">여의도 파크원</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">50만</div><div class="stat-box__label">전국 공중화장실 TAM</div></div>
</div></div>

<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>제품군</th><td>워치독 WatchDog (승강기용과 동일 기술)</td></tr>
<tr><th>설치 타입</th><td>노출형 / 매입형(다운라이트)</td></tr>
<tr><th>통신</th><td>유선(RS-485) / RF(447MHz) / 3G·LTE</td></tr>
<tr><th>인식 단어</th><td>강도야, 사람살려, 도와주세요, 아악, 꺄악</td></tr>
<tr><th>프라이버시</th><td>녹음·감청 없음, 소리 패턴만 분석</td></tr></table></div>"""

LIGHT_SWITCH_BODY = """
<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/control-panel.png" alt="비명인식 일괄소등스위치"></div>
<div class="prod-hero__info"><span class="model">5&quot; FTS · 홈네트워크 연동 · 특허 2건</span><h2>비명인식 일괄소등스위치</h2>
<p>일상의 편리함에 안전을 더한 혁신 특허 제품입니다. 현관 일괄소등 스위치에 비명인식 기능을 탑재하여, 외부인 대면 시 침입 위협을 즉시 감지·통보합니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">도입 문의</a></div></div>
""" + _vs(
  "주거 공간 침입 위협 vs 비명인식 일괄소등스위치",
  "재실 중 강력범죄 위협과 대응 솔루션",
  "SECURITY THREATS",
  [
    ("위장 침입 범죄 증가", "택배·배달원 위장하여 재실 중 입주민 대상 기습 강력 범죄"),
    ("귀가 시 현관앞 범죄", "도어락 래그 — 문이 닫히기 전 침입하는 범죄"),
    ("대응 수단 부재", "긴박한 대치 상황에서 스마트폰·비상벨 조작 불가"),
  ],
  "INTEGRATED SOLUTION",
  [
    ("HN 월패드 경보 연동", "비명 감지 시 세대 내 강력 경보 — 범죄자 심리 위축"),
    ("경비실 자동 호출", "아파트 경비실·방재실로 비상 상황 즉시 전파"),
    ("24시간 빈틈없는 경계", "재택/외출 구분 없이 현관 보안"),
  ],
  "KEY IMPACT — 재택/외출 구분 없는 24시간 빈틈없는 경계",
) + _fig("lightswitch-system.png", "일괄소등SW 시스템 구성도", "시스템 구성", "세대 현관 → HN 월패드 → 경비실·관제센터") + _fig("lightswitch-patent.png", "일괄소등SW 특허 기술", "특허 기술", "외부인 대면 시에만 비명인식 활성화 — 오작동 원천 차단") + """
<div class="content-block reveal"><h2>제품 사양</h2>
<table class="spec-table">
<tr><th>디스플레이</th><td>5&quot; Full Touch LCD (정전식)</td></tr>
<tr><th>전원</th><td>AC 220V / 60Hz</td></tr>
<tr><th>통신</th><td>RS-485 (홈넷 연동)</td></tr>
<tr><th>핵심 기능</th><td>일괄소등 · 엘리베이터 호출 · 가스차단 · 비명인식 보안</td></tr>
<tr><th>인식 단어</th><td>강도야, 사람살려, 도와주세요</td></tr>
<tr><th>특허</th><td>제10-2132316호, 제10-2237852호</td></tr>
</table></div>

<div class="content-block reveal"><h2>적용 실적</h2>
<div class="stats-row">
<div class="stat-box neu-stat"><div class="stat-box__num">100%</div><div class="stat-box__label">진주 아너스 840세대</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">444</div><div class="stat-box__label">유승한내들 세대</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">2024</div><div class="stat-box__label">국내 최초 M/H 적용</div></div>
</div>
<p style="margin-top:14px;font-size:.88rem;color:var(--text-2)">협력사: (주)스필 배선기구 전문 · 전기신문 등 언론 보도</p></div>"""

HOME_KEEPER_BODY = """
<div class="prod-hero reveal prod-hero--pink">
<div class="prod-hero__img"><img src="../assets/images/products/home-keeper.png" alt="마이안심이"></div>
<div class="prod-hero__info"><span class="model">마이안심이 · 실용신안 KR 20-0498161</span><h2>마이안심이</h2>
<p><strong>나를 지켜주는 스마트한 안심 파트너.</strong> 1인 여성 가구(280만)를 위한 재택 방범 디바이스. 비명 하나로 110dB 이상 강력 경보와 보호자 앱 알림을 즉시 전송합니다.</p>
<a href="../support/inquiry.html" class="btn btn--pink">도입 문의</a></div></div>
""" + _vs(
  "범죄 노출 vs 마이안심이 솔루션",
  "1인 여성가구 방범의 필요성",
  "TARGET RISK · 280만 가구",
  [
    ("택배/배달 가장 침입", "택배·배달원 위장하여 현관문을 열게 한 뒤 침입하는 강력 범죄"),
    ("현관 개방 시 취약점", "귀가 직후·배달 수령 시 문이 열린 찰나의 순간이 범죄 표적"),
    ("귀가길 미행·침입", "늦은 밤 귀가 시 미행·침입 시도에 즉각적 구조 요청 어려움"),
  ],
  "마이안심이 SOLUTION",
  [
    ("110dB 이상 강력 경보", "비명 인식 즉시 강력 경고음 송출 — 범죄자 퇴치"),
    ("지정 보호자 즉시 통보", "부모님·지인 등 사전 등록 연락처로 비상 상황 자동 전송"),
    ("모바일 앱 연동", "집안 상태 모니터링·설정 — 언제 어디서나 나만의 보안관"),
  ],
  "KEY VALUE — 나만의 든든한 AI 보안관",
) + _fig("homekeeper-system.png", "마이안심이 시스템 구성도", "시스템 구성", "자석감지기 → 마이안심이 본체 → 보호자 앱 알림") + _fig("homekeeper-sensor.png", "마이안심이 자석감지기", "자석감지기 센서", "BLE 무선 · 문열림 감지 → 비명인식 대기모드") + _fig("homekeeper-app.png", "마이안심이 모바일 앱", "모바일 앱", "재택/외출 모드 · 비상 알림 · 보호자 연락망") + """
<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>제품명</th><td>마이안심이</td></tr>
<tr><th>인식 방식</th><td>On-Device AI 비명 인식 (음원 패턴만 분석)</td></tr>
<tr><th>알람</th><td>110dB 이상 사이렌 + SOS 비상호출</td></tr>
<tr><th>센서</th><td>BLE 자석감지기 (CR2032, 약 1년)</td></tr>
<tr><th>통신</th><td>WiFi (2.4GHz) · BLE · 3G/LTE</td></tr>
<tr><th>전원</th><td>DC 5V (USB-C) + 보조배터리 호환</td></tr>
<tr><th>특허</th><td>실용신안 제20-0498161호 (2024.07)</td></tr>
<tr><th>설치</th><td>홈네트워크 불필요 · 독립 설치형</td></tr></table></div>"""

MODULE_BODY = """
<div class="prod-hero reveal">
<div class="prod-hero__img"><img src="../assets/images/products/pcb-module.png" alt="비명인식 모듈"></div>
<div class="prod-hero__info"><span class="model">WD-Module-V2 · B2B 연동형</span><h2>비명인식 모듈</h2>
<p><strong>어디든 적용 가능한 핵심 기술.</strong> 기존 비상벨, CCTV, 주차 시스템에 비명인식 기능을 더해 가치를 높이는 임베디드 모듈입니다.</p>
<a href="../support/inquiry.html" class="btn btn--blue">OEM/ODM 문의</a></div></div>

<div class="content-block reveal"><h2>모듈 소개</h2>
<p>기존 시스템의 하드웨어 변경 없이 <strong>간단한 결선만으로</strong> 지능형 비명감지 기능을 추가합니다. SID 내장 디지털 비명인식 모듈로 지하주차장 비상벨, 승강기 미디어 타운보드, 키오스크 등 다양한 기존 장비에 탑재 가능합니다.</p>
</div>
""" + _fig("module-overview.png", "비명인식 모듈 소개 및 사양", "모듈 개요", "WD-Module-V2 · NO 접점 · UART/GPIO 연동") + """
<div class="content-block reveal"><h2>주요 적용 분야</h2>
""" + _features([
  ("지하주차장", "기존 비상벨에 비명감지 기능 추가 (아마노 등)"),
  ("승강기", "비상호출 버튼과 연동하여 자동 호출"),
  ("미디어 타운보드", "승강기 미디어·키오스크 연동"),
  ("세대 방범", "월패드·도어락 Security 연동"),
]) + """
</div>

<div class="content-block reveal"><h2>기술 사양</h2><table class="spec-table">
<tr><th>모델</th><td>WD-Module-V2</td></tr>
<tr><th>입력 전원</th><td>DC 5V (USB Standard) Low Power</td></tr>
<tr><th>출력 방식</th><td>NO (Normally Open) 접점 출력 Dry Contact</td></tr>
<tr><th>통신 연동</th><td>UART / GPIO</td></tr>
<tr><th>인식 거리</th><td>Max 5~10m (환경에 따라 조절)</td></tr>
<tr><th>반응 속도</th><td>비명 감지 후 0.5초 이내 신호 송출</td></tr>
<tr><th>인식 단어</th><td>사람살려, 강도야, 도와주세요, 아악, 꺄악</td></tr></table></div>"""

BUSINESS_BODY = """
<div class="content-block reveal biz-intro">
<p class="biz-intro__lead">㈜아성보이스는 <strong>AI On-Device 비명 인식</strong> 기술로 승강기·화장실·세대현관·1인 가구 등 범죄 사각지대를 보호하는 <strong>생활안전 표준화 솔루션</strong>을 제공합니다.</p>
</div>
""" + _fig("biz-model-matrix.png", "비즈니스 모델 매트릭스", "비즈니스 모델", "워치독 · 일괄소등 · 마이안심이 · 비명인식 모듈 4대 포트폴리오") + """
<div class="biz-quicklinks reveal">
<a href="../products/elevator.html" class="biz-quicklink neu-card">승강기 비명감지</a>
<a href="../products/restroom.html" class="biz-quicklink neu-card">화장실 비명감지</a>
<a href="../products/light-switch.html" class="biz-quicklink neu-card">일괄소등스위치</a>
<a href="../products/home-keeper.html" class="biz-quicklink neu-card">마이안심이</a>
<a href="../products/module.html" class="biz-quicklink neu-card">비명인식 모듈</a>
</div>
""" + _fig("biz-market-overview.png", "시장 기회 Overview", "시장 기회", "승강기 51.4만 · 화장실 50만 · 신축 43만호 · 1인여성 280만") + _fig("biz-market-segments.png", "시장 세그먼트 상세", "시장 세그먼트", "B2B · B2G · B2C 타겟 시장 및 구매 결정자") + """
<div class="content-block reveal"><h2>핵심 역량</h2>
<div class="stats-row">
<div class="stat-box neu-stat"><div class="stat-box__num">99%</div><div class="stat-box__label">비명 인식률</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">3,000+</div><div class="stat-box__label">누적 납품</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">10년+</div><div class="stat-box__label">현장 검증 (2017~)</div></div>
<div class="stat-box neu-stat"><div class="stat-box__num">3건</div><div class="stat-box__label">특허·실용신안</div></div>
</div>
<div class="biz-creds" style="margin-top:20px">
<span class="biz-cred neu-card">승강기 안전기술 우수상 (2020)</span>
<span class="biz-cred neu-card">SBS 8시 뉴스 집중 보도</span>
<span class="biz-cred neu-card">네이버 AI 브리핑 대표 기술</span>
<span class="biz-cred neu-card">삼성 에스원 공식 납품사</span>
</div></div>

<div class="content-block reveal"><h2>협력 파트너</h2>
<div class="partner-grid">
<span class="partner-chip neu-card">삼성 에스원</span>
<span class="partner-chip neu-card">미쓰비시엘리베이터</span>
<span class="partner-chip neu-card">후지테크코리아</span>
<span class="partner-chip neu-card">(주)스필</span>
<span class="partner-chip neu-card">셀텍월드</span>
<span class="partner-chip neu-card">아마노코리아</span>
</div></div>

<div class="content-block reveal"><h2>판매 전략</h2>
<div class="biz-strategy">
<div class="biz-strategy__item neu-card"><strong>B2B 채널</strong><p>에스원·스필·미쓰비시EL 등 대형 파트너 영업망을 통한 신축·기축 아파트·공공 납품</p></div>
<div class="biz-strategy__item neu-card"><strong>B2C/B2G</strong><p>마이안심이 온라인 유통 및 지자체 1인여성가구 안심사업</p></div>
<div class="biz-strategy__item neu-card"><strong>라이선스</strong><p>제품 판매 + 라이선스 수익 결합 고수익 모델</p></div>
</div></div>"""

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
<div class="as-step neu-card"><div class="as-step__num">1</div><h4>접수</h4><p>전화·팩스·이메일</p></div>
<div class="as-step neu-card"><div class="as-step__num">2</div><h4>상담</h4><p>증상·설치환경 확인</p></div>
<div class="as-step neu-card"><div class="as-step__num">3</div><h4>방문/원격</h4><p>기술지원·부품 교체</p></div>
<div class="as-step neu-card"><div class="as-step__num">4</div><h4>완료</h4><p>동작 테스트·보고</p></div>
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
