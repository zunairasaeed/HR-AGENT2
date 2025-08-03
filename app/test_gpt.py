from llm_utils import call_gpt

response = call_gpt(
    "You are a helpful assistant.",
    "Give me 3 resume bullet points for a Python Developer."
)
print("GPT Response:\n", response)
