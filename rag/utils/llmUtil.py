import os
import re
from together import Together
from PIL.Image import Image

together_client = Together()
prompt = open("rag/utils/prompt.txt", "r").read()

# using the same model because pricing is the same and it supports images
textOnly_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
visualLLM_model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"

max_tokens = 2048

# Function to print in yellow if CONSOLE_DEBUG is true


def debug_print(text):
    if os.getenv('CONSOLE_DEBUG', 'false').lower() == 'true':
        print(f"\033[93m{text}\033[0m")


def summarize_text(text: str) -> str:
    debug_print("Starting text summarization...")
    response = together_client.chat.completions.create(
        model=textOnly_model,
        messages=[
            {"role": "user", "content": prompt + "\n\n" + text}
        ],
        max_tokens=max_tokens
    )
    debug_print("Received response for text summarization.")
    return response.choices[0].message.content


def summarize_text_with_image(text: str, image_base64: str) -> str:
    debug_print("Starting text and image summarization...")

    # send to LLM
    response = together_client.chat.completions.create(
        model=visualLLM_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    },
                ],
            }
        ],
        max_tokens=max_tokens
    )
    debug_print("Received response for text and image summarization.")
    return response.choices[0].message.content


embedding_model = "BAAI/bge-base-en-v1.5"
embedding_dimensions = 768
embedding_max_tokens = 256


def generate_embeddings(text: str) -> list[list[float]]:
    debug_print("Starting embeddings generation...")
    # Tokenize the text by splitting on spaces
    tokens = re.findall(r'\S+\s*', text)

    # Split tokens into chunks of embedding_max_tokens
    chunks = [tokens[i:i+embedding_max_tokens]
              for i in range(0, len(tokens), embedding_max_tokens)]

    # convert chunks, list of tokens, to text
    chunks = [''.join(chunk) for chunk in chunks]

    response = together_client.embeddings.create(
        model=embedding_model,
        input=chunks
    )

    debug_print("Received response for embeddings.")

    # Extract embeddings from the response
    embeddings = [item.embedding for item in response.data]

    return embeddings
