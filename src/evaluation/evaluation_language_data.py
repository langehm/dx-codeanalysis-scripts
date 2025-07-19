from collections import defaultdict

from model import (
    CategoryDistribution,
    LanguageDistribution,
    RepositoryCategoryConfig,
    RepositoryCategoryResult,
    RepositoryMetaData,
    LanguageWrapper,
)
from utility import LoggingService


class EvaluationLanguageData:
    @classmethod
    def collect_all_languages(
        cls, repository_metadata: list[RepositoryMetaData]
    ) -> list[LanguageWrapper]:
        LoggingService.info(
            "📚 Collecting all distinct languages from repositories ..."
        )

        all_languages = set()
        repo_count = len(repository_metadata)

        for i, repo in enumerate(repository_metadata, 1):
            repo_name = repo.repository_name
            LoggingService.info(f"🔍 ({i}/{repo_count}) Checking '{repo_name}'")

            if not repo.linguistic_data:
                LoggingService.info(f"⚠️ No linguistic data available for '{repo_name}'")
                continue

            try:
                all_languages.update(repo.linguistic_data.keys())
            except Exception as e:
                LoggingService.error(
                    f"❌ Failed to read languages from '{repo_name}': {e}"
                )

        LoggingService.info(f"✅ Found {len(all_languages)} distinct languages.")

        return [LanguageWrapper(language=lang) for lang in sorted(all_languages)]

    @classmethod
    def evaluate_global_language_distribution(
        cls, repository_metadata: list[RepositoryMetaData]
    ) -> list[LanguageDistribution]:
        LoggingService.info("📊 Starting global language distribution evaluation ...")

        language_totals = defaultdict(int)
        total_bytes = 0
        repo_count = len(repository_metadata)

        for i, repo in enumerate(repository_metadata, 1):
            repo_name = repo.repository_name
            LoggingService.info(
                f"🔍 ({i}/{repo_count}) Evaluating linguistic data of '{repo_name}'"
            )

            if not repo.linguistic_data:
                LoggingService.info(f"⚠️ No linguistic data available for '{repo_name}'")
                continue

            try:
                for language, byte_count in repo.linguistic_data.items():
                    language_totals[language] += byte_count
                    total_bytes += byte_count

            except Exception as e:
                LoggingService.error(
                    f"❌ Failed to process linguistic data of '{repo_name}': {e}"
                )

        if not language_totals:
            LoggingService.info("⚠️ No language data found across repositories.")
            return []

        LoggingService.info("✅ Language data successfully aggregated.")

        result = []
        for language, byte_count in sorted(
            language_totals.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (byte_count / total_bytes) * 100
            result.append(
                LanguageDistribution(
                    language=language, bytes=byte_count, percentage=round(percentage, 2)
                )
            )

        return result

    @classmethod
    def evaluate_repository_category_distribution(
        cls,
        repository_metadata: list[RepositoryMetaData],
        config: RepositoryCategoryConfig,
        precision: int = 2,  # <--- NEU
    ) -> tuple[list[RepositoryCategoryResult], list[CategoryDistribution]]:
        repo_count = len(repository_metadata)
        repo_category_map: dict[str, str] = {}
        category_counter = defaultdict(int)

        for i, repo in enumerate(repository_metadata, 1):
            repo_name = repo.repository_name
            LoggingService.info(
                f"🔍 ({i}/{repo_count}) Analyzing repository '{repo_name}'"
            )

            if not repo.linguistic_data:
                LoggingService.info(f"⚠️ No linguistic data available for '{repo_name}'")
                repo_category_map[repo_name] = "Rest"
                category_counter["Rest"] += 1
                continue

            try:
                total_bytes = sum(repo.linguistic_data.values())
                if total_bytes == 0:
                    raise ValueError("No language data")

                relevant_languages = {
                    lang
                    for lang, count in repo.linguistic_data.items()
                    if (count / total_bytes * 100) >= config.threshold_percent
                }

                matched_categories = {
                    cat_name
                    for cat_name, lang_set in config.categories.items()
                    if relevant_languages & lang_set
                }

                if not matched_categories:
                    assigned_category = "Rest"
                else:
                    assigned_category = " + ".join(sorted(matched_categories))

                repo_category_map[repo_name] = assigned_category
                category_counter[assigned_category] += 1

            except Exception as e:
                LoggingService.error(
                    f"❌ Failed to process linguistic data for '{repo_name}': {e}"
                )
                repo_category_map[repo_name] = "Rest"
                category_counter["Rest"] += 1

        total_categorized = sum(category_counter.values())
        if total_categorized == 0:
            LoggingService.info("⚠️ No repositories could be categorized.")
            return [], []

        # Für die Normalisierung ohne "Rest"
        categories_excluding_rest = {
            cat: count for cat, count in category_counter.items() if cat != "Rest"
        }
        total_without_rest = sum(categories_excluding_rest.values())

        repo_results = [
            RepositoryCategoryResult(repository_name=repo, category=cat)
            for repo, cat in sorted(repo_category_map.items())
        ]

        category_results = []
        for cat, count in sorted(category_counter.items()):
            value = (count / total_categorized) * 100
            percentage = (
                int(round(value)) if precision == 0 else round(value, precision)
            )

            if cat == "Rest" or total_without_rest == 0:
                normalized = 0.0
            else:
                value = (count / total_without_rest) * 100
                normalized = (
                    int(round(value)) if precision == 0 else round(value, precision)
                )

            category_results.append(
                CategoryDistribution(
                    category=cat,
                    count=count,
                    percentage=percentage,
                    normalized_percentage=normalized,
                )
            )

        LoggingService.info("✅ Language data successfully aggregated.")
        return repo_results, category_results
