from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name

def delete_corpus(
        corpus_name: str,
        confirm: bool,
        tool_context: ToolContext) -> dict:
    """
    Eliminar un Vertex AI Corpus especifico en caso de que no sea mas necesario
    Este paso necesita una corfirmacion
    :param corpus_name: Nombre del corpus que sera eliminado
    :param confirm: Debe de ser ajustado a True para que pueda ser eliminado
    :param tool_context: Herramienta de contexto
    :return:
        dict: Status e informacion sobre el corpus que ha sido eliminado
    """

    # Verificar si el corpus existe
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name
        }

    # Confirmacion para eliminar el corpus
    if not confirm:
        return{
            "status": "error",
            "message": f"Corpus '{corpus_name}' no puede ser eliminado si no se realiza la confirmacion",
            "corpus_name": corpus_name
        }

    try:
        # Obtener nombre del recurso del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Eliminar el corpus
        rag.delete_corpus(corpus_resource_name)

        # Remover el estado ajustado a False
        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' eliminado satisfactoriamente",
            "corpus_name": corpus_name
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al eliminar el corpus {corpus_name}",
            "corpus_name": corpus_name
        }