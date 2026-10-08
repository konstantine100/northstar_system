import httpx
from typing import Optional

class RestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                return {"error": str(e), "details": response.json()}
            except:
                return {"error": str(e), "details": response.text}

    def login(self, email: str, employee_id: str) -> dict:
        url = f"{self.base_url}/auth/login"
        payload = {"email": email, "employeeId": employee_id}
        with httpx.Client() as client:
            return self._handle_response(client.post(url, json=payload))

    def create_leave_request(self, token: str, leave_type: str, start_date: str, end_date: str, comment: Optional[str] = None) -> dict:
        url = f"{self.base_url}/leave-request/hr-assistant-create-leave-request"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "leaveType": leave_type,
            "startDate": start_date,
            "endDate": end_date,
            "comment": comment or ""
        }
        with httpx.Client() as client:
            return self._handle_response(client.post(url, json=payload, headers=headers))
            
    def cancel_leave_request(self, token: str, request_id: int) -> dict:
        url = f"{self.base_url}/leave-request/cancel-request/{request_id}"
        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client() as client:
            return self._handle_response(client.put(url, headers=headers))

    def answer_leave_request(self, token: str, employee_id: str, request_id: int, is_accepted: bool, message: str) -> dict:
        url = f"{self.base_url}/leave-request/answer-request"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "employeeId": employee_id,
            "requestId": request_id,
            "isAccepted": is_accepted,
            "message": message
        }
        with httpx.Client() as client:
            return self._handle_response(client.put(url, json=payload, headers=headers))
