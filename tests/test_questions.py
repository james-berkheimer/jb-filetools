import logging
from unittest.mock import patch

import pytest

from filetools.questions import QuestionError, ask_bool, ask_multichoice, ask_text_input


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    with patch("filetools.questions.log") as mock_log:
        yield mock_log


class TestQuestionError:
    """Test suite for QuestionError exception class."""

    def test_question_error_basic(self):
        """Test basic QuestionError creation and string representation."""
        error = QuestionError("Test error")
        assert str(error) == "QuestionError: Test error | Question: None | Details: None"

    def test_question_error_with_details(self):
        """Test QuestionError with all fields populated."""
        error = QuestionError("Test error", "test question", "test details")
        assert error.question == "test question"
        assert error.details == "test details"
        assert "test details" in str(error)


class TestAskBool:
    """Test suite for boolean question prompts."""

    @pytest.mark.parametrize(
        "user_input,expected",
        [
            ("y", True),
            ("Y", True),
            ("yes", True),
            ("n", False),
            ("N", False),
            ("no", False),
        ],
    )
    def test_valid_inputs(self, user_input, expected, mock_logger):
        """Test valid yes/no inputs."""
        with patch("builtins.input", return_value=user_input):
            result = ask_bool("Test question")
            assert result == expected
            mock_logger.question.assert_called_once()

    def test_default_value(self, mock_logger):
        """Test empty input with default value."""
        with patch("builtins.input", return_value=""):
            result = ask_bool("Test question", default_value=True)
            assert result is True

    def test_invalid_input_then_valid(self, mock_logger):
        """Test handling of invalid input followed by valid input."""
        with patch("builtins.input", side_effect=["invalid", "y"]):
            result = ask_bool("Test question")
            assert result is True
            assert mock_logger.warning.called


class TestAskMultichoice:
    """Test suite for multiple choice questions."""

    @pytest.fixture
    def choices(self):
        """Sample choices for testing."""
        return ["option1", "option2", "option3"]

    def test_valid_choice(self, choices, mock_logger):
        """Test selection of valid choice."""
        with patch("builtins.input", return_value="2"):
            result = ask_multichoice(choices)
            assert result == "option2"
            mock_logger.question.assert_called_once()

    def test_invalid_then_valid_choice(self, choices, mock_logger):
        """Test handling of invalid choice followed by valid choice."""
        with patch("builtins.input", side_effect=["invalid", "4", "2"]):
            result = ask_multichoice(choices)
            assert result == "option2"
            assert mock_logger.warning.called

    def test_empty_choices(self):
        """Test handling of empty choices list."""
        with pytest.raises(QuestionError) as exc_info:
            ask_multichoice([])
        assert "No choices provided" in str(exc_info.value)


class TestAskTextInput:
    """Test suite for free-form text input."""

    @pytest.mark.parametrize(
        "user_input,expected",
        [
            ("Simple Text", "simple_text"),
            ("UPPER CASE", "upper_case"),
            ("no spaces", "no_spaces"),
            (
                "   extra spaces   ",
                "extra_spaces",
            ),  # Should strip spaces before conversion
            ("multiple   spaces", "multiple_spaces"),  # Should collapse multiple spaces
            ("", ""),  # Empty input case
        ],
    )
    def test_text_input_formatting(self, user_input, expected, mock_logger):
        """Test text input formatting."""
        with patch("builtins.input", return_value=user_input):
            result = ask_text_input("Test question")
            assert result == expected
            mock_logger.question.assert_called_once()
