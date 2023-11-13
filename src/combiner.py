from io import BytesIO
from math import ceil
from typing import List

from PIL import Image
from pypdf import PdfWriter


def combine_images_to_pdf(images: List[BytesIO]) -> BytesIO:
    # Create a new PDF file merger
    pdf_merger = PdfWriter()

    one_photo_max_size = 20_000_000 // len(images)

    # Loop through each image and add it as a new page to the PDF
    for image in images:
        # Open the image using PIL
        pil_image = Image.open(image)

        while image.getbuffer().nbytes > one_photo_max_size:
            new_size: tuple[int, int] = (
                ceil(pil_image.width / 1.1),
                ceil(pil_image.height / 1.1),
            )
            pil_image = pil_image.resize(new_size)
            image = BytesIO()
            pil_image.save(image, format="JPEG", optimize=True, quality=95)
            image.seek(0)

        # Create a new BytesIO object to hold the PDF data
        pdf_bytes = BytesIO()

        # Convert the image to PDF and save it to the BytesIO object
        pil_image.save(pdf_bytes, format="PDF")

        # Seek to the beginning of the BytesIO object
        pdf_bytes.seek(0)

        # Add the PDF page to the merger
        pdf_merger.append(pdf_bytes)

    # Create a new BytesIO object to hold the merged PDF data
    merged_pdf_bytes = BytesIO()

    # Write the merged PDF data to the BytesIO object
    pdf_merger.write(merged_pdf_bytes)

    pdf_merger.close()

    # Seek to the beginning of the BytesIO object
    merged_pdf_bytes.seek(0)

    # Return the merged PDF data
    return merged_pdf_bytes
