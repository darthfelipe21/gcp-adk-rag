import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    DEFAULT_EMBEDDING_MODEL,
)
from .utils import check_corpus_exists

def create_corpus(corpus_name: str, tool_context: ToolContext) -> dict:
    """
    Crear un nuevo corpus en Vertex AI, con un nombre especifico

    Args:
        corpus_name (str): Nombre del corpus
        tool_context (ToolContext): Herramienta de context para la gestión del estado

    Return:
        dict: Status sobre la information de la operación
    """
    # Verificar si el corpus ya existe
    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "info",
            "message": f"Corpus '{corpus_name}' ya existe",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }
    try:
        # Limpiar el nombre del corpus que sera creado
        display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)

        # Configurar el modelo de embedding
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=DEFAULT_EMBEDDING_MODEL
            )
        )

        #Crear corpus
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        # Actualizar el estado y rastrear el corpus
        tool_context.state[f"corpus_exisits_{corpus_name}"] = True

        # Configurar como corpus actual
        tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' creado exitosamente",
            "corpus_name": rag_corpus.name,
            "display_name": rag_corpus.display_name,
            "corpus_created": True
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al crear el corpus: {str(e)}",
            "corpus_name": corpus_name,
            "corpus_created": False
        }

