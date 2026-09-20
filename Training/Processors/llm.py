from dotenv import load_dotenv
from groq import Groq
load_dotenv()
groq=Groq()


def classify_with_llm(log_message):
    prompt = f"""CLassify the following log message into one of the following categories: 1)'Workflow Error', 2)'Deprecation Warning'. If the log message does not fit into any of these categories, return 'Unclassified'.
    Only return the category name, do not provide any explanation or preamble. Log message: {log_message}
    
    """
    chat_completion = groq.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "user",
            "content": "What is the capital of France?"}
        ]
    )
    print(prompt.choices[0].message.content)
    

