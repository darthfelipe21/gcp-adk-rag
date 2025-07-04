from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name

def delete_document(
        corpus_name: str,
        document_id: str,
        tool_context: ToolContext) -> dict:
    """
    Eliminar un documento especifico dentro del corpus actual
    :param corpus_name: Nombre del corpus de donde se quiere borrar el documento
    :param document_name: Nombre del documento que se quiere eliminar
    :param tool_context: Herramienta de contexto
    :return:
        dict: Status e infromacion del documento eliminado
    """

    # Verificar si el corpus existe
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name,
            "dcoument_id": document_id
            }

    try:
        # Obtener nombre del recurso del corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Eliminar documento
        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        rag.delete_file(rag_file_path)

        return {
            "status": "success",
            "message": f"Documento '{document_id}' eliminado satisfactoriamente del corpus '{corpus_name}",
            "corpus_name": corpus_name,
            "document_id": document_id
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al eliminar el documento {document_id} del corpus {corpus_name}",
            "corpus_name": corpus_name,
            "document_id": document_id
        }