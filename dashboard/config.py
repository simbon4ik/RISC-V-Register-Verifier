APP_TITLE = "RISC‑V Register Verifier Dashboard"
PAGE_LAYOUT = "wide"

REGION_SIZE_BYTES = 0x0008
REGISTER_SPACE_START = 0x0000
REGISTER_SPACE_END = 0x000F

TEST_MODES = ["Full regression", "Quick sanity"]

DEMO_EVENTS = [
    {"addr": 0x0042, "bug_type": "lock_after_other_reg"},
    {"addr": 0x0013, "bug_type": "lock_on_write_value"},
    {"addr": 0x0077, "bug_type": "lock_on_write_value"},
    {"addr": 0x0042, "bug_type": "overflow_xor_dead"},
    {"addr": 0x0102, "bug_type": "overflow_xor_dead"},
    {"addr": 0x1102, "bug_type": "overflow_xor_dead"},
    {"addr": 0x1102, "bug_type": "abcd"},
]

DEMO_BUGS = [
    {
        "addr": "0x0042",
        "type": "lock_after_other_reg",
        "trigger_pattern": "read after write",
    },
    {
        "addr": "0x0013",
        "type": "overflow_xor_dead",
        "trigger_pattern": "write 0x13",
    },
]

FSM_TITLE = "Register block FSM"

FSM_STATES = [
    "IDLE",
    "DECODE",
    "READ",
    "WRITE",
    "WAIT_ACK",
    "ERROR",
    "DEADLOCK",
]

FSM_TRANSITIONS = [
    ("IDLE", "DECODE", "req"),
    ("DECODE", "READ", "rw=read"),
    ("DECODE", "WRITE", "rw=write"),
    ("READ", "WAIT_ACK", "start_read"),
    ("WRITE", "WAIT_ACK", "start_write"),
    ("WAIT_ACK", "IDLE", "ack_ok"),
    ("WAIT_ACK", "ERROR", "addr_err"),
    ("WAIT_ACK", "DEADLOCK", "no_ack_timeout"),
    ("ERROR", "IDLE", "clear_err"),
    ("DEADLOCK", "IDLE", "reset"),
]

FSM_POSITIONS = {
    "IDLE": (0.0, 0.0),
    "DECODE": (1.0, 1.0),
    "READ": (2.0, 1.5),
    "WRITE": (2.0, 0.5),
    "WAIT_ACK": (3.0, 1.0),
    "ERROR": (3.0, -0.5),
    "DEADLOCK": (4.0, 1.0),
}

FSM_NODE_SIZE = 30
FSM_NODE_COLOR = "#1f77b4"
FSM_EDGE_COLOR = "gray"
FSM_EDGE_WIDTH = 2
FSM_FIG_HEIGHT = 400
FSM_MARGIN = dict(l=20, r=20, t=20, b=20)

SIDEBAR_HEADER = "Test runner"
SIDEBAR_MODE_LABEL = "Mode"
SIDEBAR_RUN_BUTTON = "Run tests"
SIDEBAR_RUN_MESSAGE = "Updated at"

KPI_LABEL_REGS_WITH_BUGS = "Registers with bugs"
KPI_LABEL_BUG_PATTERNS = "Bug patterns"
KPI_LABEL_BUGS_FOUND = "Bugs found"

BUGS_TABLE_TITLE = "Detected bugs"

REGION_HEATMAP_TITLE = "Bug pattern heatmap"
REGION_HEATMAP_X_TITLE = "Bug / anomaly type"
REGION_HEATMAP_Y_TITLE = "Address region"
REGION_HEATMAP_COLORBAR_TITLE = "Occurrences"
REGION_HEATMAP_COLOR_SCALE = "Viridis"
