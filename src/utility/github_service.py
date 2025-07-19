import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List
from tqdm import tqdm
from github import Auth, Github

from model import EnvConfig, RepositoryFilterOptions, RepositoryMetaData, LinguisticData
from .logging_service import LoggingService

class GithubService:
    MAX_WORKERS = 16
    _github = Github(auth=Auth.Token(EnvConfig.token()))

    def __init__(self, token: str):
        self._auth = Auth.Token(EnvConfig.token())
        self._github = Github(auth=self._auth)

    @classmethod
    def fetch_all_repos(cls, filters: Optional[RepositoryFilterOptions] = None) -> list[RepositoryMetaData]:
        try:
            user = cls._github.get_user(EnvConfig.organisation())
            repos = user.get_repos()

            LoggingService.info(f"👤 Benutzer: {user.login} ({user.html_url})")
            LoggingService.info(f"📦 Gefundene Repositories: {repos.totalCount}")

            filtered = []
            for repo in repos:
                if filters:
                    if (
                        filters.include_forks is not None
                        and repo.fork != filters.include_forks
                    ):
                        continue
                    if (
                        filters.include_archived is not None
                        and repo.archived != filters.include_archived
                    ):
                        continue
                    if (
                        filters.include_disabled is not None
                        and repo.disabled != filters.include_disabled
                    ):
                        continue
                    if (
                        filters.include_template is not None
                        and repo.is_template != filters.include_template
                    ):
                        continue

                filtered.append(
                    RepositoryMetaData(
                        repository_name=repo.name,
                        repository_owner=repo.owner.login,
                        repository_id=repo.id,
                        repository_http_url=repo.html_url,
                        repository_size=repo.size,
                    )
                )

            LoggingService.info(f"✅ Repositories nach Filterung: {len(filtered)}")
            return filtered

        except Exception as e:
            LoggingService.error(f"❌ Fehler beim Abrufen der Repositories: {e}")
            return []

    @classmethod
    def download_language_data(cls, repo_id: int) -> dict[str, int]:
        try:
            langs = cls._github.get_repo(repo_id).get_languages()
            LoggingService.info(f"🧠 Sprachdaten für Repository {repo_id} abgerufen: {list(langs.keys())}")
            return langs
        except Exception as e:
            LoggingService.error(f"❌ Fehler beim Lesen der Sprachdaten von {repo_id}: {e}")
            return {}

    @classmethod
    def calculate_repositories_disk_size(cls, repositories: list[RepositoryMetaData]) -> int:
        total = sum(repo.repository_size for repo in repositories)
        LoggingService.info(f"🧮 Gesamtspeicherbedarf (kB): {total}")
        return total


    @classmethod
    def enrich_repository_linguistic_data(cls, metadata: RepositoryMetaData) -> RepositoryMetaData:
        try:
            #LoggingService.info(f"🔍 Analysiere Repository: {metadata.repository_owner}/{metadata.repository_name} …")
            repo = cls._github.get_repo(f"{metadata.repository_owner}/{metadata.repository_name}")
            metadata.linguistic_data = repo.get_languages()
            #LoggingService.info(f"🆗 Sprachdaten hinzugefügt für: {metadata.repository_name} ({len(metadata.linguistic_data)} Sprachen)")
        except Exception as e:
            LoggingService.error(f"❌ Fehler bei {metadata.repository_owner}/{metadata.repository_name}: {e}")
            metadata.linguistic_data = []
        return metadata

    @classmethod
    def enrich_repositories_linguistic_data(cls, repositories: List[RepositoryMetaData]) -> List[RepositoryMetaData]:
        LoggingService.info(f"⏩ Starte Verarbeitung von {len(repositories)} Repositories mit max. {cls.MAX_WORKERS} Threads …")

        enriched_results = [GithubService.enrich_repository_linguistic_data(repo) for repo in repositories]

        LoggingService.info("🏁 Verarbeitung abgeschlossen.")
        return enriched_results

