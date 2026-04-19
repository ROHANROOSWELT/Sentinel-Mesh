from backend.models import ToolCall
import json

TOOL_REGISTRY = {
    "read_email": lambda args: {
        "emails": [
            {"from": "alice@company.com", "subject": "Q3 Review", "date": "2025-04-15", "preview": "Please find attached..."},
            {"from": "bob@company.com", "subject": "Meeting tomorrow", "date": "2025-04-16", "preview": "Can we push to 3pm?"},
            {"from": "carol@company.com", "subject": "Budget approval", "date": "2025-04-17", "preview": "Approved for Q4."},
        ],
        "count": 3,
        "date_range": args.get("date_range", "last 7 days")
    },
    "summarise": lambda args: f"Summary: {str(args.get('content', ''))[:200]}...",
    "forward_email": lambda args: f"Email forwarded to {args.get('to', 'unknown')}",
    "delete_email": lambda args: f"Email {args.get('id', 'unknown')} deleted",
    "query_database": lambda args: {
        "rows": [
            {"id": 1, "metric": "Q3 Revenue", "value": "$2.4M", "note": "Above target"},
            {"id": 2, "metric": "Q3 Costs", "value": "$1.8M", "note": "Within budget"},
        ],
        "query": args.get("query", "SELECT *"),
        "row_count": 2
    },
    "write_file": lambda args: f"File written: {args.get('path', 'output.txt')}",
    "send_http_request": lambda args: f"HTTP {args.get('method','GET')} to {args.get('url','unknown')}",
    "read_file": lambda args: f"File contents of {args.get('path', 'unknown')}: [content here]",
}

class ToolResult:
    def __init__(self, success: bool, was_allowed: bool, output: str, tool_name: str):
        self.success = success
        self.was_allowed = was_allowed
        self.output = output
        self.tool_name = tool_name

class WorkerAgent:
    def __init__(self, permitted_tools: list[str]):
        self.permitted_tools = permitted_tools
    
    def execute(self, tool_call: ToolCall) -> ToolResult:
        if tool_call.tool_name not in self.permitted_tools:
            return ToolResult(success=False, was_allowed=False,
                            output=f"BLOCKED: {tool_call.tool_name} not in session whitelist",
                            tool_name=tool_call.tool_name)
        fn = TOOL_REGISTRY.get(tool_call.tool_name)
        if not fn:
            return ToolResult(success=False, was_allowed=True,
                            output=f"Unknown tool: {tool_call.tool_name}",
                            tool_name=tool_call.tool_name)
        result = fn(tool_call.args)
        return ToolResult(success=True, was_allowed=True,
                        output=json.dumps(result) if isinstance(result, dict) else str(result),
                        tool_name=tool_call.tool_name)
