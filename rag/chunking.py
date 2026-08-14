def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Simple sliding-window chunker. chunk_size and overlap are in characters,
    not tokens — good enough for Day 4, can swap for a token-aware splitter later.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks