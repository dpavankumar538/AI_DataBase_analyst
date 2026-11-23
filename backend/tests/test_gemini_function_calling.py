
import time

from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY


MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)


# 1. Define a Python function
def get_dataset_summary(dataset_name: str) -> dict:
    """Return a sample summary for a dataset."""

    datasets = {
        "sales": {
            "total_rows": 1000,
            "columns": ["product", "quantity", "revenue"],
            "total_revenue": 250000,
            "average_revenue": 250
        }
    }

    return datasets.get(dataset_name.lower(), {
        "error": "Dataset not found"
    })


# 2. Declare the function to Gemini
tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_dataset_summary",
            description="Retrieve summary information about a dataset.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "dataset_name": {
                        "type": "STRING",
                        "description": "Name of the dataset"
                    }
                },
                "required": ["dataset_name"]
            }
        )
    ]
)


print("Testing complete Gemini function-calling cycle...")

start = time.perf_counter()

try:
    # 3. Send the question to Gemini
    response = client.models.generate_content(
        model=MODEL,
        contents="Analyze the sales dataset and tell me its total revenue.",
        config=types.GenerateContentConfig(
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY"
                )
            )
        )
    )

    # 4. Read Gemini's function call
    function_call = None

    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            if part.function_call:
                function_call = part.function_call
                break

        if function_call:
            break

    if not function_call:
        raise RuntimeError("Gemini did not request a function call.")

    print("\nFunction requested:", function_call.name)
    print("Arguments:", function_call.args)

    # 5. Execute the requested Python function
    if function_call.name == "get_dataset_summary":
        result = get_dataset_summary(
            dataset_name=function_call.args["dataset_name"]
        )
    else:
        raise ValueError("Unknown function requested.")

    print("\nPython function executed successfully.")
    print("Function result:", result)

    # 6. Send the function result back to Gemini

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="Analyze the sales dataset and tell me its total revenue."
                    )
                ]
            ),
            response.candidates[0].content,
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response=result
                    )
                ]
            )
        ],
        config=types.GenerateContentConfig(
            tools=[tool]
        )
    )


    elapsed = time.perf_counter() - start

    print("\n--- Final Gemini Answer ---")
    print(response.text)

    print(f"\nTotal execution time: {elapsed:.2f} seconds")

except Exception as error:
    elapsed = time.perf_counter() - start
    print(f"\nFailed after {elapsed:.2f} seconds")
    print(type(error).__name__, error)
