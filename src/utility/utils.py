from typing import Callable, List, TypeVar

T = TypeVar("T")


class Utils:

    @staticmethod
    def _extract_pairs(
        data: List[T],
        value_fn: Callable[[T], float],
        label_fn: Callable[[T], str]
    ) -> List[tuple[float, str]]:
        """
        Wandelt beliebige Objekte in eine Liste von (Wert, Label)-Tupeln um.
        """
        return [(value_fn(item), label_fn(item)) for item in data]

    @staticmethod
    def _apply_grouped_remainder(
        pairs: List[tuple[float, str]],
        threshold: float,
        remainder_label: str = "Rest"
    ) -> List[tuple[float, str]]:
        """
        Gruppiert alle Einträge unterhalb des Schwellwerts in einem gemeinsamen Restposten.
        """
        above = [(v, l) for v, l in pairs if v >= threshold]
        remainder_sum = sum(v for v, _ in pairs if v < threshold)
        if remainder_sum > 0:
            above.append((remainder_sum, remainder_label))
        return above

    @staticmethod
    def format_latex_distribution(
        data: List[T],
        value_fn: Callable[[T], float],
        label_fn: Callable[[T], str],
        precision: int = 1
    ) -> str:
        """
        Formatiert eine Liste von Objekten im Format 'Wert/Label' für LaTeX-Ausgaben.
        Sortierung erfolgt absteigend nach Wert. Kein Komma am Ende der letzten Zeile.
        """
        try:
            pairs = Utils._extract_pairs(data, value_fn, label_fn)
            sorted_pairs = sorted(pairs, key=lambda t: t[0], reverse=True)
            lines = [f"{value:.{precision}f}/{label}" for value, label in sorted_pairs]
            return ",".join(lines)
        except Exception as err:
            raise ValueError("Fehler bei der LaTeX-Formatierung") from err

    @staticmethod
    def format_latex_distribution_with_remainder(
        data: List[T],
        value_fn: Callable[[T], float],
        label_fn: Callable[[T], str],
        threshold: float = 2.0,
        remainder_label: str = "Rest",
        precision: int = 1
    ) -> str:
        """
        Formatiert eine Liste von Objekten für LaTeX-Ausgabe und fasst alle Einträge
        unterhalb des Schwellwerts zu einem gemeinsamen Restposten zusammen.

        :param data: Liste von Objekten.
        :param value_fn: Funktion zur Extraktion des Werts.
        :param label_fn: Funktion zur Extraktion des Labels.
        :param threshold: Prozentwert, unterhalb dessen Einträge gruppiert werden.
        :param remainder_label: Label für den zusammengefassten Posten.
        :param precision: Rundung des Werts.
        """
        try:
            pairs = Utils._extract_pairs(data, value_fn, label_fn)
            grouped_pairs = Utils._apply_grouped_remainder(pairs, threshold, remainder_label)
            sorted_pairs = sorted(grouped_pairs, key=lambda t: t[0], reverse=True)
            lines = [f"{value:.{precision}f}/{label}" for value, label in sorted_pairs]
            return ",".join(lines)
        except Exception as err:
            raise ValueError("Fehler bei der LaTeX-Formatierung mit Gruppierung") from err
