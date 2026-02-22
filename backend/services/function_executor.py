import logging

from backend.db.database import Database
from backend.services.file_service import FileService

logger = logging.getLogger(__name__)


class FunctionExecutionError(Exception):
    pass


class FunctionExecutor:
    """
    Exécute les tool_calls retournés par les LLM providers.
    Dispatch vers les fonctions appropriées selon le nom de la fonction.
    """

    def __init__(self, db_instance: Database, project_path: str | None = None):
        self.db = db_instance
        self.project_path = project_path

    def get_available_functions(self) -> list[dict]:
        """
        Retourne la liste des fonctions disponibles au format standard JARVIS.
        
        Returns:
            Liste de fonctions avec name, description, parameters
        """
        return [
            {
                "name": "get_project_file",
                "description": "Lit le contenu d'un fichier du projet en cours",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Chemin relatif du fichier à lire",
                        }
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "get_project_structure",
                "description": "Récupère l'arborescence du projet en cours",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_depth": {
                            "type": "integer",
                            "description": "Profondeur maximale de l'arborescence (défaut: 3)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "get_library_document",
                "description": "Recherche et retourne un document de la Knowledge Base",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nom du document à rechercher",
                        },
                        "category": {
                            "type": "string",
                            "description": "Catégorie optionnelle pour filtrer",
                        },
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "get_library_list",
                "description": "Liste les documents disponibles dans la Knowledge Base",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Catégorie optionnelle pour filtrer",
                        },
                        "agent": {
                            "type": "string",
                            "description": "Agent optionnel pour filtrer",
                        },
                    },
                    "required": [],
                },
            },
        ]

    async def execute(self, function_name: str, arguments: dict) -> dict:
        """
        Dispatch vers la fonction appropriée.

        Args:
            function_name: Nom de la fonction à exécuter
            arguments: Arguments de la fonction (dict)

        Returns:
            dict: Résultat de l'exécution

        Raises:
            FunctionExecutionError: Si la fonction n'existe pas ou échoue
        """
        try:
            if function_name == "get_library_document":
                return await self.get_library_document(**arguments)
            elif function_name == "get_library_list":
                return await self.get_library_list(**arguments)
            elif function_name == "get_project_file":
                return await self.get_project_file(**arguments)
            elif function_name == "get_project_structure":
                return await self.get_project_structure(**arguments)
            else:
                raise FunctionExecutionError(f"Unknown function: {function_name}")
        except Exception as e:
            logger.error(f"Function execution failed: {function_name} - {str(e)}")
            raise FunctionExecutionError(f"Execution failed: {str(e)}") from e

    async def get_library_document(self, name: str, category: str | None = None) -> dict:
        """
        Recherche et retourne un document de la Knowledge Base.

        Args:
            name: Nom du document à rechercher
            category: Catégorie optionnelle pour filtrer

        Returns:
            dict: Document trouvé ou erreur
        """
        try:
            docs = await self.db.list_library_documents(category=category, search=name)

            if not docs:
                return {"success": False, "error": f"Document '{name}' not found in Knowledge Base"}

            # Recherche exacte du nom
            exact_match = next((doc for doc in docs if doc["name"].lower() == name.lower()), None)

            if exact_match:
                return {
                    "success": True,
                    "document": {
                        "name": exact_match["name"],
                        "category": exact_match["category"],
                        "description": exact_match["description"],
                        "content": exact_match["content"],
                        "tags": exact_match["tags"],
                        "agents": exact_match["agents"],
                    },
                }

            # Si pas de correspondance exacte, retourner le premier résultat
            first_doc = docs[0]
            return {
                "success": True,
                "document": {
                    "name": first_doc["name"],
                    "category": first_doc["category"],
                    "description": first_doc["description"],
                    "content": first_doc["content"],
                    "tags": first_doc["tags"],
                    "agents": first_doc["agents"],
                },
                "note": "Exact match not found, returning closest match",
            }
        except Exception as e:
            logger.exception(f"get_library_document failed for name={name}, category={category}")
            return {"success": False, "error": str(e)}

    async def get_library_list(
        self, category: str | None = None, agent: str | None = None
    ) -> dict:
        """
        Liste les documents disponibles dans la Knowledge Base.

        Args:
            category: Catégorie optionnelle pour filtrer
            agent: Agent optionnel pour filtrer

        Returns:
            dict: Liste des documents
        """
        try:
            docs = await self.db.list_library_documents(category=category, agent=agent)

            return {
                "success": True,
                "count": len(docs),
                "documents": [
                    {
                        "name": doc["name"],
                        "category": doc["category"],
                        "description": doc["description"],
                        "tags": doc["tags"],
                        "agents": doc["agents"],
                    }
                    for doc in docs
                ],
            }
        except Exception as e:
            logger.exception(f"get_library_list failed for category={category}, agent={agent}")
            return {"success": False, "error": str(e)}

    async def get_project_file(self, file_path: str) -> dict:
        """
        Lit le contenu d'un fichier du projet en cours.

        Args:
            file_path: Chemin relatif du fichier

        Returns:
            dict: Contenu du fichier ou erreur
        """
        if not self.project_path:
            return {"success": False, "error": "No project context available"}

        try:
            file_content = FileService.read_file(self.project_path, file_path)

            # FileContent est un objet Pydantic, le convertir en dict
            file_dict = (
                file_content.model_dump() if hasattr(file_content, "model_dump") else file_content
            )

            return {
                "success": True,
                "file_path": file_path,
                "content": file_dict.get("content", ""),
                "size": file_dict.get("size", 0),
            }
        except Exception as e:
            logger.exception(f"get_project_file failed for file_path={file_path}")
            return {"success": False, "error": f"Failed to read file: {str(e)}"}

    async def get_project_structure(self, max_depth: int = 3) -> dict:
        """
        Récupère l'arborescence du projet en cours.

        Args:
            max_depth: Profondeur maximale de l'arborescence

        Returns:
            dict: Arborescence du projet ou erreur
        """
        if not self.project_path:
            return {"success": False, "error": "No project context available"}

        try:
            tree = FileService.get_file_tree(self.project_path, max_depth)

            return {"success": True, "project_path": self.project_path, "tree": tree}
        except Exception as e:
            logger.exception(f"get_project_structure failed for max_depth={max_depth}")
            return {"success": False, "error": f"Failed to get project structure: {str(e)}"}
