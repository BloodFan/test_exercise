class IntervalProcessor:
    """Обрабатывает и объединяет интервалы."""

    @staticmethod
    def process_intervals(
        times: list[int], lesson_start: int, lesson_end: int
    ) -> list[tuple[int, int]]:
        """
        Обрезает интервалы по границам урока и возвращает список кортежей.
        """
        intervals = []
        for i in range(0, len(times), 2):
            start = max(times[i], lesson_start)
            end = min(times[i + 1], lesson_end)
            if start < end:
                intervals.append((start, end))
        return intervals

    @staticmethod
    def merge_intervals(
        intervals: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """Объединяет пересекающиеся интервалы."""
        if not intervals:
            return []
        intervals.sort()
        merged = [intervals[0]]
        for current in intervals[1:]:
            last = merged[-1]
            if current[0] <= last[1]:
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                merged.append(current)
        return merged


class IntervalIntersector:
    """Вычисляет пересечение интервалов ученика и учителя."""

    @staticmethod
    def intersect(
        pupil: list[tuple[int, int]], tutor: list[tuple[int, int]]
    ) -> int:
        """Считает общее время пересечения через two pointers."""
        total = 0
        i, j = 0, 0
        while i < len(pupil) and j < len(tutor):
            p_start, p_end = pupil[i]
            t_start, t_end = tutor[j]
            start = max(p_start, t_start)
            end = min(p_end, t_end)
            if start < end:
                total += end - start
            if p_end < t_end:
                i += 1
            else:
                j += 1
        return total


def appearance(intervals: dict[str, list[int]]) -> int:
    """обрабатывает данные и возвращает результат."""
    lesson_start, lesson_end = intervals["lesson"]
    pupil_raw = intervals["pupil"]
    tutor_raw = intervals["tutor"]

    pupil_processed = IntervalProcessor.process_intervals(
        pupil_raw, lesson_start, lesson_end
    )
    tutor_processed = IntervalProcessor.process_intervals(
        tutor_raw, lesson_start, lesson_end
    )

    pupil_merged = IntervalProcessor.merge_intervals(pupil_processed)
    tutor_merged = IntervalProcessor.merge_intervals(tutor_processed)

    return IntervalIntersector.intersect(pupil_merged, tutor_merged)


tests = [
    {
        "intervals": {
            "lesson": [1594663200, 1594666800],
            "pupil": [
                1594663340,
                1594663389,
                1594663390,
                1594663395,
                1594663396,
                1594666472,
            ],
            "tutor": [1594663290, 1594663430, 1594663443, 1594666473],
        },
        "answer": 3117,
    },
    {
        "intervals": {
            "lesson": [1594702800, 1594706400],
            "pupil": [
                1594702789,
                1594704500,
                1594702807,
                1594704542,
                1594704512,
                1594704513,
                1594704564,
                1594705150,
                1594704581,
                1594704582,
                1594704734,
                1594705009,
                1594705095,
                1594705096,
                1594705106,
                1594706480,
                1594705158,
                1594705773,
                1594705849,
                1594706480,
                1594706500,
                1594706875,
                1594706502,
                1594706503,
                1594706524,
                1594706524,
                1594706579,
                1594706641,
            ],
            "tutor": [
                1594700035,
                1594700364,
                1594702749,
                1594705148,
                1594705149,
                1594706463,
            ],
        },
        "answer": 3577,
    },
    {
        "intervals": {
            "lesson": [1594692000, 1594695600],
            "pupil": [1594692033, 1594696347],
            "tutor": [1594692017, 1594692066, 1594692068, 1594696341],
        },
        "answer": 3565,
    },
    # Пустые интервалы у ученика
    {
        "intervals": {
            "lesson": [1000, 2000],
            "pupil": [],
            "tutor": [1500, 1800],
        },
        "answer": 0,
    },
    # Интервалы ученика и учителя не пересекаются
    {
        "intervals": {
            "lesson": [1000, 2000],
            "pupil": [1000, 1200],
            "tutor": [1300, 1500],
        },
        "answer": 0,
    },
    # Интервалы полностью внутри урока
    {
        "intervals": {
            "lesson": [1000, 2000],
            "pupil": [1100, 1500, 1600, 1900],
            "tutor": [1200, 1400, 1700, 1800],
        },
        "answer": (1400 - 1200) + (1800 - 1700),  # 200 + 100 = 300
    },
    {
        "intervals": {
            "lesson": [1000, 2000],
            "pupil": [1100, 1300, 1250, 1400, 1600, 1800],
            "tutor": [1200, 1500, 1700, 1900],
        },
        "answer": 300,
    },
]

if __name__ == "__main__":
    for i, test in enumerate(tests):
        test_answer = appearance(test["intervals"])
        assert (
            test_answer == test["answer"]
        ), f'Error on test case {i}, got {test_answer}, expected {test["answer"]}'
