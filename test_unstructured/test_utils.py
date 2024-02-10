import json
import os

import pytest

from unstructured import utils
from unstructured.documents.coordinates import PixelSpace
from unstructured.documents.elements import ElementMetadata, NarrativeText, Title


@pytest.fixture()
def input_data():
    return [
        {"text": "This is a sentence."},
        {"text": "This is another sentence.", "meta": {"score": 0.1}},
    ]


@pytest.fixture()
def output_jsonl_file(tmp_path):
    return os.path.join(tmp_path, "output.jsonl")


@pytest.fixture()
def input_jsonl_file(tmp_path, input_data):
    file_path = os.path.join(tmp_path, "input.jsonl")
    with open(file_path, "w+") as input_file:
        input_file.writelines([json.dumps(obj) + "\n" for obj in input_data])
    return file_path


def test_save_as_jsonl(input_data, output_jsonl_file):
    utils.save_as_jsonl(input_data, output_jsonl_file)
    with open(output_jsonl_file) as output_file:
        file_data = [json.loads(line) for line in output_file]
    assert file_data == input_data


def test_read_as_jsonl(input_jsonl_file, input_data):
    file_data = utils.read_from_jsonl(input_jsonl_file)
    assert file_data == input_data


def test_requires_dependencies_decorator():
    @utils.requires_dependencies(dependencies="numpy")
    def test_func():
        import numpy  # noqa: F401

    test_func()


def test_requires_dependencies_decorator_multiple():
    @utils.requires_dependencies(dependencies=["numpy", "pandas"])
    def test_func():
        import numpy  # noqa: F401
        import pandas  # noqa: F401

    test_func()


def test_requires_dependencies_decorator_import_error():
    @utils.requires_dependencies(dependencies="not_a_package")
    def test_func():
        import not_a_package  # noqa: F401

    with pytest.raises(ImportError):
        test_func()


def test_requires_dependencies_decorator_import_error_multiple():
    @utils.requires_dependencies(dependencies=["not_a_package", "numpy"])
    def test_func():
        import not_a_package  # noqa: F401
        import numpy  # noqa: F401

    with pytest.raises(ImportError):
        test_func()


def test_requires_dependencies_decorator_in_class():
    @utils.requires_dependencies(dependencies="numpy")
    class TestClass:
        def __init__(self):
            import numpy  # noqa: F401

    TestClass()


@pytest.mark.parametrize("iterator", [[0, 1], (0, 1), range(10), [0], (0,), range(1)])
def test_first_gives_first(iterator):
    assert utils.first(iterator) == 0


@pytest.mark.parametrize("iterator", [[], ()])
def test_first_raises_if_empty(iterator):
    with pytest.raises(ValueError):
        utils.first(iterator)


@pytest.mark.parametrize("iterator", [[0], (0,), range(1)])
def test_only_gives_only(iterator):
    assert utils.first(iterator) == 0


@pytest.mark.parametrize("iterator", [[0, 1], (0, 1), range(10)])
def test_only_raises_when_len_more_than_1(iterator):
    with pytest.raises(ValueError):
        utils.only(iterator)


@pytest.mark.parametrize("iterator", [[], ()])
def test_only_raises_if_empty(iterator):
    with pytest.raises(ValueError):
        utils.only(iterator)


