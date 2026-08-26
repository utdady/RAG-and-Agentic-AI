"""Chunk LinkedIn JSON and build a LlamaIndex vector store."""

from __future__ import annotations

import json
import logging
from typing import Any, List, Optional

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from modules.llm_interface import create_embedding_model
import config

logger = logging.getLogger(__name__)


def split_profile_data(profile_data: dict[str, Any]) -> List:
    """Split LinkedIn profile JSON into sentence nodes."""
    try:
        document = Document(text=json.dumps(profile_data))
        splitter = SentenceSplitter(chunk_size=config.CHUNK_SIZE)
        nodes = splitter.get_nodes_from_documents([document])
        logger.info("Created %s nodes from profile data", len(nodes))
        return nodes
    except Exception as e:
        logger.error("Error in split_profile_data: %s", e)
        return []


def create_vector_database(nodes: List) -> Optional[VectorStoreIndex]:
    """Embed nodes into an in-memory VectorStoreIndex."""
    try:
        embedding_model = create_embedding_model()
        index = VectorStoreIndex(
            nodes=nodes,
            embed_model=embedding_model,
            show_progress=True,
        )
        logger.info("Vector database created successfully")
        return index
    except Exception as e:
        logger.error("Error in create_vector_database: %s", e)
        return None


def verify_embeddings(index: VectorStoreIndex) -> bool:
    """Best-effort check that nodes have embeddings."""
    try:
        vector_store = index._storage_context.vector_store
        node_ids = list(index.index_struct.nodes_dict.keys())
        missing = False
        for node_id in node_ids:
            embedding = vector_store.get(node_id)
            if embedding is None:
                logger.warning("Node ID %s has a None embedding.", node_id)
                missing = True
        if missing:
            logger.warning("Some node embeddings are missing")
            return False
        logger.info("All node embeddings are valid")
        return True
    except Exception as e:
        # Some vector store backends don't expose get() the same way — non-fatal
        logger.warning("Could not verify embeddings (%s); continuing.", e)
        return True
