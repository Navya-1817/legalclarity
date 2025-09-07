import vertexai
from vertexai.generative_models import GenerativeModel

def explain_legal_text(project_id: str, location: str, text_to_explain: str) -> str:
    """Uses the Gemini model to explain a legal clause in simple terms."""

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Load the model
    # We use 'gemini-1.5-flash' because it's fast and cost-effective for this task.
    model = GenerativeModel("gemini-1.5-flash-001")

    # This is our instruction to the AI.
    # We give it a role, the text, and a clear command.
    prompt = f"""
    You are an expert legal assistant who explains complex terms in simple, easy-to-understand language for a non-lawyer.

    Explain the following legal clause:
    "{text_to_explain}"

    Your explanation should be clear and concise.
    """

    # Send the prompt to the model and get the response
    response = model.generate_content(prompt)
    
    return response.text


# --- Main execution ---
if __name__ == "__main__":
    # 1. CONFIGURE YOUR DETAILS HERE
    import os
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-project-id-here')  # Load from environment
    GCP_LOCATION = "us-central1"           # You can change this to your preferred region

    # 2. THIS IS THE LEGAL TEXT WE WANT TO EXPLAIN
    legal_clause = "Notwithstanding any other provision of this Agreement, the total liability of the Service Provider, whether in contract, tort (including negligence), or otherwise, shall be limited to the aggregate amount of fees paid by the Client hereunder."

    # 3. RUN THE FUNCTION AND PRINT THE RESULT
    print("Analyzing legal clause...")
    print("-" * 20)
    
    explanation = explain_legal_text(
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        text_to_explain=legal_clause
    )

    print("Simple Explanation:")
    print(explanation)