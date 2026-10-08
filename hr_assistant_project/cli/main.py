import os
import sys
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import httpx

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from cli.session import SessionContext
from cli.agent import HRAssistantAgent

load_dotenv()
console = Console()

async def main():
    console.print(Panel.fit("HR Assistant System CLI", style="bold blue"))
    
    email = Prompt.ask("შეიყვანეთ ელ-ფოსტა")
    employee_id = Prompt.ask("შეიყვანეთ Employee ID")
    
    console.print("[cyan]მიმდინარეობს ავთენტიფიკაცია...[/cyan]")
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:5010")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{base_url}/api/auth/login", json={"email": email, "employeeId": employee_id})
            res.raise_for_status()
            data = res.json()
            if data.get("isSuccess"):
                token = data["value"]["accessToken"]
                console.print("[green]ავტორიზაცია წარმატებულია.[/green]")
            else:
                console.print(f"[red]ავტორიზაცია ვერ მოხერხდა: {data.get('error', {}).get('message')}[/red]")
                return
    except Exception as e:
         console.print(f"[red]შეცდომა სერვერთან დაკავშირებისას: {e}[/red]")
         console.print("[yellow]ვიყენებთ ტესტურ ტოკენს.[/yellow]")
         token = "test_token_123"
    
    session = SessionContext(email=email, employee_id=employee_id, token=token)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[red]GEMINI_API_KEY არ არის მითითებული .env ფაილში.[/red]")
        return
        
    mcp_script = os.path.join(base_dir, "mcp_server", "server.py")
    db_dir = os.path.join(base_dir, "chroma_db")
    
    console.print("[cyan]აგენტის ინიციალიზაცია...[/cyan]")
    try:
        agent = HRAssistantAgent(api_key, mcp_script, db_dir)
        await agent.init(session)
        console.print("[bold green]HR ასისტენტი მზად არის. (გამოსასვლელად აკრიფეთ 'exit')[/bold green]")
    except Exception as e:
        console.print(f"[bold red]აგენტის ინიციალიზაციის შეცდომა: {e}[/bold red]")
        return
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]თანამშრომელი[/bold blue]")
            if user_input.lower() in ["exit", "quit", "გასვლა"]:
                break
                
            with console.status("[bold cyan]მონაცემების დამუშავება...[/bold cyan]"):
                try:
                    response = await agent.send_message(user_input)
                    console.print(f"\n[bold magenta]HR ასისტენტი:[/bold magenta]\n{response}")
                except Exception as e:
                    console.print(f"[bold red]შეცდომა პასუხის გენერაციისას:[/bold red] {e}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    asyncio.run(main())
