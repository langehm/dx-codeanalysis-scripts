import os

from git import GitCommandError, Repo

from model import RepositoryMetaData

from .configuration_service import ConfigurationService
from .file_service import FileService
from .logging_service import LoggingService


class GitService:

    def __init__(self, token: str):
        raise TypeError("This utility class cannot be instantiated.")

    @classmethod
    def clone_repo(cls, repo: RepositoryMetaData):
        if FileService.has_repository(repo):
            LoggingService.info(
                f"📦 {repo.repository_name} ist bereits geklont – kein Klonen erforderlich."
            )
            return

        try:
            target_path = FileService.get_absolute_path(
                ConfigurationService.get_repository_path_builder(repo)
            )
            LoggingService.info("⬇️ Repository nicht gefunden – beginne mit Klonen ...")
            Repo.clone_from(repo.repository_http_url, target_path)
            LoggingService.info(f"✅ Klonen von {repo.repository_name} abgeschlossen.")
        except GitCommandError as e:
            LoggingService.error(
                f"❌ Klonen fehlgeschlagen für {repo.repository_name}: {e}"
            )

    @classmethod
    def update_repo(cls, repo: RepositoryMetaData):

        if not FileService.has_repository(repo):
            LoggingService.info(
                f"📦 {repo.repository_name} nicht vorhanden. Update nicht möglich"
            )
            return

        LoggingService.info("🔄 Repository bereits vorhanden – prüfe auf Updates ...")

        repo_path = FileService.get_absolute_path(
            ConfigurationService.get_repository_path_builder(repo)
        )

        try:
            repository = Repo(repo_path)
            repository.remotes.origin.fetch()

            local = repository.commit(repository.active_branch.name)
            remote = repository.commit(f"origin/{repository.active_branch.name}")

            if local.hexsha != remote.hexsha:
                LoggingService.info(
                    f"🔄 Änderungen erkannt – aktualisiere {repo.repository_name}"
                )
                repository.git.reset("--hard")
                repository.remotes.origin.pull()
                LoggingService.info(
                    f"✅ Aktualisierung von {repo.repository_name} abgeschlossen."
                )
            else:
                LoggingService.info(
                    f"✔️ {repo.repository_name} ist bereits aktuell – kein Pull erforderlich."
                )

        except GitCommandError as e:
            LoggingService.error(
                f"❌ Update fehlgeschlagen für {repo.repository_name}: {e}"
            )
        except Exception as e:
            LoggingService.error(f"⚠️ Ungültiges Repository {repo.repository_name}: {e}")

    @classmethod
    def get_all_repositories(cls, repository_list: list[RepositoryMetaData]):
        LoggingService.info(f"⏩ Starte Verarbeitung von {len(repository_list)} Repositories ...")

        for repository_item in repository_list:
            repo_path = ConfigurationService.get_repository_path_builder(
                repository_item
            )
            abs_path = FileService.get_absolute_path(repo_path)

            LoggingService.info(
                f"📁 Repository: {repository_item.repository_owner}/{repository_item.repository_name}"
            )
            LoggingService.info(f"   → Zielpfad: {abs_path}")

            if FileService.has_repository(repository_item):
                GitService.update_repo(repository_item)
            else:
                GitService.clone_repo(repository_item)

        LoggingService.info("🏁 Verarbeitung abgeschlossen.")
