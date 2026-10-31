from io import BytesIO
from unittest.mock import MagicMock

from app.resume_parser import extract_text_from_pdf


def test_extract_text_from_pdf():
    mock_file = BytesIO(b"fake pdf content")

    mock_reader = MagicMock()

    page1 = MagicMock()
    page1.extract_text.return_value = "Python Developer"

    page2 = MagicMock()
    page2.extract_text.return_value = "FastAPI Developer"

    mock_reader.pages = [page1, page2]

    from unittest.mock import patch

    with patch("app.resume_parser.PdfReader", return_value=mock_reader):
        result = extract_text_from_pdf(mock_file)

    assert result == "Python Developer\nFastAPI Developer\n"


def test_extract_text_from_pdf_with_empty_page():
    mock_file = BytesIO(b"fake pdf content")

    mock_reader = MagicMock()

    page1 = MagicMock()
    page1.extract_text.return_value = None

    mock_reader.pages = [page1]

    from unittest.mock import patch

    with patch("app.resume_parser.PdfReader", return_value=mock_reader):
        result = extract_text_from_pdf(mock_file)

    assert result == ""

def test_extract_text_from_pdf_with_mixed_pages():
    mock_file = BytesIO(b"fake pdf content")

    mock_reader = MagicMock()

    page1 = MagicMock()
    page1.extract_text.return_value = "Python Developer"

    page2 = MagicMock()
    page2.extract_text.return_value = None

    page3 = MagicMock()
    page3.extract_text.return_value = "FastAPI Developer"

    mock_reader.pages = [page1, page2, page3]

    from unittest.mock import patch

    with patch("app.resume_parser.PdfReader", return_value=mock_reader):
        result = extract_text_from_pdf(mock_file)

    assert result == "Python Developer\nFastAPI Developer\n"

def test_extract_text_from_pdf_raises_exception_for_invalid_pdf():
    from unittest.mock import patch

    mock_file = BytesIO(b"invalid pdf content")

    with patch(
        "app.resume_parser.PdfReader",
        side_effect=Exception("Invalid PDF")
    ):
        try:
            extract_text_from_pdf(mock_file)
            assert False, "Expected an exception"
        except Exception as error:
            assert str(error) == "Invalid PDF"        