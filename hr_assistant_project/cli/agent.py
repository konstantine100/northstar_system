import os
import json
import asyncio
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

class HRAssistantAgent:
    def __init__(self, api_key: str, mcp_server_script: str, rag_db_dir: str):
        self.client = genai.Client(api_key=api_key)
        self.mcp_server_script = mcp_server_script
        self.rag_db_dir = rag_db_dir
        self.chat = None
        self.session_context = None

    async def init(self, session_context):
        self.session_context = session_context
        
        import sys
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if base_dir not in sys.path:
            sys.path.append(base_dir)
            
        from rag.vector_store import VectorStore
        self.vector_store = VectorStore(self.rag_db_dir)

        import sys
        self.exit_stack = AsyncExitStack()
        server_params = StdioServerParameters(command=sys.executable, args=[self.mcp_server_script])
        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.mcp_session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.mcp_session.initialize()

    async def _handle_tool_call(self, function_name: str, args: dict) -> str:
        try:
            if function_name == "search_hr_policy":
                return self.vector_store.search_hr_policy(args.get("query", ""))
            else:
                # Always inject the JWT token from the session
                args["token"] = self.session_context.token
                res = await self.mcp_session.call_tool(function_name, args)
                if hasattr(res, 'content') and len(res.content) > 0:
                    return res.content[0].text
                return "{}"
        except Exception as e:
            return f"{{\"error\": \"Tool call failed: {str(e)}\"}}"

    async def send_message(self, text: str) -> str:
        if not self.chat:
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            self.chat = self.client.aio.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=f"შენ ხარ მკაცრად მხოლოდ შპს „ნორთსტარ სერვისეზი“-ს HR ასისტენტი. დღევანდელი თარიღია {current_date}. შენი ერთადერთი მიზანია HR-თან დაკავშირებული პროცესების მართვა და კომპანიის პოლიტიკაზე დაყრდნობით თანამშრომლებისთვის დეტალური და ამომწურავი ინფორმაციის მიწოდება. პასუხის გაცემისას დეტალურად აღწერე წესები და ახსენე კომპანიის სახელი. კატეგორიულად აკრძალულია სხვა თემებზე საუბარი (მაგ: ხუმრობები, კოდის დაწერა, ზოგადი კითხვები) და ასეთ კითხვებზე ზრდილობიანად თქვი უარი. ყოველთვის გამოიყენე RAG ძიება (`search_hr_policy`) პოლიტიკის წესების გასაგებად და აუცილებლად დაეყრდენი მხოლოდ ძიების შედეგად მიღებულ ინფორმაციას. შვებულების მოთხოვნის გაგზავნაზე, დამტკიცებაზე ან გაუქმებაზე წინასწარ ნუ იტყვი უარს; ყოველთვის სცადე შესაბამისი ფუნქციის გამოძახება და მხოლოდ API-ს პასუხის მიხედვით (მაგალითად თუ დააბრუნა შეცდომა) შეატყობინე მომხმარებელს სტატუსი.",
                    tools=[
                        types.Tool(
                            function_declarations=[
                                # ── RAG ──────────────────────────────────────────
                                types.FunctionDeclaration(
                                    name="search_hr_policy",
                                    description="Search HR policy documents using RAG. Use this for any policy or rules questions.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"query": types.Schema(type=types.Type.STRING, description="Search query in Georgian")},
                                        required=["query"]
                                    )
                                ),
                                # ── Employee ─────────────────────────────────────
                                types.FunctionDeclaration(
                                    name="get_me",
                                    description="Get the currently logged-in employee's own profile information.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="get_employee_profile",
                                    description="Get a specific employee's profile by their employee ID. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"employee_id": types.Schema(type=types.Type.STRING, description="The employee ID")},
                                        required=["employee_id"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="get_all_employees",
                                    description="Get a list of all employees in the company. Requires HR role.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                # ── Available Days ───────────────────────────────
                                types.FunctionDeclaration(
                                    name="get_my_available_days",
                                    description="Get the remaining (available) leave days for the current employee.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="get_employee_available_days",
                                    description="Get the remaining leave days for a specific employee. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"employee_id": types.Schema(type=types.Type.STRING, description="The employee ID")},
                                        required=["employee_id"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="get_all_employee_available_days",
                                    description="Get remaining leave days for all employees. Requires HR role.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                # ── Entitlements ─────────────────────────────────
                                types.FunctionDeclaration(
                                    name="get_my_leave_entitlements",
                                    description="Get the annual leave entitlement limits (total days granted per year) for the current employee.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="get_employee_leave_entitlements",
                                    description="Get annual leave entitlement limits for a specific employee. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"employee_id": types.Schema(type=types.Type.STRING, description="The employee ID")},
                                        required=["employee_id"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="get_all_leave_entitlements",
                                    description="Get annual leave entitlements for all employees. Requires HR role.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="filter_leave_entitlements",
                                    description="Filter leave entitlements by leave type and/or employee ID. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={
                                            "leave_type": types.Schema(type=types.Type.STRING, description="ANNUAL, SICK, UNPAID, BEREAVEMENT, STUDY, PARENTAL"),
                                            "employee_id": types.Schema(type=types.Type.STRING, description="Optional employee ID filter")
                                        }
                                    )
                                ),
                                # ── Leave Requests ───────────────────────────────
                                types.FunctionDeclaration(
                                    name="get_my_leave_requests",
                                    description="Get the current employee's own leave requests, optionally filtered by status.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"status": types.Schema(type=types.Type.STRING, description="Optional: PENDING, APPROVED, REJECTED, CANCELLED")}
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="get_all_employee_leave_requests",
                                    description="Get all leave requests from all employees. Requires HR role.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="find_employee_leave_requests",
                                    description="Find leave requests for a specific employee with optional status filter. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={
                                            "employee_id": types.Schema(type=types.Type.STRING, description="The employee ID"),
                                            "status": types.Schema(type=types.Type.STRING, description="Optional: PENDING, APPROVED, REJECTED, CANCELLED")
                                        },
                                        required=["employee_id"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="create_leave_request",
                                    description="Create a new leave request for the current employee.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={
                                            "leave_type": types.Schema(type=types.Type.STRING, description="ANNUAL, SICK, UNPAID, BEREAVEMENT, STUDY, PARENTAL"),
                                            "start_date": types.Schema(type=types.Type.STRING, description="Format YYYY-MM-DD"),
                                            "end_date": types.Schema(type=types.Type.STRING, description="Format YYYY-MM-DD"),
                                            "comment": types.Schema(type=types.Type.STRING, description="Optional reason")
                                        },
                                        required=["leave_type", "start_date", "end_date"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="cancel_leave_request",
                                    description="Cancel a leave request by its ID.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={"request_id": types.Schema(type=types.Type.INTEGER, description="The leave request ID")},
                                        required=["request_id"]
                                    )
                                ),
                                types.FunctionDeclaration(
                                    name="answer_leave_request",
                                    description="Approve or reject a leave request. Requires HR role.",
                                    parameters=types.Schema(
                                        type=types.Type.OBJECT,
                                        properties={
                                            "employee_id": types.Schema(type=types.Type.STRING, description="The employee ID whose request is being answered"),
                                            "request_id": types.Schema(type=types.Type.INTEGER, description="The leave request ID"),
                                            "is_accepted": types.Schema(type=types.Type.BOOLEAN, description="True to approve, False to reject"),
                                            "message": types.Schema(type=types.Type.STRING, description="Explanation message")
                                        },
                                        required=["employee_id", "request_id", "is_accepted", "message"]
                                    )
                                ),
                                # ── Leave Types & Holidays ───────────────────────
                                types.FunctionDeclaration(
                                    name="get_leave_types",
                                    description="Get available leave types and their rules (limits, policy references, etc.).",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                ),
                                types.FunctionDeclaration(
                                    name="get_holidays",
                                    description="Get the list of official public holidays.",
                                    parameters=types.Schema(type=types.Type.OBJECT, properties={})
                                )
                            ]
                        )
                    ]
                )
            )

        response = await self.chat.send_message(text)
        
        while response.function_calls:
            tool_responses = []
            for func_call in response.function_calls:
                # We need to un-wrap types if they are proto objects, but SDK usually gives dict
                args_dict = dict(func_call.args) if func_call.args else {}
                result = await self._handle_tool_call(func_call.name, args_dict)
                tool_responses.append(types.Part.from_function_response(
                    name=func_call.name,
                    response={"result": result}
                ))
            response = await self.chat.send_message(tool_responses)
            
        return response.text
