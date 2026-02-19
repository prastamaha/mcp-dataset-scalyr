"""Tests for dataset_scalyr_query tool."""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError
import pytest

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.dataset_scalyr_query import dataset_scalyr_query as dataset_scalyr_query_tool

# Get the actual function from the FunctionTool wrapper
dataset_scalyr_query = dataset_scalyr_query_tool.fn

class TestDatasetScalyrQuery:
    """Test the dataset_scalyr_query tool."""

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_successful_query(self, mock_urlopen: MagicMock) -> None:
        """Test successful API query."""
        # Mock API response
        mock_response_data = {
            "status": "success",
            "matches": [
                {
                    "timestamp": "1234567890",
                    "message": "Test log message",
                    "severity": "INFO"
                }
            ],
            "continuationToken": "next-token-456"
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call the function
        result = dataset_scalyr_query(
            filter="Environment = 'staging' Project = 'backend'"
        )

        # Verify result
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert len(result["matches"]) == 1
        assert "continuationToken" in result

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_token(self) -> None:
        """Test behavior when API token is missing."""
        result = dataset_scalyr_query(filter="test filter")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "SCALYR_API_TOKEN" in result["error"]

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_query_with_custom_parameters(self, mock_urlopen: MagicMock) -> None:
        """Test query with custom parameters."""
        mock_response_data = {"status": "success", "matches": []}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call with custom parameters
        result = dataset_scalyr_query(
            filter="error",
            start_time="1h",
            end_time="0h",
            max_count=200,
            columns="timestamp,message,severity",
            continuation_token="token-123"
        )

        # Verify the request was made
        assert mock_urlopen.called
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        
        # Verify request body
        request_body = json.loads(request.data.decode("utf-8"))
        assert request_body["filter"] == "error"
        assert request_body["startTime"] == "1h"
        assert request_body["endTime"] == "0h"
        assert request_body["maxCount"] == 200
        assert request_body["columns"] == "timestamp,message,severity"
        assert request_body["continuationToken"] == "token-123"
        assert request_body["queryType"] == "log"
        assert request_body["token"] == "test-token-123"

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_query_with_default_parameters(self, mock_urlopen: MagicMock) -> None:
        """Test query with default parameters."""
        mock_response_data = {"status": "success"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call with only required parameter
        result = dataset_scalyr_query(filter="test")

        # Verify the request
        request = mock_urlopen.call_args[0][0]
        request_body = json.loads(request.data.decode("utf-8"))
        
        # Check default values
        assert request_body["startTime"] == "4h"
        assert request_body["endTime"] == "0h"
        assert request_body["maxCount"] == 100
        assert request_body["columns"] == ""
        assert "continuationToken" not in request_body

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_http_error_handling(self, mock_urlopen: MagicMock) -> None:
        """Test handling of HTTP errors."""
        # Create mock HTTP error
        error_response = {"message": "Invalid query", "code": "BAD_REQUEST"}
        
        # Create a proper mock for the error's file pointer
        mock_fp = MagicMock()
        mock_error = HTTPError(
            url="https://app.scalyr.com/api/query",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=mock_fp
        )
        # Set up the read method to return the error response
        mock_error.read = MagicMock(return_value=json.dumps(error_response).encode("utf-8"))
        mock_error.fp = mock_fp  # Ensure fp attribute is set
        
        mock_urlopen.side_effect = mock_error

        # Call the function
        result = dataset_scalyr_query(filter="invalid")

        # Verify error handling
        assert isinstance(result, dict)
        assert "error" in result
        assert "HTTP 400" in result["error"]
        assert "details" in result
        assert isinstance(result["details"], dict)
        assert result["details"]["code"] == "BAD_REQUEST"

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_url_error_handling(self, mock_urlopen: MagicMock) -> None:
        """Test handling of URL errors (network issues)."""
        mock_urlopen.side_effect = URLError("Network unreachable")

        result = dataset_scalyr_query(filter="test")

        assert isinstance(result, dict)
        assert "error" in result
        assert "URL Error" in result["error"]

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_unexpected_error_handling(self, mock_urlopen: MagicMock) -> None:
        """Test handling of unexpected errors."""
        mock_urlopen.side_effect = Exception("Unexpected error occurred")

        result = dataset_scalyr_query(filter="test")

        assert isinstance(result, dict)
        assert "error" in result
        assert "Unexpected error" in result["error"]

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_api_endpoint_and_headers(self, mock_urlopen: MagicMock) -> None:
        """Test that correct endpoint and headers are used."""
        mock_response_data = {"status": "success"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        dataset_scalyr_query(filter="test")

        # Verify the request
        request = mock_urlopen.call_args[0][0]
        
        # Check URL
        assert request.full_url == "https://app.scalyr.com/api/query"
        
        # Check headers
        assert request.headers["Content-type"] == "application/json"
        
        # Check method
        assert request.method == "POST"

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_returns_dict_not_string(self, mock_urlopen: MagicMock) -> None:
        """Test that the function returns a dict, not a JSON string."""
        mock_response_data = {"status": "success", "data": [1, 2, 3]}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = dataset_scalyr_query(filter="test")

        # Must be a dict, not a string
        assert isinstance(result, dict)
        assert not isinstance(result, str)
        assert result["status"] == "success"
        assert result["data"] == [1, 2, 3]

    @patch.dict("os.environ", {"SCALYR_API_TOKEN": "test-token-123"})
    @patch("urllib.request.urlopen")
    def test_returns_dict_not_string(self, mock_urlopen: MagicMock) -> None:
        """Test handling error_body that is not valid JSON."""
        mock_fp = MagicMock()
        mock_error = HTTPError(
            url="https://app.scalyr.com/api/query",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=mock_fp
        )
        mock_error.read = MagicMock(return_value=b"Non-JSON error response")
        mock_error.fp = mock_fp
        
        mock_urlopen.side_effect = mock_error

        result = dataset_scalyr_query(filter="test")

        assert isinstance(result, dict)
        assert "error" in result
        assert "HTTP 500" in result["error"]
        assert "details" in result
        assert result["details"] == "Non-JSON error response"  
      