import aiohttp

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

async def download_image(url: str) -> bytes | None:
    """Download an image from a URL with 10s timeout."""
    try:
        headers = {"User-Agent": _USER_AGENT}
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
    except Exception:
        pass
    return None

def chunk_text(text: str, max_length: int = 1900) -> list[str]:
    """Chunk text into pieces smaller than max_length, preferably at newlines."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
            
        # Find the last newline within the max_length
        split_idx = text.rfind('\n', 0, max_length)
        if split_idx == -1:
            # If no newline, find the last space
            split_idx = text.rfind(' ', 0, max_length)
            if split_idx == -1:
                # If no space, just cut exactly at max_length
                split_idx = max_length
                
        chunks.append(text[:split_idx].strip())
        text = text[split_idx:].strip()
        
    return chunks

def format_history_for_summary(messages: list) -> str:
    """Format a list of Discord message objects into a string for summarization."""
    formatted = []
    for msg in messages:
        author = msg.author.display_name
        content = msg.clean_content
        if content:
            formatted.append(f"{author}: {content}")
    return "\n".join(formatted)

def is_image_attachment(attachment) -> bool:
    """Check if a Discord attachment is an image based on content_type."""
    if attachment.content_type is None:
        return False
    return attachment.content_type.startswith("image/")
