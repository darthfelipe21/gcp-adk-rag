import logging
import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    LOCATION,
    PROJECT_ID,
)

logger = logging.getLogger(__name__)


def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convierte el nombre de un corpus en el nombre completo de su recurso si es necesario.
    Administra varios formatos de entrada y garantiza que el nombre devuelto cumpla con los requisitos de Vertex AI.

    Args:
        corpus_name (str): Nombre del corpus

    Returns:
        str: Nombre completo del recurso del corpus
    """
    logger.info(f"Getting resource name for corpus: {corpus_name}")

    # Si ya es un nombre de recurso completo con el formato proyectos/ubicaciones/ragCorpora
    if re.match(r"^projects/[^/]+/locations/[^/]+/ragCorpora/[^/]+$", corpus_name):
        return corpus_name

    # Comprobar si este es un nombre para mostrar de un corpus existente
    try:
        # Enumerar todos los corpus y verifique si hay una coincidencia con el nombre para mostrar
        corpora = rag.list_corpora()
        for corpus in corpora:
            if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
                return corpus.name
    except Exception as e:
        logger.warning(f"Error when checking for corpus display name: {str(e)}")
        # Si no se puede comprobar, continuamos con el comportamiento predeterminado
        pass

    # Si contiene elementos de ruta parciales, extraer solo el ID del corpus
    if "/" in corpus_name:
        # Extarer la ultima parte del path como el corpus ID
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name

    # Eliminar cualquier caracter especial que podria causar un problema
    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    # Construir nombre de recurso estandarizado
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Verificair si el corpus indicado existe

    Args:
        corpus_name (str): Nombre del corpus a verificar
        tool_context (ToolContext): Herramienta de contexto para administrar el estado

    Returns:
        bool: True si el corpus existe de lo contrario False
    """
    # Verificar el estado si tool_context fue provisto
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True

    try:
        # Obtener nombre del recurso completo
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Listar todos los corpora y verificar si este existe
        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):
                # Actualizar el estado
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                # Asignar el nuevo corpus como actual si es que no lo es
                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking if corpus exists: {str(e)}")
        # Si no puede verificar, se asume que no existe
        return False


def set_current_corpus(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Asignar el nuevo corpus con el estado del tool context 

    Args:
        corpus_name (str): Nombre del corpus que sera el actual
        tool_context (ToolContext): Herramienta de contexto para administrar el estado

    Returns:
        bool: True si el corpus existe de lo contrario False
    """
    # Verificar si el corpus existe
    if check_corpus_exists(corpus_name, tool_context):
        tool_context.state["current_corpus"] = corpus_name
        return True
    return False