@pytest.mark.parametrize(
    ("elements", "nested_error_tolerance_px", "expectation"),
    [
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely text",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            5,
            (
                True,
                [
                    {
                        "overlapping_elements": ["Title(ix=0)", "NarrativeText(ix=1)"],
                        "overlapping_case": "nested NarrativeText in Title",
                        "overlap_percentage": "100%",
                        "metadata": {
                            "largest_ngram_percentage": None,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely text",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["0. Title(ix=0)", "1. NarrativeText(ix=1)"],
                        "overlapping_case": "partial overlap sharing 50.0% of the text from1. "
                        "NarrativeText(2-gram)",
                        "overlap_percentage": "11.11%",
                        "metadata": {
                            "largest_ngram_percentage": 50.0,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely title",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["0. Title(ix=0)", "1. NarrativeText(ix=1)"],
                        "overlapping_case": "partial overlap with duplicate text",
                        "overlap_percentage": "11.11%",
                        "metadata": {
                            "largest_ngram_percentage": None,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["1. NarrativeText(ix=1)", "0. Title(ix=0)"],
                        "overlapping_case": (
                            "partial overlap with empty content in 1. NarrativeText"
                        ),
                        "overlap_percentage": "11.11%",
                        "metadata": {
                            "largest_ngram_percentage": None,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely title",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["0. Title(ix=0)", "1. NarrativeText(ix=1)"],
                        "overlapping_case": "partial overlap with empty content in 0. Title",
                        "overlap_percentage": "11.11%",
                        "metadata": {
                            "largest_ngram_percentage": None,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 5), (4, 8), (7, 8), (7, 5)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Something totally different here",
                    coordinates=((2, 3), (2, 6), (5, 6), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["0. Title(ix=0)", "1. NarrativeText(ix=1)"],
                        "overlapping_case": "partial overlap without sharing text",
                        "overlap_percentage": "11.11%",
                        "metadata": {
                            "largest_ngram_percentage": 0,
                            "overlap_percentage_total": "5.88%",
                            "max_area": "9pxˆ2",
                            "min_area": "9pxˆ2",
                            "total_area": "18pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((5, 6), (5, 10), (8, 10), (8, 6)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely text",
                    coordinates=((1, 3), (2, 7), (6, 7), (5, 3)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (
                True,
                [
                    {
                        "overlapping_elements": ["0. Title(ix=0)", "1. NarrativeText(ix=1)"],
                        "overlapping_case": "Small partial overlap",
                        "overlap_percentage": "8.33%",
                        "metadata": {
                            "largest_ngram_percentage": None,
                            "overlap_percentage_total": "3.23%",
                            "max_area": "20pxˆ2",
                            "min_area": "12pxˆ2",
                            "total_area": "32pxˆ2",
                        },
                    },
                ],
            ),
        ),
        (
            [
                Title(
                    text="Some lovely title",
                    coordinates=((4, 6), (4, 7), (7, 7), (7, 6)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
                NarrativeText(
                    text="Some lovely text",
                    coordinates=((6, 8), (6, 9), (9, 9), (9, 8)),
                    coordinate_system=PixelSpace(width=20, height=20),
                    metadata=ElementMetadata(page_number=1),
                ),
            ],
            1,
            (False, []),
        ),
    ],
)
def test_catch_overlapping_and_nested_bboxes(
    elements,
    expectation,
    nested_error_tolerance_px,
):
    overlapping_flag, overlapping_cases = utils.catch_overlapping_and_nested_bboxes(
        elements,
        nested_error_tolerance_px,
        sm_overlap_threshold=10.0,
    )
    assert overlapping_flag == expectation[0]
    assert overlapping_cases == expectation[1]


def test_validate_data_args():
    assert utils.validate_date_args("2020-10-10") is True

    with pytest.raises(ValueError):
        utils.validate_date_args("blah")

    with pytest.raises(ValueError):
        utils.validate_date_args(None)


def test_validate_date_args_accepts_standard_formats():
    assert utils.validate_date_args("1990-12-01")
    assert utils.validate_date_args("2050-01-01T00:00:00")
    assert utils.validate_date_args("2050-01-01+00:00:00")
    assert utils.validate_date_args("2022-02-12T14:30:00-0500")


def test_validate_date_args_raises_for_invalid_formats():
    with pytest.raises(ValueError):
        assert utils.validate_date_args(None)
        assert utils.validate_date_args("not a date")
        assert utils.validate_date_args("1990-12-33")
        assert utils.validate_date_args("2022-02-12T14:30:00-2000")


def test_htmlify_matrix_handles_empty_cells():
    matrix = [["cell1", "", "cell3"], ["", "cell5", ""]]
    expected_html = (
        "<table><tr><td>cell1</td><td></td><td>cell3</td></tr>"
        "<tr><td></td><td>cell5</td><td></td></tr></table>"
    )
    assert utils.htmlify_matrix_of_cell_texts(matrix) == expected_html


def test_htmlify_matrix_handles_special_characters():
    matrix = [['<>&"', "newline\n"]]
    expected_html = "<table><tr><td>&lt;&gt;&amp;&quot;</td><td>newline<br/></td></tr></table>"
    assert utils.htmlify_matrix_of_cell_texts(matrix) == expected_html


def test_htmlify_matrix_handles_multiple_rows_and_cells():
    matrix = [["cell1", "cell2"], ["cell3", "cell4"]]
    expected_html = (
        "<table><tr><td>cell1</td><td>cell2</td></tr><tr><td>cell3</td><td>cell4</td></tr></table>"
    )
    assert utils.htmlify_matrix_of_cell_texts(matrix) == expected_html


def test_htmlify_matrix_handles_empty_matrix():
    assert utils.htmlify_matrix_of_cell_texts([]) == ""


def test_only_returns_singleton_iterable():
    singleton_iterable = [42]
    result = utils.only(singleton_iterable)
    assert result == 42


def test_only_raises_on_non_singleton_iterable():
    singleton_iterable = [42, 0]
    with pytest.raises(ValueError):
        utils.only(singleton_iterable)
