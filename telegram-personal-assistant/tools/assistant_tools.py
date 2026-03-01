"""Personal assistant tools - notes via database, knowledge via RAG."""

from connic.tools import db_insert, db_find, db_delete, query_knowledge, store_knowledge

NOTES_COLLECTION = "notes"
KNOWLEDGE_NAMESPACE = "personal"


async def save_note(title: str, content: str) -> dict:
    """Save a personal note. Use for quick facts, reminders, and things the user wants to remember.

    Args:
        title: Short label for the note (e.g. "dentist appointment", "wifi password").
        content: The note body. Include all relevant details.

    Returns:
        The saved note document.
    """
    result = await db_insert(NOTES_COLLECTION, {
        "title": title,
        "content": content,
    })
    return result["inserted"][0]


async def find_notes(query: str = "") -> list[dict]:
    """Search saved notes. Returns up to 20 matching notes ordered by most recent.

    Args:
        query: Search term to filter by title. Leave empty to list all recent notes.

    Returns:
        List of matching note documents.
    """
    filter_dict = {}
    if query.strip():
        filter_dict = {"title": {"$regex": query}}

    result = await db_find(
        NOTES_COLLECTION,
        filter=filter_dict,
        sort={"_created_at": -1},
        limit=20,
    )
    return result.get("documents", [])


async def delete_note(note_id: str) -> dict:
    """Delete a note by its ID.

    Args:
        note_id: The _id of the note to delete (from find_notes results).

    Returns:
        Deletion result.
    """
    return await db_delete(NOTES_COLLECTION, filter={"_id": note_id})


async def search_knowledge(query: str) -> list[dict]:
    """Search the personal knowledge base for longer-form stored information.

    Use this for articles, meeting summaries, reference material, or anything
    the user stored with remember_knowledge.

    Args:
        query: Describe what you're looking for (e.g. "meeting notes from last week").

    Returns:
        List of matching knowledge entries with content and relevance score.
    """
    result = await query_knowledge(query, namespace=KNOWLEDGE_NAMESPACE, max_results=5)
    return result.get("results", [])


async def remember_knowledge(content: str, entry_id: str | None = None) -> dict:
    """Store information in the personal knowledge base for later retrieval.

    Best for longer content like summaries, articles, how-tos, or reference
    material. For short facts and reminders, use save_note instead.

    Args:
        content: The information to store. Be descriptive so it can be found later.
        entry_id: Optional stable ID for updates (e.g. "project-roadmap"). If an
                  entry with this ID exists, it will be replaced.

    Returns:
        Store result with entry_id.
    """
    return await store_knowledge(
        content, namespace=KNOWLEDGE_NAMESPACE, entry_id=entry_id
    )
