"""Runs the exact command from the quickstart docs

    htrflow pipeline pipeline.yaml image.jpg

against its three example images:
https://ai-riksarkivet.github.io/htrflow/latest/getting_started/quick_start.html

This is a real end-to-end run: it downloads the two documented models
(a YOLO line segmenter and a TrOCR text recognizer) and runs them on CPU,
so it's slow and needs network access. The transcription is compared to the
documented expected result with a word error rate, not an exact match, since
minor decoding differences (dependency versions, hardware) are expected.

Only example_1 runs in default CI (each case reloads and reruns both models
on CPU, so 3 cases roughly triples the wall time for the same "does the
documented pipeline still work" signal). example_2 and example_3 are marked
`extended` and skipped by CI's default `-m` filter; run them locally or
deliberately with `pytest -m extended`.
"""

from pathlib import Path

import jiwer
import pytest
from typer.testing import CliRunner

from htrflow.cli import app


runner = CliRunner()

PIPELINE_YAML = Path("tests/integration/data/pipelines/quickstart_pipeline.yaml").resolve()

# Word error rate threshold below which the transcription is considered a
# working match of the documented result. Generous on purpose: this test is
# meant to catch "the pipeline is broken/producing garbage", not to pin down
# an exact transcription. Real runs against these images land around
# 0.44-0.50 WER (normal OCR noise on real handwriting vs. a cleaned-up
# reference transcription); a totally broken pipeline scores far higher.
MAX_WER = 0.0  # deliberately impossible threshold to test the E2E CI gate

EXAMPLES = {
    "example_1": (
        "docs/examples/A0062408_00007.jpg",
        """
        Mästaren med det lofliga hammarsmeds hämbetet bör¬
        römliga Sven Svensson Hjerpe, som med sin hustru rör¬
        bära och dygdesanna Lisa Jansdotter bortflyttrande
        till Lungsundt Sochn; bekoma härifrån följande
        bewis, at mannen är född 1746, hustrun 1754.
        begge i sina Christandoms stycken grundrade och i
        sin lofnad förelgifwande. warit till hittwarden
        sin 25/4 och wid Förhören på behörig tid.
        Carlskoja fyld 21 Sept: 1773. Bengt Forsman
        adj: Past:
        Sundberg
        """,
    ),
    "example_2": (
        "docs/examples/A0062408_00006.jpg",
        """
        Beskedeliga mannen Jöns Håkansson
        Född 1730, som med dess hustru Åhreborn till
        Margreta Andersdotter född 1736 flygge wäl
        Liungsunds församling, kunna i ägge wäl
        Läfft i och utan bok, och förstå sin Christendom
        Förswarligen, hafwa under sitt wistelig af
        här i Församlingen fördt en Christa gång
        larbar wandel, Commarerade sista gång
        d. 21. nästl. dotren Maria är född. 1760.
        Det. Sigrid 1767. Son Anders 1768. Attr
        Philipstad d. 25. Martii 1773.
        And: Levin
        Malborj
        Comminist loci.
        """,
    ),
    "example_3": (
        "docs/examples/451511_1512_01.jpg",
        """
        Monmouth den 29 1882.
        .
        Platskade Syster emot Svåger
        Hå godt är min önskan
        Jag får återigen göra försöket
        att sända eder bref, jag har
        förut skrifvitt men ej erhallett
        någott wår från eder var. varför
        jag tager det för troligt att
        brefven icke har gått fram.
        jag har erinu den stora gåfvan
        att hafva en god helsa intill
        skrifvande dag, och önskligt
        voro att dessa rader trefar
        eder vid samma goda gofva.
        och jag får önska eder lycka
        på det nya åratt samt god
        fortsättning på detsamma.
        """,
    ),
}


@pytest.mark.slow
@pytest.mark.parametrize(
    "image_path,expected_text",
    [
        EXAMPLES["example_1"],
        pytest.param(*EXAMPLES["example_2"], marks=pytest.mark.extended),
        pytest.param(*EXAMPLES["example_3"], marks=pytest.mark.extended),
    ],
    ids=list(EXAMPLES.keys()),
)
def test_quickstart_pipeline(image_path, expected_text, tmp_path, monkeypatch):
    image_path = Path(image_path).resolve()
    assert image_path.exists(), f"quickstart example image not found: {image_path}"

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        ["pipeline", str(PIPELINE_YAML), str(image_path), "--logfile", "quickstart-test.log"],
    )
    assert result.exit_code == 0, result.output

    output_file = tmp_path / "outputs" / f"{image_path.stem}.txt"
    assert output_file.exists(), f"expected output file was not created: {output_file}"
    transcription = output_file.read_text(encoding="utf-8")

    assert transcription.strip(), "pipeline produced an empty transcription"

    error_rate = jiwer.wer(expected_text, transcription)
    assert error_rate < MAX_WER, (
        f"transcription differs too much from the documented quickstart result "
        f"(word error rate {error_rate:.2f}, threshold {MAX_WER}):\n{transcription}"
    )
