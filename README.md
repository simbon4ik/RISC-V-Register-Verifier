# RISC-V Register Verifier (МИФИ–YADRO)

Командная задача по верификации регистрового блока RISC-V SoC от YADRO.  
Получен «чёрный ящик» — реальный RTL‑блок регистров, доступный только через Python‑API, и по SystemRDL‑спецификации строим тестплан, находим баги и показываем результат на дашборде.

## Постановка задачи

DUT: `RISC_V_REG_BLOCK` — регистровый файл RISC-V периферии YADRO, RTL под NDA.
Интерфейс доступа из Python:

```python
def riscv_reg_access(addr: int, data: int, rw: str, bus_width: int = 32) -> dict:
    """
    DUT: RISC-V Register File Block (МИФИ-Ядро)
    addr: 0x0000-0xFFFF (SystemRDL spec)
    rw: 'read' / 'write'

    return: {'reg_value': int, 'status': str, 'ack': bool}
    """
```
Диапазон адресов: 0x0000–0xFFFF (по SystemRDL‑спецификации).

Известные баги (которые нужно поймать)
- Register Misread: addr = 0x0042 → stale data (FSM не обновляет значение).
- Bus Deadlock: write(0x0013) → read(0x0077) без ACK (зависание шины/ФСМ).
- Glitch: bus_width = 64 на 32‑битном адресном пространстве → переполнение/обрезка данных.

## Цели и метрики
Задача — по методике YADRO: 
- тестплан по SystemRDL,
- покрытие
- багрепорт.

Цели:
- Register Coverage: протестировать ≥ 94% доступных регистров.
- Transition Coverage: покрыть ≥ 89% read/write‑последовательностей (переходов).
- Bugs Reported: обнаружить 3/3 известных багов с воспроизводимыми тестами и severity.
- Code quality: pylint score ≥ 8.5/10, адекватная структура и регрессия через pytest.

## Роли и этапы

Test Sequencer Engineer:
- Парсит SystemRDL.
- Генерирует random/directed тесты по всем адресам (до 65k обращений).
- Обеспечивает покрытие регистров ≥ 94%.

Coverage Engineer:
- Считает покрытие регистров и переходов read→write.
- Строит/анализирует FSM на основе наблюдаемого поведения (networkx).
- Формализует триггеры для багов.

Verification GUI Engineer
- Делает Streamlit‑дашборд.
- Heatmap по регистрах (покрытие/статус).
- Граф FSM (networkx + Plotly), отображение deadlock‑состояний.

## Технологический стек

Python 3.x
systemrdl-compiler — парсинг SystemRDL‑спецификации регистров.
pytest, pytest-cov — тесты и покрытие.
networkx — построение FSM и анализ графа.
streamlit + plotly — верификационный GUI (heatmap, FSM‑граф).

## Установка и виртуальное окружение
Клонирование репозитория
```bash
git clone <url>
cd <project_nam>
```
Создание и активация виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
