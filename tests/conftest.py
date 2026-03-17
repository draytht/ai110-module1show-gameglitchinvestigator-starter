"""
Conftest: mock the entire streamlit module before any test file imports app.py.
app.py runs st.* calls at module level, so we need a fully configured mock
to prevent runtime errors during import.
"""
import os
import sys
from unittest.mock import MagicMock

# Allow `from app import ...` to work when pytest is run from inside tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_st = MagicMock()

# sidebar.selectbox must return a real string so dict lookups work
_st.sidebar.selectbox.return_value = "Normal"

# st.columns(3) must unpack into exactly 3 values
_st.columns.return_value = (MagicMock(), MagicMock(), MagicMock())

# session_state needs to support `"key" not in st.session_state` and attribute assignment
_session = MagicMock()
_session.__contains__ = MagicMock(return_value=False)
_st.session_state = _session

sys.modules["streamlit"] = _st
