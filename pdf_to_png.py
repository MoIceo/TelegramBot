import fitz
import os

def pdf_to_png(pdf_path, output_folder="output_images", dpi=200):
    os.makedirs(output_folder, exist_ok=True)

    pdf = fitz.open(pdf_path)
    for page_index, page in enumerate(pdf):
        zoom = dpi / 72  # 72 DPI — стандарт PDF
        matrix = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(matrix=matrix)
        output_path = os.path.join(output_folder, f"page_{page_index + 1}.png")

        pix.save(output_path)
        print(f"Saved: {output_path}")

    pdf.close()


if __name__ == "__main__":
    pdf_to_png("input.pdf")
