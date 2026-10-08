import httpx
from typing import Optional, Dict, Any, List

class GraphQLClient:
    def __init__(self, graphql_url: str):
        self.graphql_url = graphql_url

    def _execute(self, token: str, query: str, variables: Optional[Dict[str, Any]] = None) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        with httpx.Client() as client:
            response = client.post(self.graphql_url, json=payload, headers=headers)
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                try:
                    return {"error": str(e), "details": response.json()}
                except:
                    return {"error": str(e), "details": response.text}

    # ─── Employee ────────────────────────────────────────────────────────────────

    def get_me(self, token: str) -> dict:
        """Get the currently authenticated employee's profile"""
        query = """
        query GetMe {
          me {
            employeeId
            fullName
            email
            jobTitle
            departmentName
            departmentCode
            employmentType
            startDate
            probationEndDate
            managerId
            status
          }
        }
        """
        return self._execute(token, query)

    def get_employee_profile(self, token: str, employee_id: str) -> dict:
        """Get a specific employee's profile by ID (HR role)"""
        query = """
        query GetAllEmployees {
          allEmployees {
            employeeId
            fullName
            email
            jobTitle
            departmentName
            departmentCode
            employmentType
            startDate
            probationEndDate
            managerId
            status
          }
        }
        """
        res = self._execute(token, query)
        if "error" in res:
            return res
        employees = res.get("data", {}).get("allEmployees", [])
        found = next((e for e in employees if e["employeeId"] == employee_id), None)
        return {"data": {"employee": found}}

    def get_all_employees(self, token: str) -> dict:
        """Get all employees (HR role)"""
        query = """
        query GetAllEmployees {
          allEmployees {
            employeeId
            fullName
            email
            jobTitle
            departmentName
            departmentCode
            employmentType
            startDate
            status
          }
        }
        """
        return self._execute(token, query)

    # ─── Available Days ──────────────────────────────────────────────────────────

    def get_my_available_days(self, token: str) -> dict:
        """Get remaining leave days for the current employee"""
        query = """
        query GetMyAvailableDays {
          myAvailableDays {
            employeeId
            leaveType
            availableDays
          }
        }
        """
        return self._execute(token, query)

    def get_employee_available_days(self, token: str, employee_id: str) -> dict:
        """Get remaining leave days for a specific employee (HR role)"""
        query = """
        query GetEmployeeAvailableDays($id: String!) {
          employeeAvailableDays(employeeId: $id) {
            employeeId
            leaveType
            availableDays
          }
        }
        """
        return self._execute(token, query, {"id": employee_id})

    def get_all_employee_available_days(self, token: str) -> dict:
        """Get remaining leave days for all employees (HR role)"""
        query = """
        query GetAllEmployeeAvailableDays {
          allEmployeeAvailableDays {
            employeeId
            leaveType
            availableDays
          }
        }
        """
        return self._execute(token, query)

    # ─── Entitlements ────────────────────────────────────────────────────────────

    def get_my_leave_entitlements(self, token: str) -> dict:
        """Get the annual leave entitlement (limit) for the current employee"""
        query = """
        query GetMyLeaveEntitlements {
          myLeaveEntitlements {
            employeeId
            year
            leaveType
            entitledDays
            carriedOverDays
          }
        }
        """
        return self._execute(token, query)

    def get_employee_leave_entitlements(self, token: str, employee_id: str) -> dict:
        """Get the annual leave entitlement for a specific employee (HR role)"""
        query = """
        query GetEmployeeLeaveEntitlements($id: String!) {
          employeeLeaveEntitlements(employeeId: $id) {
            employeeId
            year
            leaveType
            entitledDays
            carriedOverDays
          }
        }
        """
        return self._execute(token, query, {"id": employee_id})

    def get_all_leave_entitlements(self, token: str) -> dict:
        """Get leave entitlements for all employees (HR role)"""
        query = """
        query GetAllLeaveEntitlements {
          allLeaveEntitlements {
            employeeId
            year
            leaveType
            entitledDays
            carriedOverDays
          }
        }
        """
        return self._execute(token, query)

    def filter_leave_entitlements(self, token: str, leave_type: Optional[str] = None, employee_id: Optional[str] = None) -> dict:
        """Filter leave entitlements by type and/or employee (HR role)"""
        query = """
        query FilterLeaveEntitlements($type: LEAVE_TYPE, $employeeId: String) {
          leaveEntitlementsFilter(type: $type, employeeId: $employeeId) {
            employeeId
            year
            leaveType
            entitledDays
            carriedOverDays
          }
        }
        """
        variables = {}
        if leave_type:
            variables["type"] = leave_type
        if employee_id:
            variables["employeeId"] = employee_id
        return self._execute(token, query, variables or None)

    # ─── Leave Requests ──────────────────────────────────────────────────────────

    def get_my_leave_requests(self, token: str, status: Optional[str] = None) -> dict:
        """Get the current employee's leave requests"""
        query = """
        query GetMyLeaveRequests {
          myLeaveRequests {
            id
            leaveType
            startDate
            endDate
            days
            status
            comment
            createdVia
            createdAt
          }
        }
        """
        res = self._execute(token, query)
        if status and "error" not in res:
            reqs = res.get("data", {}).get("myLeaveRequests", [])
            res["data"]["myLeaveRequests"] = [r for r in reqs if r.get("status") == status]
        return res

    def get_all_employee_leave_requests(self, token: str) -> dict:
        """Get all employees' leave requests (HR role)"""
        query = """
        query GetAllEmployeeLeaveRequests {
          allEmployeeLeaveRequests {
            id
            employeeId
            leaveType
            startDate
            endDate
            days
            status
            comment
            createdVia
            createdAt
          }
        }
        """
        return self._execute(token, query)

    def find_employee_leave_requests(self, token: str, employee_id: str, status: Optional[str] = None) -> dict:
        """Find leave requests for a specific employee with optional status filter (HR role)"""
        query = """
        query FindEmployeeLeaveRequests($id: String, $status: [LEAVE_REQUEST_STATUS!]) {
          employeeLeaveRequestsFinder(employeeId: $id, leaveRequestStatuses: $status) {
            id
            employeeId
            leaveType
            startDate
            endDate
            days
            status
            comment
            createdVia
            createdAt
          }
        }
        """
        variables: Dict[str, Any] = {"id": employee_id}
        if status:
            variables["status"] = [status]
        return self._execute(token, query, variables)

    # ─── Leave Types & Holidays ──────────────────────────────────────────────────

    def get_holidays(self, token: str) -> dict:
        """Get official holidays"""
        query = """
        query GetHolidays {
          holidays {
            date
            name
          }
        }
        """
        return self._execute(token, query)

    def get_leave_types(self, token: str) -> dict:
        """Get available leave types and their rules"""
        query = """
        query GetLeaveTypes {
          leaveTypes {
            leaveTypes
            name
            dayUnit
            annualLimitDays
            selfService
            assistantSupported
            policyReference
          }
        }
        """
        return self._execute(token, query)
