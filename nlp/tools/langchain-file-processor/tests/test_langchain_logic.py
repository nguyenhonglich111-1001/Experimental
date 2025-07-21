import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
from langchain_chroma import Chroma

# Mock streamlit before importing the function to be tested
from tests.mocks import mock_streamlit
mock_streamlit()

from app.langchain_logic import delete_file


class TestDeleteFile(unittest.TestCase):

    @patch("app.langchain_logic.os.remove")
    @patch("app.langchain_logic.os.path.exists")
    @patch("app.langchain_logic.Chroma")
    def test_delete_file_success(self, MockChroma, mock_os_exists, mock_os_remove):
        """
        Tests the successful deletion of a file.
        """
        # Arrange
        mock_vectorstore_instance = MockChroma.return_value
        mock_vectorstore_instance.get.return_value = {"ids": ["id1", "id2"]}
        
        file_path = "/fake/path/to/document.pdf"
        mock_os_exists.return_value = True

        # Act
        result = delete_file(mock_vectorstore_instance, file_path)

        # Assert
        mock_os_exists.assert_called_once_with(file_path)
        mock_vectorstore_instance.get.assert_called_once_with(where={"source": file_path})
        mock_vectorstore_instance.delete.assert_called_once_with(ids=["id1", "id2"])
        mock_os_remove.assert_called_once_with(file_path)
        self.assertTrue(result)

    @patch("app.langchain_logic.os.path.exists")
    def test_delete_file_not_found(self, mock_os_exists):
        """
        Tests the case where the file to be deleted does not exist.
        """
        # Arrange
        mock_vectorstore = MagicMock(spec=Chroma)
        file_path = "/fake/path/to/non_existent_document.pdf"
        mock_os_exists.return_value = False

        # Act
        result = delete_file(mock_vectorstore, file_path)

        # Assert
        mock_os_exists.assert_called_once_with(file_path)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
