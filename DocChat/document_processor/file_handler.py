"""Upload validation, chunking, and on-disk chunk cache."""

from __future__ import annotations

import hashlib
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from config import constants, settings
from utils.logging import logger


class DocumentProcessor:
    def __init__(self):
        self.headers = [("#", "Header 1"), ("##", "Header 2")]
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=150
        )

    def validate_files(self, files: List) -> None:
        total_size = 0
        for f in files:
            path = self._path(f)
            total_size += path.stat().st_size
        if total_size > constants.MAX_TOTAL_SIZE:
            raise ValueError(
                f"Total size exceeds {constants.MAX_TOTAL_SIZE // 1024 // 1024}MB limit"
            )

    def process(self, files: List) -> List[Document]:
        self.validate_files(files)
        all_chunks: List[Document] = []
        seen_hashes: set[str] = set()

        for file in files:
            try:
                path = self._path(file)
                with open(path, "rb") as fh:
                    file_hash = self._generate_hash(fh.read())
                cache_path = self.cache_dir / f"{file_hash}.pkl"

                if self._is_cache_valid(cache_path):
                    logger.info("Loading from cache: %s", path.name)
                    chunks = self._load_from_cache(cache_path)
                else:
                    logger.info("Processing: %s", path.name)
                    chunks = self._process_file(path)
                    self._save_to_cache(chunks, cache_path)

                for chunk in chunks:
                    chunk_hash = self._generate_hash(chunk.page_content.encode())
                    if chunk_hash not in seen_hashes:
                        all_chunks.append(chunk)
                        seen_hashes.add(chunk_hash)
            except Exception as e:
                logger.error("Failed to process %s: %s", file, e)
                continue

        logger.info("Total unique chunks: %s", len(all_chunks))
        return all_chunks

    def _path(self, file) -> Path:
        if isinstance(file, (str, Path)):
            return Path(file)
        name = getattr(file, "name", None) or getattr(file, "path", None)
        if not name:
            raise ValueError("Invalid upload")
        return Path(name)

    def _process_file(self, path: Path) -> List[Document]:
        suffix = path.suffix.lower()
        if suffix not in constants.ALLOWED_TYPES:
            logger.warning("Skipping unsupported type: %s", path.name)
            return []

        # Prefer Docling when available (course path); else local loaders
        try:
            from docling.document_converter import DocumentConverter

            markdown = (
                DocumentConverter()
                .convert(str(path))
                .document.export_to_markdown()
            )
            splitter = MarkdownHeaderTextSplitter(self.headers)
            chunks = splitter.split_text(markdown)
            if chunks:
                return chunks
            return self._splitter.create_documents([markdown])
        except Exception as e:
            logger.info("Docling unavailable/failed (%s); using fallback loaders", e)

        if suffix == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader

            docs = PyPDFLoader(str(path)).load()
        elif suffix == ".docx":
            from langchain_community.document_loaders import Docx2txtLoader

            docs = Docx2txtLoader(str(path)).load()
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if suffix == ".md":
                return MarkdownHeaderTextSplitter(self.headers).split_text(text) or (
                    self._splitter.create_documents([text])
                )
            docs = [Document(page_content=text, metadata={"source": str(path)})]

        return self._splitter.split_documents(docs)

    def _generate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _save_to_cache(self, chunks: List, cache_path: Path):
        with open(cache_path, "wb") as f:
            pickle.dump(
                {"timestamp": datetime.now().timestamp(), "chunks": chunks}, f
            )

    def _load_from_cache(self, cache_path: Path) -> List:
        with open(cache_path, "rb") as f:
            return pickle.load(f)["chunks"]

    def _is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return age < timedelta(days=settings.CACHE_EXPIRE_DAYS)
