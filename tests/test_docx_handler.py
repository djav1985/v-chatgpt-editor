import os
import shutil
import sys
from pathlib import Path

import pytest
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from docx_handler import (  # noqa: E402
    add_formatted_runs,
    merge_groups_and_save,
    process_html_fragments,
    replace_quotes,
)


def test_replace_quotes_smart_quotes():
    text = '"Hello", she said. It\'s "fine."'
    expected = '“Hello”, she said. It’s “fine.”'
    assert replace_quotes(text) == expected


def test_process_html_fragments_nested_styles():
    html = "Plain <b>bold <i>both</i></b> <i>italic</i>"
    fragments = process_html_fragments(html)
    assert fragments == [
        ("Plain ", set()),
        ("bold ", {"b"}),
        ("both", {"b", "i"}),
        (" ", set()),
        ("italic", {"i"}),
    ]


def test_add_formatted_runs_for_nested_styles():
    doc = Document()
    para = doc.add_paragraph()
    html = "Plain <b>bold <i>both</i></b> <i>italic</i>"
    fragments = process_html_fragments(html)
    add_formatted_runs(para, fragments)

    formatted_runs = [
        (run.text, bool(run.bold), bool(run.italic))
        for run in para.runs
        if run.text
    ]

    assert formatted_runs == [
        ("Plain ", False, False),
        ("bold ", True, False),
        ("both", True, True),
        (" ", False, False),
        ("italic", False, True),
    ]


@pytest.mark.parametrize(
    "heading_tag, expected_style, expected_text",
    [
        ("<h3>Deep Dive</h3>", "Heading 3", "Deep Dive"),
        ("<h4>Appendix</h4>", "Heading 4", "Appendix"),
    ],
)
def test_merge_groups_and_save_preserves_heading_levels(
    tmp_path, heading_tag, expected_style, expected_text
):
    sample_name = "sample.docx"
    tmp_root = Path("tmp")
    section_dir = tmp_root / Path(sample_name).stem
    output_dir = tmp_path / "output"

    shutil.rmtree(section_dir, ignore_errors=True)
    section_dir.mkdir(parents=True, exist_ok=True)

    new_content = [
        "<h1>Chapter \"One\"</h1>",
        "<p>Intro paragraph.</p>",
        heading_tag,
    ]
    (section_dir / "1-section.new").write_text("\n".join(new_content), encoding="utf-8")
    (section_dir / "1-section.old").write_text("\n".join(new_content), encoding="utf-8")

    os.environ["OUTPUT_DIR"] = str(output_dir)

    try:
        merge_groups_and_save(sample_name, "edit")

        generated_doc = output_dir / f"EDIT_{sample_name}"
        assert generated_doc.exists()

        document = Document(generated_doc)
        heading_styles = [(para.text, para.style.name) for para in document.paragraphs]

        assert ("Chapter “One”", "Heading 1") in heading_styles
        assert any(text == "Intro paragraph." for text, _ in heading_styles)
        assert (expected_text, expected_style) in heading_styles
    finally:
        shutil.rmtree(section_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
        os.environ.pop("OUTPUT_DIR", None)
