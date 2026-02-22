from datetime import datetime, timedelta


class FileTreeCache:
    """Cache simple pour arborescences (évite régénération)"""

    def __init__(self, ttl_seconds: int = 300):
        self.cache: dict[str, tuple[datetime, dict]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, project_id: str) -> dict | None:
        if project_id in self.cache:
            cached_at, tree = self.cache[project_id]
            if datetime.now() - cached_at < self.ttl:
                return tree
            else:
                del self.cache[project_id]
        return None

    def set(self, project_id: str, tree: dict):
        self.cache[project_id] = (datetime.now(), tree)

    def invalidate(self, project_id: str):
        if project_id in self.cache:
            del self.cache[project_id]

    def clear(self):
        self.cache.clear()


file_tree_cache = FileTreeCache()
