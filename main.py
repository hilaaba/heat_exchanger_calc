import sys
from math import pi
from typing import Dict, Tuple

import requests

CAS_REGISTRY_NUMBERS: Dict[str, str] = {
    'азот': 'C7727379',
    'кислород': 'C7782447',
    'аргон': 'C7440371',
    'метан': 'C74828',
    'углекислота': 'C124389',
    'водород': 'C1333740',
    'пропан': 'C74986',
    'бутан': 'C106978',
    'гелий': 'C7440597',
    'аммиак': 'C7664417',
}

PROPERTIES_NAMES: Tuple[str, ...] = (
    'Temperature',
    'Pressure',
    'Density',
    'Volume',
    'Internal Energy',
    'Enthalpy',
    'Entropy',
    'Cv',
    'Cp',
    'Sound_speed',
    'Joule_Thomson',
    'Viscosity',
    'Thermal Conductivity',
    'Phase',
)

DIAMETER_NOMINAL: Tuple[float, ...] = (
    2.5, 3, 4, 5, 6, 10, 15, 20, 25, 32, 40, 50, 65, 80, 100,
    125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000,
    1200, 1400, 1600, 1800, 2000, 2200, 2400, 2800, 3000, 3400, 4000,
)

LIQUID_VELOCITY: int = 3
GAS_VELOCITY: int = 17

NORMAL_PRESSURE: float = 1.013
NORMAL_TEMPERATURE: float = 273.15
SECOND_IN_HOUR: int = 3600
MM_IN_M: int = 1000


def is_number(number: str) -> float:
    """Проверка на число."""
    while True:
        try:
            return float(number)
        except ValueError:
            number = input('Неправильный ввод. Введите заново: ')


def is_true(answer: str) -> bool:
    """Булево значение ответа."""
    while True:
        if answer.lower() in ('да', 'yes'):
            return True
        elif answer.lower() in ('нет', 'no'):
            return False
        else:
            answer = input('Неправильный ввод. Введите заново: ')


def get_fluid_cas_number(fluid: str) -> str:
    """Получение уникального численного идентификатора химических соединений (СAS)."""
    fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    while fluid_cas_number is None:
        fluid = input('Рабочая среда не найдена. Повторите ввод: ').lower()
        fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    return fluid_cas_number


def get_fluid_properties(cas_number: str, pressure: float, temperature: float) -> dict:
    """Получение термодинамических свойств рабочей жидкости."""
    url: str = 'https://webbook.nist.gov/cgi/fluid.cgi'
    params: dict = {
        'Action': 'Data',
        'Wide': 'On',
        'ID': cas_number,
        'Type': 'IsoTherm',
        'Digits': '5',
        'PLow': str(pressure),
        'PHigh': str(pressure),
        'PInc': '1',
        'T': str(temperature),
        'RefState': 'DEF',
        'TUnit': 'K',
        'PUnit': 'bar',
        'DUnit': 'kg%2Fm3',
        'HUnit': 'kJ%2Fkg',
        'WUnit': 'm%2Fs',
        'VisUnit': 'uPa*s',
        'STUnit': 'N%2Fm',
    }
    try:
        # Запрос сразу преобразуем в список из строк.
        response: list = requests.get(url, params=params).text.split()
        # В запросе значения параметров начинаются с 30 номера.
        # Все значения преобразуем во float и добавим в property_values.
        property_values = list(map(float, response[30:-1:1]))
        # Последним в списке идет фазовое состояние. Просто добавим его.
        property_values.append(response[-1])
        # Создадим словарь с термодинамическими свойствами.
        thermodynamic_properties = dict()
        for index in range(len(PROPERTIES_NAMES)):
            thermodynamic_properties.update({PROPERTIES_NAMES[index]: property_values[index]})
        return thermodynamic_properties
    except Exception as error:
        print(f'Произошла ошибка: {error}')
        input('Нажмите клавишу Enter, чтобы выйти из программы.')
        sys.exit()


def get_mass_flow_rate(normal_density: float, flag: bool) -> float:
    """Получение значения массового расхода в зависимости от ответа."""
    if flag:
        normal_flow_rate: float = is_number(input('Введите расход при нормальных условиях (нм3/ч): '))
        return normal_flow_rate * normal_density
    return is_number(input('Введите массовый расход (кг/ч): '))


def get_temperature(flag: bool, pipe_branch: str) -> float:
    """Получение значения температуры в зависимости от ответа."""
    if flag:
        return is_number(input(f'Введите значение температуры на {pipe_branch}е (°С): ')) + NORMAL_TEMPERATURE
    return is_number(input(f'Введите значение температуры на {pipe_branch}е (K): '))


def calc_electric_power(mass_flow_rate: float, enthalpy_difference: float) -> Tuple[float, float]:
    """Расчет электрической мощности нагревателя."""
    electric_power: float = round(mass_flow_rate * enthalpy_difference / SECOND_IN_HOUR, 1)
    electric_power_30: float = round(electric_power * 1.3, 1)
    return electric_power, electric_power_30


