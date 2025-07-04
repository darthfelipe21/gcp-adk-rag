import re
from typing import List

from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from .utils import check_corpus_exists, get_corpus_resource_name

from ..config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)

def add_data(
        corpus_name: str,
        paths: List[str],
        tool_context: ToolContext,
) -> dict:
    """
    Agregar nueva fuente de datos a un corpus especifico
    :param corpus_name: Nombre dle corpus al que se agregara la data
    :param paths: Lsita de URLs del cloud storage para agregar al corpus
        Formato aceptado:
            - Google Drive: "https://drive.google.com/file/d/{file_id}/view"
            - Google docs/sheets/slides: "https://docs.google.com/{type}/d/{file_id}/..."
            - Google Cloud Storage: "gs://{bucket_name}/{path_to_file}"
    :param tool_context: Contexto de la herramienta
    :return:
        dict: Informacion sobre el data agregada y su status
    """
    # Verificar si el orpus existe
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name,
            "paths": paths,
        }
    # Validar los inputs
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Path invalido, por favor ingresar un formato correcto (Drive, GCS, Google docs/sheets/slides)",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Preprocesar los paths para validar y convertir Google Docs URLs a un formato de Drive si es necesario
    validate_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (no es un string valido)")
            continue

        # Chekear Google docs/sheets/slides URLs y convertirlos en formato de Drive
        docs_match = re.match(
            r"https://docs\.google\.com/(?:document|spreadsheets|presentation)/d/([a-zA-Z0-9_-]+)(?:/|$)", path
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validate_paths.append(drive_url)
            conversions.append(f"{path} -> {drive_url}")
            continue

        # Chekear que el Drive URL sea valido
        drive_match = re.match(
            r"https://drive\.google\.com/(?:file/d/|open\?id=)([a-zA-Z0-9_-]+)(?:/|$)", path
        )
        if drive_match:
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validate_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} -> {drive_url}")
            continue

        # Chekear GCP path
        if path.startswith("gs://"):
            validate_paths.append(path)
            continue

        # Informacion dentro de esta variable no es un formato valido
        invalid_paths.append(f"{path} (no es un path valido)")


    # Verificar si tenemos algun path valido despues de la validacion
    if not validate_paths:
        return {
            "status": "error",
            "message": "No se ha ingresado un path valido",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths
        }

    try:
        # Obtener el nombre corpus
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configurar el chunking
        transformation_config = rag.TrasnformationConfig(
            chunking_config=rag.ChunkingConfig(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            )
        )

        # Importar archivos al corpus
        import_result = rag.import_files(
            corpus_resource_name,
            validate_paths,
            transformation_config =transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN
        )

        # Preparar el corpus como acutal si es que no lo esta
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name


        # Todo salio bien mensaje
        conversaion_msg = ""
        if conversions:
            convertion_msg = "(Convertido Google Docs URLs a formato Drive)"

        return {
            "status": "success",
            "message": f"Agregado satisfactorio { import_result.imported_rag_files_count}:  archivos{conversaion_msg} en corpus {corpus_name}",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validate_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "No se ha ingresado un path valido",
            "corpus_name": corpus_name,
            "paths": paths
        }












