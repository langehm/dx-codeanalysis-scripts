from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Callable, List, Optional

from tqdm import tqdm

from .logging_service import LoggingService


def _now() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")

def use_threads(
    func: Callable[[Any], Any],
    args_list: List[Any],
    max_threads: int = 4,
    description: Optional[str] = "🔄 In Arbeit"
) -> List[Any]:
    """
    Führt eine Funktion parallel mit mehreren Threads aus.

    :param func: Die Funktion, die aufgerufen werden soll.
    :param args_list: Liste der Argumente (ein Argument pro Aufruf).
    :param max_threads: Maximale Anzahl paralleler Threads.
    :param description: Beschreibung für die Fortschrittsanzeige.
    :return: Liste der Rückgabewerte der Funktion.
    """
    results = [None] * len(args_list)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(func, arg): i
            for i, arg in enumerate(args_list)
        }

        formatted_desc = f"logging-service - {_now()} - INFO - {description}"

        for future in tqdm(as_completed(futures), total=len(args_list), desc=formatted_desc):
            i = futures[future]
            try:
                results[i] = future.result()
            except Exception as e:
                LoggingService.error(f"❌ Fehler in Thread {i}: {e}")
                results[i] = None  # oder: args_list[i], wenn du das Original zurückgeben willst

    return results
