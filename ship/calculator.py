# calculator.py
# 연료 소비량 및 운항 비용 계산 함수를 담당하는 파일


def calculate_fuel_consumption(operation_hours: float, fuel_per_hour: float) -> float:
    """
    총 연료 소비량을 계산하는 함수.

    Args:
        operation_hours (float): 운항 시간 (hour)
        fuel_per_hour (float): 시간당 연료 소비량 (L/h)

    Returns:
        float: 총 연료 소비량 (L)
    """
    if operation_hours <= 0:
        raise ValueError("운항 시간은 0보다 커야 합니다.")

    if fuel_per_hour <= 0:
        raise ValueError("시간당 연료 소비량은 0보다 커야 합니다.")

    total_fuel = operation_hours * fuel_per_hour

    return total_fuel


def calculate_total_cost(total_fuel: float, fuel_price: float) -> float:
    """
    총 운항 비용을 계산하는 함수.

    Args:
        total_fuel (float): 총 연료 소비량 (L)
        fuel_price (float): 연료 단가 (원/L)

    Returns:
        float: 총 운항 비용 (원)
    """
    if total_fuel <= 0:
        raise ValueError("총 연료 소비량은 0보다 커야 합니다.")

    if fuel_price <= 0:
        raise ValueError("연료 단가는 0보다 커야 합니다.")

    total_cost = total_fuel * fuel_price

    return total_cost


def calculate_all(
    operation_hours: float,
    fuel_per_hour: float,
    fuel_price: float
) -> dict:
    """
    연료 소비량과 총 비용을 한 번에 계산하는 함수.

    Args:
        operation_hours (float): 운항 시간 (hour)
        fuel_per_hour (float): 시간당 연료 소비량 (L/h)
        fuel_price (float): 연료 단가 (원/L)

    Returns:
        dict: 총 연료 소비량과 총 운항 비용
    """
    total_fuel = calculate_fuel_consumption(
        operation_hours=operation_hours,
        fuel_per_hour=fuel_per_hour
    )

    total_cost = calculate_total_cost(
        total_fuel=total_fuel,
        fuel_price=fuel_price
    )

    return {
        "total_fuel": total_fuel,
        "total_cost": total_cost
    }


if __name__ == "__main__":
    test_hours = 60.0
    test_fuel_per_hour = 120.0
    test_fuel_price = 1800.0

    result = calculate_all(
        operation_hours=test_hours,
        fuel_per_hour=test_fuel_per_hour,
        fuel_price=test_fuel_price
    )

    print("=" * 45)
    print("운항 비용 계산 테스트")
    print("=" * 45)
    print(f"운항 시간: {test_hours:,.1f} h")
    print(f"시간당 연료 소비량: {test_fuel_per_hour:,.1f} L/h")
    print(f"연료 단가: {test_fuel_price:,.0f} 원/L")
    print("-" * 45)
    print(f"총 연료 소비량: {result['total_fuel']:,.1f} L")
    print(f"총 운항 비용: {result['total_cost']:,.0f} 원")
    print("=" * 45)
