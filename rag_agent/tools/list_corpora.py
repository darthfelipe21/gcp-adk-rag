from vertexai import rag
from typing import Dict, List, Union

def list_corpora() -> dict:
    """
    Lista todos corpus disponibles en Vertex AI

    :return:
        dict: una lista de todos los corpus disponibles y su status y contenido dentro de el
            - resource_name: Nombre ocmpleto del recurso
            - display_name: nombre del corpus leible para una persona
            - create_time: cuando el corpus fue creado
            - update_time: cuando fue la ultima actualizacion del corpus
    """
    try:
        # Obtener lista de corpus
        corpora = rag.list_corpora()

        # Procesar todo la informaicon del corpus en un formato mas legible
        corpus_info: List[Dict[str, Union[str, int]]] = []
        for corpus in corpora:
            corpus_data: Dict[str, Union[str, int]] = {
                "resource_name": corpus.name,
                "display_name": corpus.display_name,
                "create_time": (str(corpus.create_time) if hasattr(corpus, 'create_time') else ""),
                "update_time": (str(corpus.update_time) if hasattr(corpus, 'update_time') else ""),
            }
            corpus_info.append(corpus_data)

        return {
            "status": "success",
            "message": f"Encontrado {len(corpus_info)} corpora disponible",
            "corpora": corpus_info,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al listar corpus: {str(e)}",
            "corpora": []
        }