# charts.py
# matplotlib 그래프를 그리는 함수를 담당하는 파일

import platform

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


def set_korean_font():
    """
    matplotlib에서 한글이 깨지지 않도록 운영체제별 폰트를 설정하는 함수.

    Windows: Malgun Gothic
    Mac: AppleGothic
    Linux, Streamlit Cloud: NanumGothic
    """
    system = platform.system()

    if system == "Windows":
        font_name = "Malgun Gothic"
    elif system == "Darwin":
        font_name = "AppleGothic"
    else:
        font_name = "NanumGothic"

    plt.rcParams["font.family"] = font_name
    plt.rcParams["axes.unicode_minus"] = False


def draw_fuel_bar_chart(df: pd.DataFrame) -> plt.Figure:
    """
    선박별 평균 연료 소비량을 비교하는 가로 막대 차트.

    Args:
        df (pd.DataFrame): 저장 기록 데이터프레임

    Returns:
        plt.Figure: matplotlib Figure 객체
    """
    set_korean_font()

    fuel_by_ship = (
        df.groupby("선박명")["총연료(L)"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    bars = ax.barh(
        fuel_by_ship.index,
        fuel_by_ship.values,
        color="#2196F3",
        alpha=0.85
    )

    max_value = max(fuel_by_ship.values) if len(fuel_by_ship.values) > 0 else 1

    for bar, value in zip(bars, fuel_by_ship.values):
        ax.text(
            value + max_value * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.1f} L",
            va="center",
            fontsize=9
        )

    ax.set_title("선박별 평균 연료 소비량 비교", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("총 연료 소비량 (L)", fontsize=10)
    ax.set_ylabel("선박명", fontsize=10)

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    )

    ax.grid(axis="x", linestyle="--", alpha=0.3)

    plt.tight_layout()

    return fig


def draw_cost_bar_chart(df: pd.DataFrame) -> plt.Figure:
    """
    선박별 평균 운항 비용을 비교하는 가로 막대 차트.

    Args:
        df (pd.DataFrame): 저장 기록 데이터프레임

    Returns:
        plt.Figure: matplotlib Figure 객체
    """
    set_korean_font()

    cost_by_ship = (
        df.groupby("선박명")["총비용(원)"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    bars = ax.barh(
        cost_by_ship.index,
        cost_by_ship.values,
        color="#4CAF50",
        alpha=0.85
    )

    max_value = max(cost_by_ship.values) if len(cost_by_ship.values) > 0 else 1

    for bar, value in zip(bars, cost_by_ship.values):
        ax.text(
            value + max_value * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{value / 10000:,.0f} 만원",
            va="center",
            fontsize=9
        )

    ax.set_title("선박별 평균 운항 비용 비교", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("총 운항 비용 (원)", fontsize=10)
    ax.set_ylabel("선박명", fontsize=10)

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    )

    ax.grid(axis="x", linestyle="--", alpha=0.3)

    plt.tight_layout()

    return fig


def draw_cost_trend_chart(df: pd.DataFrame) -> plt.Figure:
    """
    저장 순서에 따른 운항 비용 추이를 보여주는 꺾은선 차트.

    Args:
        df (pd.DataFrame): 저장 기록 데이터프레임

    Returns:
        plt.Figure: matplotlib Figure 객체
    """
    set_korean_font()

    df_sorted = df.sort_values("번호").reset_index(drop=True)

    x_values = range(1, len(df_sorted) + 1)
    y_values = df_sorted["총비용(원)"].values

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        x_values,
        y_values,
        marker="o",
        color="#FF5722",
        linewidth=2,
        markersize=7
    )

    for x, y, name in zip(x_values, y_values, df_sorted["선박명"]):
        ax.annotate(
            f"{name}\n{y / 10000:,.0f}만원",
            xy=(x, y),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=8
        )

    ax.set_title("운항 비용 추이", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("저장 순번", fontsize=10)
    ax.set_ylabel("총 운항 비용 (원)", fontsize=10)

    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"{y:,.0f}")
    )

    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()

    return fig
