# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it? 
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
- could not restart game after win
- could not start a new game after use all the attempts
- wrong output after typing number (guess)
- wrong suggestion(hint)
- UI did not change after changed difficulty
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? 
    - copilot & claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result). 
    - when asked to fix the bugs, claude identified that the check_guess hint were swapped and applied the fix to both the primary try block and the except TypeError fallback path at the same time. 

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
    - When i was settin gup pytest. Claude's first attempt mocked streamlit by setting session)state which iis a plain dict. This make the pytest failed with AttributeError: 'dict' object has no attribute.. because the main app.py user attribute-style access rather then dict-style access. I prompted to tell claude then tried patching session_data as a MagicMock inline in the test file. but still failed to unpack iunto three values. it took three iterations before claude moved the mock setup into conftest.py with all edge cases covered.
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed? `python -m pytest tests/test_game_logic.py -v` from the project root. The tests `test_too_high_hint_says_go_lower` and `test_too_low_hint_says_go_higher` both passed, confirming the directions were no longer backwards. Before the fix, I could verify the bug by reading the code — `check_guess` returned "Go HIGHER!" when the guess was too high, which is the wrong direction.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  The pytest suite exposed that the score bug was broader than expected. The score oscillation test (`test_no_score_oscillation_across_attempts`) calculated the score across 6 consecutive "Too High" guesses and expected a steady -5 per attempt. Running it before the fix would have produced a zigzag, not a straight decline — which made the scoring meaningless regardless of how well you played.
- Did AI help you design or understand any tests? How?
  Yes. Claude helped write the 10 pytest cases, one per bug scenario. However, the mock setup for Streamlit required three rounds of back-and-forth before it worked — Claude's first two suggestions failed at import time. That taught me to always run the tests immediately after AI writes them rather than assuming they work.
---

## 4. What did you learn about Streamlit and state?

**Why the Secret Changed (Investigation Finding):**
While this wasn't observed through running the game, the code reveals that Streamlit's session state management is critical. If the secret was stored in a regular variable instead of `st.session_state.secret`, it would reset on every rerun (which happens every time the user interacts with the app). The fact that secret is stored in session state *should* prevent changes, but the bugs in the logic (like resetting attempts to 0) disrupt the expected flow.

**Understanding Streamlit Reruns:**
Streamlit reruns the entire script from top to bottom whenever the user interacts with a widget (like clicking a button or typing input). This means:
- Without session state, all variables would reset
- With session state, variables persist across reruns
- The UI doesn't "update"—it re-renders based on the current state values

**The Attempt Counter Problem:**
The "New Game" button (line 135) resets `attempts` to 0 instead of 1, which breaks the attempt-based logic elsewhere. When `attempts` becomes 0, then the first guess is recorded as `attempt_number=0`, causing all subsequent attempt-dependent logic to be off by one. This cascades through the string-conversion bug (which checks `attempt_number % 2 == 0`), making the second attempt (which is actually count=1) not trigger the string conversion.

**State Stability Issue:**
The code sets session state variables properly on initialization (lines 92-105), but the mutation logic (especially the attempt counter) is inconsistent, creating a brittle state machine where the order of operations matters greatly.


---

## 5. Looking ahead: your developer habits

**Habit to Reuse: "Test Before Trusting"**
This project reinforced the critical habit of not trusting code based on its appearance or the fact that it runs without crashing. The buggy code was syntactically correct and would execute, but it had fundamental logic errors. Going forward, I will always run code through realistic scenarios (even if just in my head or via simulation) before considering it "done." This applies especially to AI-generated code, which may look plausible but hide semantic errors.

**Different Approach for AI Collaboration:**
Next time I work with AI on a coding task, I would explicitly ask it to **justify its logic**, not just produce code. For example: "Why are you converting the secret to a string on even attempts?" or "How does this scoring system reflect player skill?" This would expose flawed reasoning before implementation.

**How This Changed My View of AI Code:**
This project showed me that AI-generated code is like code written by a developer who never tested it. It's syntactically competent but semantically broken. The AI can produce working code, but it doesn't think like a player—it doesn't simulate gameplay to catch logical contradictions. This means AI code requires the same rigor and testing as human code, if not more, because it's easy to overlook the subtle logic errors when the code "looks right."

