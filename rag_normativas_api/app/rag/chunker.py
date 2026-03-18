import re


def divide_by_articles(documents):
    chunks = []

    pattern = re.compile(
        r"(ARTÍCULO|Artículo)\s+([0-9IVXLCDM]+)",
        re.IGNORECASE
    )

    for doc in documents:
        content = doc["content"]
        metadata = doc.get("metadata", {})
        matches = list(pattern.finditer(content))

        # Si no hay artículos, se guarda todo como un solo chunk
        if not matches:
            chunks.append({
                "content": content,
                "metadata": {
                    **metadata,
                    "article": "N/A"
                }
            })
            continue

        # Si hay artículos, se divide correctamente
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            chunks.append({
                "content": content[start:end],
                "metadata": {
                    **metadata,
                    "article": match.group(2)
                }
            })

    print(f"🧩 Chunks creados: {len(chunks)}")
    return chunks
