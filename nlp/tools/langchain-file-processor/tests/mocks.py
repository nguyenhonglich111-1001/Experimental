import sys
from unittest.mock import MagicMock

def mock_streamlit():
    """
    Mocks the Streamlit module and its functions to avoid errors during testing.
    """
    st_mock = MagicMock()
    st_mock.cache_data = lambda func: func
    st_mock.cache_resource = lambda func: func
    sys.modules["streamlit"] = st_mock
