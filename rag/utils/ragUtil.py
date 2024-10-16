from PIL.Image import Image
from pdf2image import convert_from_path
import os
import base64
import io

from filesystem.models import FileModel
from rag.utils.llmUtil import summarize_text, summarize_text_with_image, generate_embeddings


def debug_print(message: str):
    if os.getenv('CONSOLE_DEBUG', 'false').lower() == 'true':
        print(f"\033[92m{message}\033[0m")  # ANSI escape code for green


def txt_to_summary(txtFilePath: str) -> str:
    debug_print(f"Reading text file from {txtFilePath}")
    with open(txtFilePath, 'r') as file:
        text = file.read()
    debug_print("Summarizing text")
    return summarize_text(text)


def pdf_to_summaries_per_page(pdfFilePath: str) -> list[str]:
    debug_print(f"Generating summaries for each page in {pdfFilePath}")

    images = convert_from_path(pdfFilePath)

    base64_images = []

    # Iterate through the list of images
    for img in images:
        # Create a BytesIO object to hold the image
        buffered = io.BytesIO()

        # Save the image to the BytesIO object in PNG format
        img.save(buffered, format="PNG")

        # Get the image data from the BytesIO object
        img_data = buffered.getvalue()

        # Encode the image data to Base64
        base64_string = base64.b64encode(img_data).decode('utf-8')

        # Append the Base64 string to the list
        base64_images.append(base64_string)

    summaries = []
    for image_base64 in base64_images:
        debug_print("Summarizing image")
        summaries.append(summarize_text_with_image("", image_base64))
    return summaries


def file_to_summaries(fileInstance: FileModel) -> list[str]:
    type = fileInstance.file_type
    debug_print(f"Processing file of type {type}")
    if type == 'plain':
        return [txt_to_summary(fileInstance.file.path)]
    elif type == 'pdf':
        return pdf_to_summaries_per_page(fileInstance.file.path)
    else:
        raise ValueError(f"File type {type} is not supported for RAG")


def summary_to_embeddings(summary: str) -> list[list[float]]:
    debug_print("Generating embeddings for summary")
    return generate_embeddings(summary)
