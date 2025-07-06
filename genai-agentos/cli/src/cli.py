import asyncio
import multiprocessing
import typer
from uuid import uuid4

from src.exceptions import APIError
from src.utils import cli_error_renderer, load_jwt, validate_uuid
from src.log import prettify_json, render_success, render_error
from src.http import http_repo
from src.jinja.file_generator import generate_agent_file
from src.launch_all_agents import AgentDependencyManager

app = typer.Typer(
    help="GenAI CLI app",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)

@app.command(name="login")
@cli_error_renderer
def login(
    username: str = typer.Option(..., "--username", "-u", help="Your genai username"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Your password"),
):
    return asyncio.run(http_repo.login_user(username=username, password=password))


@app.command(name="signup")
@cli_error_renderer
def register(
    username: str = typer.Option(..., "--username", "-u", help="Your genai username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Your password"),
):
    try:
        return asyncio.run(http_repo.register_user(username=username, password=password))
    except APIError as e:
        render_error(str(e))
        return


@app.command(name="logout")
def logout():
    return http_repo.creds_manager.logout()


@app.command(name="list_agents")
@cli_error_renderer
def list_agents(limit: int = 100, offset: int = 0):
    try:
        user_jwt = load_jwt(http_repo=http_repo)
        result = asyncio.run(
            http_repo.list_agents(
                limit=limit,
                offset=offset,
                headers={"Authorization": f"Bearer {user_jwt}"},
            )
        )
        render_success(prettify_json(result.json()))
    except APIError as e:
        render_error(str(e))


@app.command(name="register_agent")
@cli_error_renderer
def register_agent(
    agent_id: str = typer.Option(None, "--id", help="UUID for your agent (auto-generated if not provided)"),
    name: str = typer.Option(..., "-n", "--name", help="Name of your agent"),
    description: str = typer.Option(..., "-d", "--description", help="Agent description")
):
    if not agent_id:
        agent_id = str(uuid4())

    agent_id = validate_uuid(agent_id, field_name="agent_id")
    if not agent_id:
        return

    user_jwt = load_jwt(http_repo=http_repo)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        register_result = loop.run_until_complete(
            http_repo.register_agent(
                agent_id=agent_id,
                name=name,
                description=description,
                headers={"Authorization": f"Bearer {user_jwt}"},
            )
        )

        result_json = register_result.json()
        agent_id_str = result_json.get("agent_id")  # ✅ Corrected key

        if not agent_id_str:
            raise KeyError("No 'agent_id' returned from backend. Full response: " + str(result_json))

        render_success(f"✅ Registered agent '{agent_id_str}' successfully. Generating agent body...")

        # Look up and generate agent YAML
        agent = loop.run_until_complete(
            http_repo.lookup_agent(
                agent_id=agent_id_str,
                headers={"Authorization": f"Bearer {user_jwt}"},
            )
        )

        if not agent:
            loop.run_until_complete(
                http_repo.delete_agent(
                    agent_id=agent_id_str,
                    headers={"Authorization": f"Bearer {user_jwt}"},
                )
            )
            render_error("❌ Agent lookup failed after registration. Cleanup done.")
            return

        generate_agent_file(agent_body=agent)

    except Exception as e:
        render_error(f"❌ Failed to register agent. Error: {e}")
    finally:
        loop.close()


@app.command(name="delete_agent")
@cli_error_renderer
def delete_agent(
    agent_id: str = typer.Option(..., "--id", help="UUID of the agent to delete"),
):
    agent_id = validate_uuid(agent_id, field_name="agent_id")
    if not agent_id:
        return

    user_jwt = load_jwt(http_repo=http_repo)

    is_deleted = asyncio.run(
        http_repo.delete_agent(
            agent_id=agent_id,
            headers={"Authorization": f"Bearer {user_jwt}"},
        )
    )
    if is_deleted:
        render_success(f"✅ Agent {agent_id} was deleted successfully")
    else:
        raise APIError("Request succeeded but failed to delete the agent.")


@app.command(name="generate_agent")
@cli_error_renderer
def generate_agent(
    agent_id: str = typer.Option(..., "--id", help="UUID of the agent to generate"),
):
    agent_id = validate_uuid(agent_id, field_name="agent_id")
    if not agent_id:
        return

    user_jwt = load_jwt(http_repo=http_repo)
    agent = asyncio.run(
        http_repo.lookup_agent(
            agent_id=agent_id, headers={"Authorization": f"Bearer {user_jwt}"}
        )
    )
    if not agent:
        return

    generate_agent_file(agent_body=agent)


@app.command(name="run_agents")
@cli_error_renderer
def run_agents():
    manager = AgentDependencyManager()
    manager.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)
    app()
