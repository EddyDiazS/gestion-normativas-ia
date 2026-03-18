import os
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

from PyPDF2 import PdfReader
from docx import Document


ARTICLE_LINE_REGEX = re.compile(
    r"^\s*articulo\s+(?:no\.\s*)?(\d+|[ivxlcdm]+)\b",
    re.IGNORECASE,
)


def _normalize_for_match(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_accents = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    )
    return re.sub(r"\s+", " ", without_accents).strip().lower()


def _extract_text(path: str, file_name: str) -> str:
    text = ""
    lower = file_name.lower()

    if lower.endswith(".pdf"):
        reader = PdfReader(path)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text

    if lower.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    if lower.endswith(".docx"):
        try:
            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml")

            root = ET.fromstring(document_xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for paragraph in root.findall(".//w:p", ns):
                nodes = [node.text for node in paragraph.findall(".//w:t", ns) if node.text]
                if nodes:
                    paragraphs.append("".join(nodes))

            if paragraphs:
                return "\n".join(paragraphs)
        except Exception:
            # Fallback parser for uncommon DOCX variants.
            pass

        doc = Document(path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    return ""


def _split_by_article_lines(text: str):
    lines = text.splitlines()
    blocks = []
    current_article = None
    current_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            if current_lines:
                current_lines.append("")
            continue

        match = ARTICLE_LINE_REGEX.match(_normalize_for_match(line))
        if match:
            if current_article and current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    blocks.append((current_article, content))

            token = match.group(1).upper()
            if token.isdigit():
                token = str(int(token))
            current_article = f"ARTÍCULO {token}"
            current_lines = [line]
            continue

        if current_article:
            current_lines.append(line)

    if current_article and current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            blocks.append((current_article, content))

    return blocks


def load_documents(folder_path: str):
    documents = []

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            path = os.path.join(root, file_name)

            try:
                text = _extract_text(path, file_name)
                if not text.strip():
                    continue

                source_type = (
                    "original" if file_name.lower().endswith(".docx") else "secondary"
                )
                article_blocks = _split_by_article_lines(text)

                if not article_blocks:
                    documents.append(
                        {
                            "content": text.strip(),
                            "metadata": {
                                "document": file_name,
                                "article": "N/A",
                                "source_type": source_type,
                            },
                        }
                    )
                    continue

                for article, body in article_blocks:
                    documents.append(
                        {
                            "content": body,
                            "metadata": {
                                "document": file_name,
                                "article": article,
                                "source_type": source_type,
                            },
                        }
                    )

            except Exception as error:
                print(f"Error leyendo {file_name}: {error}")

    print(f"Documentos cargados: {len(documents)}")
    return documents
