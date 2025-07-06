import multiprocessing
import pathlib
import os
import subprocess
import sys
import re
import platform

from typing import Optional, List
from pydantic import BaseModel
from src.log import render_error
from src.exceptions import DependencyError


class AgentFolderContent(BaseModel):
    agent_name: str
    agent_folder_path: pathlib.Path
    agent_folder_content: List[pathlib.Path]
    venv_folder: pathlib.Path


class ValidAgentFileData(BaseModel):
    agent_file: pathlib.Path
    agent_folder_path: pathlib.Path
    venv_folder: pathlib.Path


class AgentDependencyManager:
    """
    Builder class to run all agent in the root agents folder in the multiprocessing pool
    Supports only virtual environments folders named 'venv/' and '.venv/'
    """

    def __init__(self, agents_folder_name: str = "agents/"):
        self.agents_folder_name = agents_folder_name
        self.agents_folder_path = pathlib.Path().cwd() / self.agents_folder_name
        if not self.agents_folder_path.exists():
            raise OSError(
                f"Folder {str(self.agents_folder_path)} does not exist. Please specify a valid folder name with agents in the monorepo"
            )
        self.venv_combinations = ("venv", ".venv")
        self.agent_folders: List[Optional[pathlib.Path]] = []

    def _lookup_agents_folder(self) -> None:
        agent_folders = os.listdir(self.agents_folder_path)
        for agent_folder in agent_folders:
            full_fp = self.agents_folder_path / agent_folder
            if full_fp.is_dir():
                if full_fp.name not in self.venv_combinations:
                    self.agent_folders.append(full_fp)

    def _check_venvs_in_agent_folders(
        self,
    ) -> Optional[List[Optional[AgentFolderContent]]]:
        folders_data: List[Optional[AgentFolderContent]] = []
        for agent_folder in self.agent_folders:
            venv_folder = self._find_venv_in_agent_folder(agent_folder)
            if venv_folder:
                folders_data.append(
                    AgentFolderContent(
                        agent_name=agent_folder.name,
                        agent_folder_path=agent_folder,
                        agent_folder_content=[
                            agent_folder / file for file in os.listdir(agent_folder)
                        ],
                        venv_folder=venv_folder,
                    )
                )
            else:
                agents_root_folder = agent_folder.parent
                venv_folder = self._find_venv_in_agent_folder(agents_root_folder)
                if not venv_folder:
                    raise DependencyError(
                        f"No virtual environment folders were found in '{agent_folder}' and '{agents_root_folder}'.\nPlease create virtual environment in '{self.agents_folder_name}' folder or inside of the specific agent folder with your dependencies before proceeding"
                    )
                folders_data.append(
                    AgentFolderContent(
                        agent_name=agent_folder.name,
                        agent_folder_path=agent_folder,
                        agent_folder_content=[
                            agent_folder / obj for obj in os.listdir(agent_folder)
                        ],
                        venv_folder=venv_folder,
                    )
                )
        return folders_data

    def _find_venv_in_agent_folder(
        self, agent_folder_fp: pathlib.Path
    ) -> Optional[pathlib.Path]:
        agent_folder_content = os.listdir(str(agent_folder_fp))
        venv_folder = None
        for obj in agent_folder_content:
            if obj in self.venv_combinations:
                venv_folder = agent_folder_fp / obj
        return venv_folder

    def _lookup_file_for_session(self, py_file_fp: pathlib.Path) -> bool:
        re_pattern = r"(from genai_session\.session import GenAISession)|(GenAISession)|(@session\.bind)"
        with open(py_file_fp, "r+", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(pattern=re_pattern, string=content)
            return len(matches) == 3

    def _find_agent_file_in_agent_folder(
        self, folder_data: List[AgentFolderContent]
    ) -> List[Optional[ValidAgentFileData]]:
        valid_agents = []
        for folder in folder_data:
            for file in folder.agent_folder_content:
                if file.name.endswith(".py"):
                    is_agent = self._lookup_file_for_session(file)
                    if is_agent:
                        valid_agents.append(
                            ValidAgentFileData(
                                agent_file=file,
                                agent_folder_path=folder.agent_folder_path,
                                venv_folder=folder.venv_folder,
                            )
                        )
        return valid_agents

    def _get_venv(self, venv_folder: pathlib.Path) -> Optional[pathlib.Path]:
        if platform.system() == "Windows":
            venv_executable = venv_folder / "Scripts" / "python"
        else:
            venv_executable = venv_folder / "bin" / "python3"
        if not venv_executable.exists():
            raise FileNotFoundError(f"venv executable not found at {venv_executable}")
        return venv_executable

    def _run_agent_under_venv(self, file_content: ValidAgentFileData) -> None:
        try:
            venv_exec = self._get_venv(venv_folder=file_content.venv_folder)
            try:
                subprocess.run(
                    [str(venv_exec), str(file_content.agent_file)],
                    text=True,
                    check=True,
                    stdout=sys.stdout,
                    stderr=sys.stdout,
                )
            except subprocess.CalledProcessError as e:
                render_error(
                    f"Agent '{str(file_content.agent_file)}' has failed to start. Exiting with code: {e.returncode}"
                )
        except FileNotFoundError:
            render_error(
                "Virtual environment of the agent is not valid. Make sure python interpreter exists in the virtual environment and necessary packages were installed"
            )

    def _run_in_parallel(self, valid_agents: List[ValidAgentFileData]):
        processes: List[Optional[multiprocessing.Process]] = []
        for agent in valid_agents:
            process = multiprocessing.Process(
                target=self._run_agent_under_venv, args=(agent,)
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    def _run_in_pool(self, valid_agents: List[ValidAgentFileData]):
        processes_num = len(valid_agents)
        if processes_num < 1:
            return

        with multiprocessing.Pool(processes=processes_num) as p:
            self._run_in_parallel(valid_agents=valid_agents)
            p.terminate()
            p.join()

    def run(self):
        self._lookup_agents_folder()
        agent_folders_data = self._check_venvs_in_agent_folders()
        if agent_folders_data:
            valid_agents = self._find_agent_file_in_agent_folder(
                folder_data=agent_folders_data
            )
            self._run_in_pool(valid_agents)
