"""Dataset_scalyr_query tool for MCP server.
"""

import os
import json
from typing import Optional, Any
import urllib.request
import urllib.error

from mcp.types import ToolAnnotations

from core.server import mcp
from core.utils import get_tool_config


@mcp.tool(
    annotations=ToolAnnotations(
        title="Dataset_scalyr_query",
        readOnlyHint=True,
    ),
)
def dataset_scalyr_query(
    filter: str,
    start_time: str = "4h",
    end_time: str = "0h",
    max_count: int = 100,
    columns: str = "",
    continuation_token: Optional[str] = None,
) -> dict[str, Any]:
    """Query Scalyr logs API.

    Args:
        filter: Events to match, using the same syntax as the Expression field in the query UI. (e.g., "Environment = 'staging' Project = 'backend'" AccountGroup = 'product' 'error')
        
        start_time: Start time for the query. You can also supply a simple timestamp, measured in seconds, milliseconds, or nanoseconds since 1/1/1970. (default: "4h")
        
        end_time: End time for the query. You can also supply a simple timestamp, measured in seconds, milliseconds, or nanoseconds since 1/1/1970. (default: "0h")
        
        max_count: Maximum number of records to return. You may specify a value from 1 to 5000. (default: 100)
        
        columns: [Optional] fields to return for each log message, as a comma-delimited list. e.g "timestamp,message" (default: "", which returns all columns)

        continuation_token: [Optional] is used to page through result sets larger than max_count. Omit this parameter for your first query. You may then repeat the query with the same filter, start_time and end_time to retrieve further matches. Each time, set continuation_token to the value returned by the previous query. When using continuation_token, you should set start_time and end_time to absolute values, not relative values such as 4h. If you use relative time values, and the time range drifts so that the continuation token refers to an event that falls outside the new time range, the query will fail.

    Returns:
        dict: Parsed JSON response from Scalyr API
    """
    # Get Scalyr API token from environment variable
    token = os.environ.get("SCALYR_API_TOKEN")
    if not token:
        return {
            "error": "SCALYR_API_TOKEN environment variable not set"
        }

    # Prepare the API request body
    body = {
        "token": token,
        "queryType": "log",
        "filter": filter,
        "startTime": start_time,
        "endTime": end_time,
        "maxCount": max_count,
        "columns": columns,
    }
    
    # Add continuation token if provided
    if continuation_token:
        body["continuationToken"] = continuation_token

    # Make the API request
    url = "https://app.scalyr.com/api/query"
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_details = json.loads(error_body)
        except:
            error_details = error_body
        return {
            "error": f"HTTP {e.code}: {e.reason}",
            "details": error_details
        }
    except urllib.error.URLError as e:
        return {
            "error": f"URL Error: {e.reason}"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}"
        }
