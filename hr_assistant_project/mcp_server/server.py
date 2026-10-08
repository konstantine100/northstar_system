from mcp.server.mcpserver import MCPServer
from typing import Optional
from config import REST_URL, GRAPHQL_URL
from rest_client import RestClient
from graphql_client import GraphQLClient

mcp = MCPServer("HRAssistant")
rest_client = RestClient(REST_URL)
graphql_client = GraphQLClient(GRAPHQL_URL)

# ─── Auth ────────────────────────────────────────────────────────────────────

@mcp.tool()
def login_user(email: str, employee_id: str) -> dict:
    """Login a user and get authentication token"""
    return rest_client.login(email, employee_id)

# ─── Employee ────────────────────────────────────────────────────────────────

@mcp.tool()
def get_me(token: str) -> dict:
    """Get the currently authenticated employee's own profile"""
    return graphql_client.get_me(token)

@mcp.tool()
def get_employee_profile(token: str, employee_id: str) -> dict:
    """Get a specific employee's profile by ID (HR role required)"""
    return graphql_client.get_employee_profile(token, employee_id)

@mcp.tool()
def get_all_employees(token: str) -> dict:
    """Get all employees in the company (HR role required)"""
    return graphql_client.get_all_employees(token)

# ─── Available Days ──────────────────────────────────────────────────────────

@mcp.tool()
def get_my_available_days(token: str) -> dict:
    """Get remaining leave days for the current employee"""
    return graphql_client.get_my_available_days(token)

@mcp.tool()
def get_employee_available_days(token: str, employee_id: str) -> dict:
    """Get remaining leave days for a specific employee (HR role required)"""
    return graphql_client.get_employee_available_days(token, employee_id)

@mcp.tool()
def get_all_employee_available_days(token: str) -> dict:
    """Get remaining leave days for all employees (HR role required)"""
    return graphql_client.get_all_employee_available_days(token)

# ─── Entitlements ────────────────────────────────────────────────────────────

@mcp.tool()
def get_my_leave_entitlements(token: str) -> dict:
    """Get the annual leave entitlement (limit) for the current employee"""
    return graphql_client.get_my_leave_entitlements(token)

@mcp.tool()
def get_employee_leave_entitlements(token: str, employee_id: str) -> dict:
    """Get the annual leave entitlement for a specific employee (HR role required)"""
    return graphql_client.get_employee_leave_entitlements(token, employee_id)

@mcp.tool()
def get_all_leave_entitlements(token: str) -> dict:
    """Get leave entitlements for all employees (HR role required)"""
    return graphql_client.get_all_leave_entitlements(token)

@mcp.tool()
def filter_leave_entitlements(token: str, leave_type: Optional[str] = None, employee_id: Optional[str] = None) -> dict:
    """Filter leave entitlements by type and/or employee (HR role required)"""
    return graphql_client.filter_leave_entitlements(token, leave_type, employee_id)

# ─── Leave Requests ──────────────────────────────────────────────────────────

@mcp.tool()
def get_my_leave_requests(token: str, status: Optional[str] = None) -> dict:
    """Get the current employee's own leave requests with optional status filter"""
    return graphql_client.get_my_leave_requests(token, status)

@mcp.tool()
def get_all_employee_leave_requests(token: str) -> dict:
    """Get all leave requests from all employees (HR role required)"""
    return graphql_client.get_all_employee_leave_requests(token)

@mcp.tool()
def find_employee_leave_requests(token: str, employee_id: str, status: Optional[str] = None) -> dict:
    """Find leave requests for a specific employee with optional status filter (HR role required)"""
    return graphql_client.find_employee_leave_requests(token, employee_id, status)

@mcp.tool()
def create_leave_request(token: str, leave_type: str, start_date: str, end_date: str, comment: Optional[str] = None) -> dict:
    """Create a new leave request for the current employee"""
    return rest_client.create_leave_request(token, leave_type, start_date, end_date, comment)

@mcp.tool()
def cancel_leave_request(token: str, request_id: int) -> dict:
    """Cancel a leave request by its ID"""
    return rest_client.cancel_leave_request(token, request_id)

@mcp.tool()
def answer_leave_request(token: str, employee_id: str, request_id: int, is_accepted: bool, message: str) -> dict:
    """Approve or reject a leave request (HR role required)"""
    return rest_client.answer_leave_request(token, employee_id, request_id, is_accepted, message)

# ─── Leave Types & Holidays ──────────────────────────────────────────────────

@mcp.tool()
def get_holidays(token: str) -> dict:
    """Get official holidays"""
    return graphql_client.get_holidays(token)

@mcp.tool()
def get_leave_types(token: str) -> dict:
    """Get available leave types and their rules"""
    return graphql_client.get_leave_types(token)

if __name__ == "__main__":
    mcp.run()
