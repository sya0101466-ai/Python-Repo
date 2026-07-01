# ocean_view.py
# 저장된 선박 기록을 가상의 바다 위에서 움직이는 배 이모지로 보여주는 파일

import html

import pandas as pd


def _safe_text(value) -> str:
    """
    HTML에 들어갈 텍스트를 안전하게 변환하는 함수.
    선박명 등에 특수문자가 들어가도 HTML 구조가 깨지지 않도록 escape 처리합니다.
    """
    if value is None:
        return ""

    return html.escape(str(value))


def _safe_float(value, default: float = 0.0) -> float:
    """
    숫자 변환이 실패해도 앱이 멈추지 않도록 안전하게 float으로 변환합니다.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_value(row, column_name: str, default=""):
    """
    DataFrame 행에서 값을 안전하게 가져오는 함수.
    컬럼이 없을 경우 기본값을 반환합니다.
    """
    if column_name in row:
        return row[column_name]

    return default


def _speed_to_duration(speed: float) -> float:
    """
    실제 평균속도(km/h)를 CSS 애니메이션 시간(초)으로 변환합니다.

    속도가 빠를수록 animation-duration이 짧아지고,
    duration이 짧을수록 화면에서 더 빠르게 움직입니다.
    """
    min_speed = 5.0
    max_speed = 60.0

    slow_duration = 46.0
    fast_duration = 13.0

    speed = max(min_speed, min(speed, max_speed))

    ratio = (speed - min_speed) / (max_speed - min_speed)

    duration = slow_duration - ratio * (slow_duration - fast_duration)

    return round(duration, 1)


def _get_route_points(index: int):
    """
    선박별 이동 경로를 반환하는 함수.

    이번 버전은 툴팁이 배 위에 뜨도록 되돌렸기 때문에
    툴팁이 잘리지 않도록 이동 좌표를 화면 가장자리에서 조금 떨어뜨렸습니다.

    x 좌표:
    - 너무 왼쪽/오른쪽으로 가면 툴팁이 좌우로 잘릴 수 있으므로 22%~78% 중심으로 이동

    y 좌표:
    - 너무 위쪽으로 가면 배 위 툴팁이 잘릴 수 있으므로 42% 이상에서 움직이게 조정
    """
    route_templates = [
        [(22, 44), (38, 39), (62, 43), (76, 55), (52, 70), (26, 62)],
        [(74, 46), (58, 56), (34, 48), (24, 63), (46, 74), (70, 66)],
        [(24, 70), (40, 58), (64, 63), (76, 50), (56, 42), (30, 48)],
        [(70, 72), (52, 62), (30, 68), (22, 54), (42, 41), (72, 48)],
        [(28, 54), (48, 42), (74, 54), (60, 73), (36, 68), (24, 58)],
        [(72, 64), (56, 46), (34, 42), (24, 56), (44, 72), (76, 68)],
    ]

    return route_templates[index % len(route_templates)]


def create_ocean_view(df: pd.DataFrame) -> str:
    """
    저장된 선박 기록 DataFrame을 받아 가상 바다 HTML 문자열을 생성합니다.

    Args:
        df (pd.DataFrame): database.py의 get_all_records()가 반환한 데이터프레임

    Returns:
        str: Streamlit components.html()에 넣을 HTML 문자열
    """
    if df is None or df.empty:
        return """
        <div style="
            padding: 40px;
            text-align: center;
            font-family: Arial, sans-serif;
            background: #e3f2fd;
            border-radius: 16px;
            color: #0d47a1;
        ">
            <h2>🌊 아직 바다에 띄울 선박이 없습니다</h2>
            <p>계산 결과를 먼저 저장해 주세요.</p>
        </div>
        """

    # 화면이 너무 복잡해지지 않도록 최근 10개만 표시
    df_display = df.head(10).copy()

    ship_elements = []
    route_keyframes = []

    for index, (_, row) in enumerate(df_display.iterrows()):
        ship_name = _safe_text(_get_value(row, "선박명", "이름 없는 선박"))

        distance = _safe_float(_get_value(row, "운항거리(km)", 0))
        speed = _safe_float(_get_value(row, "평균속도(km/h)", 0))
        operation_hours = _safe_float(_get_value(row, "운항시간(h)", 0))
        total_fuel = _safe_float(_get_value(row, "총연료(L)", 0))
        total_cost = _safe_float(_get_value(row, "총비용(원)", 0))
        created_at = _safe_text(_get_value(row, "저장일시", ""))

        duration = _speed_to_duration(speed)

        ship_size = 32 + (index % 3) * 4

        route_points = _get_route_points(index)

        keyframe_name = f"ship-route-{index}"

        keyframe_css_parts = []

        percent_steps = [0, 20, 40, 60, 80, 100]

        for step, point in zip(percent_steps, route_points):
            x_position, y_position = point

            keyframe_css_parts.append(
                f"""
                {step}% {{
                    left: {x_position}%;
                    top: {y_position}%;
                }}
                """
            )

        route_keyframes.append(
            f"""
            @keyframes {keyframe_name} {{
                {"".join(keyframe_css_parts)}
            }}
            """
        )

        if index % 2 == 0:
            ship_direction = "scaleX(1)"
        else:
            ship_direction = "scaleX(-1)"

        ship_html = f"""
        <div class="ship-card"
            data-ship-index="{index}"
            data-ship-name="{ship_name}"
             style="
                animation-name: {keyframe_name};
                animation-duration: {duration}s;
                animation-delay: -{index * 2.4}s;
             ">

            <div class="ship-emoji" style="font-size: {ship_size}px; transform: {ship_direction};">
                🚢
            </div>

            <div class="ship-label">
                {ship_name}
            </div>

            <div class="ship-tooltip">
                <div class="tooltip-title">🚢 {ship_name}</div>
                <div class="tooltip-row">평균속도: <b>{speed:,.1f} km/h</b></div>
                <div class="tooltip-row">운항거리: <b>{distance:,.1f} km</b></div>
                <div class="tooltip-row">운항시간: <b>{operation_hours:,.1f} h</b></div>
                <div class="tooltip-row">총연료: <b>{total_fuel:,.1f} L</b></div>
                <div class="tooltip-row">총비용: <b>{total_cost:,.0f} 원</b></div>
                <div class="tooltip-date">저장일시: {created_at}</div>
            </div>
        </div>
        """

        ship_elements.append(ship_html)

    ships_html = "\n".join(ship_elements)
    route_keyframes_css = "\n".join(route_keyframes)

    collision_script = """
    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const ocean = document.querySelector(".ocean-wrapper");
            const ships = Array.from(document.querySelectorAll(".ship-card"));

            if (!ocean || ships.length < 2) {
                return;
            }

            const collisionCooldown = new Map();
            const CHECK_INTERVAL_MS = 120;
            const COLLISION_COOLDOWN_MS = 1500;
            const COLLISION_PAUSE_MS = 850;

            function getShipHitBox(ship) {
                const emoji = ship.querySelector(".ship-emoji");

                if (!emoji) {
                    return ship.getBoundingClientRect();
                }

                const rect = emoji.getBoundingClientRect();
                const padding = 4;

                return {
                    left: rect.left + padding,
                    right: rect.right - padding,
                    top: rect.top + padding,
                    bottom: rect.bottom - padding,
                    width: rect.width - padding * 2,
                    height: rect.height - padding * 2
                };
            }

            function isOverlapping(rectA, rectB) {
                return !(
                    rectA.right < rectB.left ||
                    rectA.left > rectB.right ||
                    rectA.bottom < rectB.top ||
                    rectA.top > rectB.bottom
                );
            }

            function getCollisionKey(shipA, shipB) {
                const indexA = shipA.dataset.shipIndex || "a";
                const indexB = shipB.dataset.shipIndex || "b";

                return [indexA, indexB].sort().join("-");
            }

            function showCollisionFlash(rectA, rectB) {
                const oceanRect = ocean.getBoundingClientRect();

                const centerX = ((rectA.left + rectA.right + rectB.left + rectB.right) / 4) - oceanRect.left;
                const centerY = ((rectA.top + rectA.bottom + rectB.top + rectB.bottom) / 4) - oceanRect.top;

                const flash = document.createElement("div");
                flash.className = "collision-flash";
                flash.textContent = "💥";
                flash.style.left = centerX + "px";
                flash.style.top = centerY + "px";

                ocean.appendChild(flash);

                setTimeout(function () {
                    flash.remove();
                }, 900);
            }

            function triggerCollision(shipA, shipB, rectA, rectB) {
                const key = getCollisionKey(shipA, shipB);
                const now = Date.now();
                const lastTime = collisionCooldown.get(key) || 0;

                if (now - lastTime < COLLISION_COOLDOWN_MS) {
                    return;
                }

                collisionCooldown.set(key, now);

                shipA.classList.add("collision");
                shipB.classList.add("collision");

                showCollisionFlash(rectA, rectB);

                setTimeout(function () {
                    shipA.classList.remove("collision");
                    shipB.classList.remove("collision");
                }, COLLISION_PAUSE_MS);
            }

            function checkCollisions() {
                for (let i = 0; i < ships.length; i++) {
                    for (let j = i + 1; j < ships.length; j++) {
                        const shipA = ships[i];
                        const shipB = ships[j];

                        const rectA = getShipHitBox(shipA);
                        const rectB = getShipHitBox(shipB);

                        if (isOverlapping(rectA, rectB)) {
                            triggerCollision(shipA, shipB, rectA, rectB);
                        }
                    }
                }
            }

            setInterval(checkCollisions, CHECK_INTERVAL_MS);
        });
    </script>
    """

    ocean_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8" />
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                overflow: hidden;
            }}

            .ocean-wrapper {{
                width: 100%;
                height: 820px;
                position: relative;
                overflow: hidden;
                border-radius: 22px;
                border: 1px solid rgba(2, 73, 117, 0.35);
                background:
                    linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px),
                    radial-gradient(circle at 15% 20%, rgba(255,255,255,0.20), transparent 10%),
                    radial-gradient(circle at 80% 30%, rgba(255,255,255,0.13), transparent 12%),
                    radial-gradient(circle at 35% 78%, rgba(255,255,255,0.10), transparent 14%),
                    linear-gradient(135deg, #0b7fab 0%, #0a5e91 42%, #063f73 100%);
                background-size:
                    70px 70px,
                    70px 70px,
                    100% 100%,
                    100% 100%,
                    100% 100%,
                    100% 100%;
            }}

            .ocean-header {{
                position: absolute;
                top: 18px;
                left: 22px;
                z-index: 30;
                padding: 12px 16px;
                border-radius: 14px;
                color: white;
                background: rgba(0, 38, 77, 0.45);
                backdrop-filter: blur(6px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.18);
            }}

            .ocean-header h2 {{
                margin: 0 0 4px 0;
                font-size: 20px;
            }}

            .ocean-header p {{
                margin: 0;
                font-size: 13px;
                opacity: 0.9;
            }}

            .map-badge {{
                position: absolute;
                right: 18px;
                top: 18px;
                z-index: 30;
                padding: 8px 12px;
                border-radius: 999px;
                color: #e3f2fd;
                background: rgba(0, 0, 0, 0.28);
                font-size: 12px;
                letter-spacing: 0.3px;
            }}

            .island {{
                position: absolute;
                font-size: 38px;
                opacity: 0.95;
                filter: drop-shadow(0 5px 8px rgba(0,0,0,0.25));
                z-index: 3;
            }}

            .island.one {{
                left: 10%;
                bottom: 16%;
            }}

            .island.two {{
                right: 13%;
                top: 35%;
            }}

            .island.three {{
                left: 72%;
                bottom: 18%;
                font-size: 30px;
            }}

            .wave {{
                position: absolute;
                color: rgba(255,255,255,0.42);
                font-size: 22px;
                animation: wave-move 6s ease-in-out infinite alternate;
                z-index: 2;
            }}

            .wave.w1 {{
                left: 28%;
                top: 26%;
            }}

            .wave.w2 {{
                left: 62%;
                top: 67%;
                animation-delay: -2s;
            }}

            .wave.w3 {{
                left: 45%;
                top: 48%;
                animation-delay: -4s;
            }}

            .wave.w4 {{
                left: 18%;
                top: 76%;
                animation-delay: -1s;
            }}

            .route-line {{
                position: absolute;
                left: 7%;
                right: 7%;
                height: 1px;
                border-top: 2px dashed rgba(255,255,255,0.16);
                z-index: 1;
            }}

            .route-line.r1 {{
                top: 34%;
            }}

            .route-line.r2 {{
                top: 54%;
            }}

            .route-line.r3 {{
                top: 74%;
            }}

            .ship-card {{
                position: absolute;
                z-index: 12;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 2px;
                cursor: pointer;
                animation-timing-function: linear;
                animation-iteration-count: infinite;
            }}

            .ship-card:hover {{
                animation-play-state: paused;
                z-index: 100;
            }}

            .ship-card.collision {{
                animation-play-state: paused !important;
                z-index: 180;
            }}

            .ship-card.collision .ship-emoji {{
                animation: ship-collision-shake 0.45s ease-in-out infinite;
                filter:
                    drop-shadow(0 0 8px rgba(255,255,255,0.9))
                    drop-shadow(0 0 14px rgba(255,193,7,0.85));
            }}

            .ship-card.collision .ship-label {{
                background: rgba(255, 87, 34, 0.85);
            }}

            .collision-flash {{
                position: absolute;
                transform: translate(-50%, -50%);
                z-index: 220;
                pointer-events: none;
                font-size: 34px;
                animation: collision-pop 0.85s ease-out forwards;
                filter: drop-shadow(0 6px 12px rgba(0,0,0,0.35));
            }}

            @keyframes ship-collision-shake {{
                0% {{
                    transform: translateX(0) rotate(0deg);
                }}
                25% {{
                    transform: translateX(-3px) rotate(-4deg);
                }}
                50% {{
                    transform: translateX(3px) rotate(4deg);
                }}
                75% {{
                    transform: translateX(-2px) rotate(-3deg);
                }}
                100% {{
                    transform: translateX(0) rotate(0deg);
                }}
            }}

            @keyframes collision-pop {{
                0% {{
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.4);
                }}
                20% {{
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1.25);
                }}
                100% {{
                    opacity: 0;
                    transform: translate(-50%, -70%) scale(1.75);
                }}
            }}

            .ship-emoji {{
                line-height: 1;
                filter: drop-shadow(0 6px 6px rgba(0,0,0,0.25));
                transition: filter 0.2s ease, transform 0.2s ease;
            }}

            .ship-card:hover .ship-emoji {{
                filter: drop-shadow(0 8px 12px rgba(255,255,255,0.55));
            }}

            .ship-label {{
                max-width: 125px;
                padding: 3px 8px;
                border-radius: 999px;
                font-size: 11px;
                color: white;
                background: rgba(0, 0, 0, 0.38);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                backdrop-filter: blur(4px);
            }}

            .ship-tooltip {{
                position: absolute;
                left: 50%;
                bottom: 68px;
                width: 270px;
                padding: 14px 15px;
                border-radius: 16px;
                color: #0b2538;
                background: rgba(255, 255, 255, 0.98);
                box-shadow: 0 14px 34px rgba(0,0,0,0.30);
                opacity: 0;
                visibility: hidden;
                transform: translateX(-50%) translateY(10px);
                transition: all 0.18s ease;
                pointer-events: none;
                font-size: 13px;
                z-index: 200;
            }}

            .ship-card:hover .ship-tooltip {{
                opacity: 1;
                visibility: visible;
                transform: translateX(-50%) translateY(0);
            }}

            .tooltip-title {{
                font-weight: 800;
                font-size: 15px;
                margin-bottom: 8px;
                color: #06446b;
                border-bottom: 1px solid #d8edf7;
                padding-bottom: 6px;
            }}

            .tooltip-row {{
                margin: 4px 0;
            }}

            .tooltip-date {{
                margin-top: 8px;
                padding-top: 6px;
                border-top: 1px dashed #c9dce7;
                font-size: 11px;
                color: #546e7a;
            }}

            .legend {{
                position: absolute;
                left: 22px;
                bottom: 28px;
                z-index: 40;
                padding: 11px 15px;
                border-radius: 12px;
                color: white;
                background: rgba(0, 38, 77, 0.46);
                font-size: 12px;
                line-height: 1.55;
                backdrop-filter: blur(6px);
                box-shadow: 0 8px 18px rgba(0,0,0,0.18);
            }}

            @keyframes wave-move {{
                0% {{
                    transform: translateY(0);
                    opacity: 0.25;
                }}
                100% {{
                    transform: translateY(12px);
                    opacity: 0.65;
                }}
            }}

            {route_keyframes_css}
        </style>
    </head>

    <body>
        <div class="ocean-wrapper">

            <div class="ocean-header">
                <h2>🌊 가상 바다 운항 보기</h2>
                <p>저장된 계산 결과를 바탕으로 선박이 자유롭게 움직입니다.</p>
            </div>

            <div class="map-badge">
                Virtual Ocean Map
            </div>

            <div class="route-line r1"></div>
            <div class="route-line r2"></div>
            <div class="route-line r3"></div>

            <div class="wave w1">〜 〜 〜</div>
            <div class="wave w2">〜 〜 〜</div>
            <div class="wave w3">〜 〜 〜</div>
            <div class="wave w4">〜 〜 〜</div>

            <div class="island one">🏝️</div>
            <div class="island two">🪨</div>
            <div class="island three">🏝️</div>

            {ships_html}

            <div class="legend">
                🚢 배에 마우스를 올리면 정지합니다.<br/>
                ⚡ 평균속도가 높을수록 더 빠르게 이동합니다.<br/>
                🧭 선박은 여러 지점을 순찰하듯 움직입니다.
            </div>
        </div>
        {collision_script}
    </body>
    </html>
    """

    return ocean_html