def get_nominal_diameter(mass_flow_rate: float, density: float, phase: str) -> float:
    """Получение значения номинального диаметра для патрубка нагревателя."""
    velocity: int = LIQUID_VELOCITY if phase == 'liquid' else GAS_VELOCITY
    cross_sectional_area: float = mass_flow_rate / (velocity * density) * MM_IN_M ** 2 / SECOND_IN_HOUR
    diameter: float = (4 * cross_sectional_area / pi) ** 0.5
    for index in range(len(DIAMETER_NOMINAL)):
        if DIAMETER_NOMINAL[index] < diameter <= DIAMETER_NOMINAL[index + 1]:
            diameter = DIAMETER_NOMINAL[index + 1]
            break
    return diameter


def calc_velocity(diameter: float, mass_flow_rate: float, density: float) -> float:
    """Расчет скорости потока."""
    cross_sectional_area: float = pi * diameter ** 2 / (4 * MM_IN_M ** 2)
    volumetric_flow_rate: float = mass_flow_rate / density
    velocity: float = volumetric_flow_rate / (cross_sectional_area * SECOND_IN_HOUR)
    return round(velocity, 1)


def print_parameters(electric_power: float, electric_power_30: float, nominal_diameter: float, velocity: float) -> None:
    """Печатает параметры нагревателя."""
    print(f'Необходимая мощность нагревателя равна: {electric_power} кВт.')
    print(f'Мощность с запасом 30% равна: {electric_power_30} кВт.')
    print(f'Номинальный диаметр патрубка: DN{nominal_diameter}')
    print(f'Скорость рабочей среды на выходе: {velocity} м/с.')


def get_phase(answer: str) -> str:
    """Возвращает фазовое состояние на английском, как указано в GET запросе."""
    while True:
        if answer.lower() == 'газ':
            return 'vapor'
        elif answer.lower() == 'жидкость':
            return 'liquid'
        else:
            answer = input('Неправильный ввод. Введите заново: ')


def main():
    """Главная функция."""
    fluid: str = input('Введите название рабочей среды: ').lower()
    cas_number: str = get_fluid_cas_number(fluid)

    normal_thermodynamic_properties: dict = get_fluid_properties(cas_number, NORMAL_PRESSURE, NORMAL_TEMPERATURE)
    normal_density: float = normal_thermodynamic_properties.get('Density')

    pressure: float = is_number(input('Введите значение давления (бар): '))

    flag: bool = is_true(input('Температура в Цельсиях? (да/нет): '))
    temperature_inlet: float = get_temperature(flag, 'вход')
    thermodynamic_properties_inlet: dict = get_fluid_properties(cas_number, pressure, temperature_inlet)
    temperature_outlet: float = get_temperature(flag, 'выход')
    thermodynamic_properties_outlet: dict = get_fluid_properties(cas_number, pressure, temperature_outlet)
    density_outlet: float = thermodynamic_properties_outlet.get('Density')
    phase_outlet: str = thermodynamic_properties_outlet.get('Phase')

    flag: bool = is_true(input('Значение расхода при нормальных условиях? (да/нет): '))
    mass_flow_rate: float = get_mass_flow_rate(normal_density, flag)

    enthalpy_inlet: float = thermodynamic_properties_inlet.get('Enthalpy')
    enthalpy_outlet: float = thermodynamic_properties_outlet.get('Enthalpy')
    enthalpy_difference: float = enthalpy_outlet - enthalpy_inlet

    electric_power, electric_power_30 = calc_electric_power(mass_flow_rate, enthalpy_difference)

    nominal_diameter: float = get_nominal_diameter(mass_flow_rate, density_outlet, phase_outlet)
    velocity: float = calc_velocity(nominal_diameter, mass_flow_rate, density_outlet)

    print_parameters(electric_power, electric_power_30, nominal_diameter, velocity)


def calc_unknown_fluid():
    """Расчет неизвестной рабочей среды."""
    phase: str = get_phase(input('Это газ или жидкость? (газ/жидкость): '))

    enthalpy_inlet: float = is_number(input('Введите значение энтальпии на входе (кДж/кг): '))
    enthalpy_outlet: float = is_number(input('Введите значение энтальпии на выходе (кДж/кг): '))
    enthalpy_difference: float = enthalpy_outlet - enthalpy_inlet

    normal_density: float = is_number(input('Введите значение плотности при нормальных условиях (кг/м3): '))
    density_outlet: float = is_number(input('Введите значение плотности на выходе (кг/м3): '))

    flag: bool = is_true(input('Значение расхода при нормальных условиях? (да/нет): '))
    mass_flow_rate: float = get_mass_flow_rate(normal_density, flag)

    electric_power, electric_power_30 = calc_electric_power(mass_flow_rate, enthalpy_difference)

    nominal_diameter: float = get_nominal_diameter(mass_flow_rate, density_outlet, phase)
    velocity: float = calc_velocity(nominal_diameter, mass_flow_rate, density_outlet)

    print_parameters(electric_power, electric_power_30, nominal_diameter, velocity)


if __name__ == '__main__':
    while True:
        print(f'Вот какие рабочие среды я знаю:', end=' ')
        print(*CAS_REGISTRY_NUMBERS.keys(), sep=', ')
        if is_true(input('Ваша рабочая среда есть в списке? (да/нет): ')):
            main()
        else:
            calc_unknown_fluid()
        if not is_true(input('Хотите еще раз выполнить расчет? (да/нет): ')):
            input('Нажмите клавишу Enter, чтобы выйти из программы.')
            sys.exit()
