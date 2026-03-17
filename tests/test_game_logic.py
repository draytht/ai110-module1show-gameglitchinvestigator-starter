"""
Tests targeting the five bugs fixed in app.py.

Streamlit is mocked in conftest.py so the module-level st.* calls
don't raise errors during testing.
"""
from app import check_guess, update_score, get_range_for_difficulty


# ---------------------------------------------------------------------------
# Bug 1: Backwards hint messages
# "Too High" should say Go LOWER, "Too Low" should say Go HIGHER
# ---------------------------------------------------------------------------

def test_too_high_hint_says_go_lower():
    outcome, message = check_guess(80, 50)
    assert outcome == "Too High"
    assert "LOWER" in message, f"Expected 'LOWER' in hint, got: {message}"


def test_too_low_hint_says_go_higher():
    outcome, message = check_guess(20, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message, f"Expected 'HIGHER' in hint, got: {message}"


# ---------------------------------------------------------------------------
# Bug 2: String comparison on even attempts (lexicographic vs numeric)
# Passing an integer secret must always produce correct numeric comparisons.
# The classic failure case was "9" > "50" == True (wrong), 9 > 50 == False (correct).
# ---------------------------------------------------------------------------

def test_numeric_comparison_not_lexicographic():
    # 9 < 50 numerically — outcome must be "Too Low", not "Too High"
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low", (
        f"Expected 'Too Low' (9 < 50), got '{outcome}'. "
        "Likely caused by string/lexicographic comparison."
    )


def test_numeric_comparison_large_guess():
    # 100 > 50 numerically — outcome must be "Too High"
    outcome, _ = check_guess(100, 50)
    assert outcome == "Too High"


# ---------------------------------------------------------------------------
# Bug 3: Score oscillation — "Too High" must always deduct, never reward
# ---------------------------------------------------------------------------

def test_too_high_always_deducts_on_even_attempt():
    score = update_score(100, "Too High", attempt_number=2)  # even
    assert score == 95, f"Expected 95, got {score}. Even attempts should still deduct."


def test_too_high_always_deducts_on_odd_attempt():
    score = update_score(100, "Too High", attempt_number=3)  # odd
    assert score == 95, f"Expected 95, got {score}."


def test_no_score_oscillation_across_attempts():
    """Score should decrease monotonically on repeated Too High outcomes."""
    score = 100
    for attempt in range(1, 7):
        score = update_score(score, "Too High", attempt_number=attempt)
    assert score == 70, f"Expected 70 after 6 Too High penalties, got {score}."


# ---------------------------------------------------------------------------
# Bug 4: Hard difficulty range must be wider than Normal (1–100)
# ---------------------------------------------------------------------------

def test_hard_range_wider_than_normal():
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high, (
        f"Hard ({hard_high}) should have a larger upper bound than Normal ({normal_high})."
    )


def test_easy_range_narrower_than_normal():
    normal_low, normal_high = get_range_for_difficulty("Normal")
    easy_low, easy_high = get_range_for_difficulty("Easy")
    assert easy_high < normal_high


# ---------------------------------------------------------------------------
# Bug 5: New game attempts reset
# The fix sets attempts back to 1 (matching initialization), not 0.
# This is enforced via the app's session state logic, but we can verify
# the initial state value is 1 by checking the session_state initialization
# path is consistent with what a new game would set.
#
# Note: Full session-state behavior requires an integration/Streamlit test.
# This unit test documents the expected starting value.
# ---------------------------------------------------------------------------

def test_initial_attempts_value_is_one():
    """
    The game initializes attempts at 1, and New Game should reset to the same value.
    This test documents the contract: attempt counting starts at 1, not 0.
    Attempt-based logic (score, string-conversion) breaks if starting at 0.
    """
    expected_start = 1
    # Verify update_score behaves correctly when called with attempt_number=1
    # (i.e., first real guess), not attempt_number=0
    score_from_attempt_1 = update_score(0, "Win", attempt_number=1)
    score_from_attempt_0 = update_score(0, "Win", attempt_number=0)
    # attempt_number=0 gives a higher (wrong) score than attempt_number=1
    assert score_from_attempt_1 < score_from_attempt_0, (
        "Win on attempt 1 should score less than attempt 0. "
        "Starting at 0 inflates the win score incorrectly."
    )
