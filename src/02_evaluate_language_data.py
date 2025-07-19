from importlib.metadata import distribution
from typing import Callable

from unicodedata import category

from evaluation import EvaluationLanguageData
from model import (
    EnvConfig,
    RepositoryCategoryConfig,
    RepositoryFilterOptions,
    RepositoryMetaData,
    CategoryDistribution,
    LanguageDistribution,
)
from utility import (
    ConfigurationService,
    FileService,
    LoggingService,
    Utils,
)


def evaluate_languages():
    LoggingService.info("🚀 Start 'evaluate_languages' ...")

    repos = FileService.from_json(FileService.get_absolute_path(ConfigurationService.get_data_directory(), EnvConfig.organisation(), "repos-metadata.json"), RepositoryMetaData) # nur den einzelnen Typ mitgeben! keine Liste!

    languages = EvaluationLanguageData.collect_all_languages(repos)

    language_distributions = EvaluationLanguageData.evaluate_global_language_distribution(repos)

    config = RepositoryCategoryConfig(
        threshold_percent=7,
        categories={
            "Frontend": {"Vue", "JavaScript", "TypeScript", "HTML", "CSS"},
            "Backend": {"Java"},
            "Python": {"Python", "Jupyter Notebook"}
        }
    )
    repository_distribution, category_distribution = EvaluationLanguageData.evaluate_repository_category_distribution(repos, config, precision=1)

    LoggingService.info("📈 Languages:")
    FileService.to_csv(languages, ConfigurationService.get_result_directory(), EnvConfig.organisation(), "languages.csv")
    LoggingService.log_list(languages)

    LoggingService.info("📈 Global language distribution:")
    FileService.to_csv(language_distributions, ConfigurationService.get_result_directory(), EnvConfig.organisation(), "language-distribution.csv")
    LoggingService.log_list(language_distributions)

    LoggingService.info("📈 Repository category distribution:")
    FileService.to_csv(repository_distribution, ConfigurationService.get_result_directory(), EnvConfig.organisation(), "repository-distribution.csv")
    FileService.to_csv(category_distribution, ConfigurationService.get_result_directory(), EnvConfig.organisation(), "category-distribution.csv")
    LoggingService.log_list(repository_distribution)
    LoggingService.log_list(category_distribution)

    def category_value_fn(x: CategoryDistribution) -> float:
        return x.normalized_percentage
    def category_label_fn(x: CategoryDistribution) -> str:
        return x.category

    formated_category_distribution = Utils.format_latex_distribution(
        data=category_distribution,
        value_fn=category_value_fn,
        label_fn=category_label_fn,
    )
    LoggingService.info(f"category_distribution: {formated_category_distribution}")

    def language_value_fn(x: LanguageDistribution) -> float:
        return x.percentage

    def language_label_fn(x: LanguageDistribution) -> str:
        return x.language

    formated_language_distribution = Utils.format_latex_distribution_with_remainder(
        data=language_distributions,
        value_fn=language_value_fn,
        label_fn=language_label_fn,
        threshold=2.13
    )

    LoggingService.info(f"language_distribution: {formated_language_distribution}")


    return




if __name__ == "__main__":
    ConfigurationService.load_environment_configuration()
    evaluate_languages()

