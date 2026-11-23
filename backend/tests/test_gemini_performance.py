
import time
from app.ai.llm.gemini import GeminiLLMProvider

llm = GeminiLLMProvider()

prompt = """
Explain the Turing Test in artificial intelligence
in approximately 100 words. Use simple language.
"""

print("Testing Gemini generation independently...")

start = time.perf_counter()

try:
    answer = llm.generate_response(prompt)

    elapsed = time.perf_counter() - start

    print("\n--- Gemini Performance ---")
    print(f"Generation time: {elapsed:.2f} seconds")
    print("\n--- Answer ---")
    print(answer)

except Exception as error:
    elapsed = time.perf_counter() - start
    print(f"\nRequest failed after {elapsed:.2f} seconds")
    print(type(error).__name__, error)
