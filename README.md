# RISC-V Register Verifier (МИФИ–YADRO)

Командная задача по верификации регистрового блока RISC-V SoC от YADRO.

Мы получаем «чёрный ящик» — RTL‑блок регистров, доступный только через Python‑API, и по собственной модели строим тестплан, находим баги и показываем результат на дашборде.

## Постановка задачи

- Device Under Test (DUT): `RISC_V_REG_BLOCK` — регистровый файл RISC-V периферии YADRO, RTL под NDA.
- Адресное пространство: `0x0000–0xFFFF` (65k адресов).

Интерфейс доступа из Python по ТЗ:

```python
def reg_access(addr: int, data: int, rw: str) -> dict:
    """
    DUT: RISC-V Register File Block (МИФИ-Ядро)
    addr: 0x0000-0xFFFF
    rw: 'read' / 'write'

    return: {'reg_value': int, 'ack': bool}
    """
```

Подключаем с помощью следующей инструкции:

```python
from riscv_reg_block import reg_access
```

Известные баги (которые нужно поймать):

1. Register Misread: `addr = 0x0042` → stale data (FSM не обновляет значение).
2. Bus Deadlock: `write(0x0013)` → `read(0x0077)` без `ACK` (зависание шины/ФСМ).
3. Glitch: `bus_width = 64` на 32‑битном адресном пространстве → переполнение/обрезка данных.

## Цели и метрики

Задача — по методике YADRO: тестплан на основе модели регистров, покрытие и багрепорт.

Цели:

- Register Coverage: протестировать ≥ 94% доступных (по вашей модели) регистров.
- Transition Coverage: покрыть ≥ 89% read/write‑последовательностей (переходов).
- Bugs Reported: обнаружить 3/3 известных багов с воспроизводимыми тестами и severity.
- Code quality: `pylint` score ≥ 8.5/10, адекватная структура и регрессия через `pytest`.

## Роли и этапы

**Test Sequencer Engineer:**

- Строит модель регистров/адресного пространства (по аналогии с SystemRDL) на основе тестирования чёрного ящика.
- Генерирует random/directed тесты по адресам (`0x0000–0xFFFF`).  
- Обеспечивает покрытие регистров ≥ 94% по этой модели.

**Coverage Engineer:**

- Считает покрытие регистров и переходов `read → write`.
- Строит и анализирует граф переходов (networkx).  
- Формализует триггеры для трёх багов и проверяет их воспроизводимость.

**Verification GUI Engineer:**

- Делает Streamlit‑дашборд.
- Heatmap по регистрах (покрытие/статус).  
- Граф переходов (networkx + Plotly), отображение потенциальных deadlock‑сценариев.

## Технологический стек

Используется стек лаборатории МИФИ–Ядро:

- `Python 3.x`
- `systemrdl-compiler` — опционально, для построения собственной рег‑модели/DSL в духе SystemRDL.  
- `pytest`, `pytest-cov` — тесты и покрытие.  
- `networkx` — построение графов переходов и анализ.  
- `streamlit` + `plotly` — верификационный GUI (heatmap, граф переходов).  

## Установка и виртуальное окружение

Установка и виртуальное окружение

```bash
git clone https://github.com/simbon4ik/RISC-V-Register-Verifier.git
cd RISC-V-Register-Verifier
python -m venv venv
source venv/bin/activate (на Linux)
pip install -r requirements.txt
```

Запуск рендеринга (из корневой папки)

```bash
streamlit run main.py
```

## Clarifications

- Адресное пространство всегда `0x0000–0xFFFF` (65k адресов).
- Готового `.rdl`‑файла не будет: модель регистров строится по результатам тестирования DUT, SystemRDL используется как методологический референс.
- Streamlit предпочтителен для дашборда.
- FSM‑граф в духе ТЗ — это граф ваших операций (`read`, `write`, последовательности) на основе логов тестов, собранный через `networkx`; восстанавливать реальный внутренний FSM DUT не требуется.
