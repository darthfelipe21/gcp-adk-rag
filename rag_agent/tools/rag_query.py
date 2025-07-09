import logging

from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name

from ..config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
)

def rag_query(
        corpus_name: str,
        query: str,
        tool_context: ToolContext) -> dict:
    """
    Ai Vertex Rag Corpus tenga la capacidad de responder onsultas sobre la informacion almacenada en un corpus
    :param corpus_name: Nombre del corpus con el que se esta respondiendo u obteniendo respuesta
    :param query: Texto que se estara buscando en el corpus para la respuesta
    :param tool_context: Contexto de la herramienta
    :return:
        dict: Informacion sobre la respuesta y su status
    """
    try:
        # Verificar si el corpus existe
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' no existe",
                "corpus_name": corpus_name
            }
        # Obtener el nombre de recurso del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configurar parametros de recuperacion (retrieval)
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD)  # Se refiere a la busqueda de vectores en relacion a nuestra consulta
        )

        # Realizar la consulta
        print("Realizando la recuperacion de la consulta...")
        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=corpus_resource_name)],
            text=query,
            rag_retrieval_config=rag_retrieval_config
        )
        # Procesar la respuesta de la consulta de una manera mas vistoza
        results = []
        if hasattr(response, 'contexts') and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri
                        if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source_name
                        if hasattr(ctx_group, "source_name") else ""
                    ),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0
                }
                results.append(result)
        # Si no se consigue ningun resultado
        if not results:
            return {
                "status": "error",
                "message": f"No se encontraron resultados para la consulta en el corpus {corpus_name} para la consulta {query}",
                "query": query,
                "corpus_name": corpus_name,
                "results": [],
                "results_count": 0
            }

        return {
            "status": "success",
            "message": f"Respuesta encontrada para la consulta '{query}' en el corpus '{corpus_name}'",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results)
        }

    except Exception as e:
        error_msg = f"Error querying corpus {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": corpus_name
        }
