"""The module provides the BaseFaissAnn class, a base class for Faiss-based ANN.

It supports two types of indices:
Euclidean (L2) and inner-product (IP).

Classes:
    BaseFaissAnn: Manages the creation and querying of Faiss indices with support for both
    L2 and IP types. It allows embedding of vectors and querying for nearest neighbors
    within those embeddings.

Example usage:
    from numpy import array
    embeddings = array([...])
    ann = BaseFaissAnn(index_type="L2")
    ann._fit(embeddings)
    neighbors = ann.query(query_embedding, n_neighbors=5)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from faiss import IndexFlatIP, IndexFlatL2  # Make sure to import necessary Faiss classes
from numpy import dtype, float32, int32, ndarray
from torch import Tensor

from nltkp.modules.indices import BaseAnn
from nltkp.utils import LOGGER

if TYPE_CHECKING:
    from numpy.typing import NDArray


class BaseFaissAnn(BaseAnn):
    """Base class for Faiss-based Approximate Nearest Neighbor (ANN) methods.

    Attributes
    ----------
        index_type (str): Type of index, "L2" for Euclidean or "IP" for inner-product.
        index (Optional[faiss.IndexFlatL2 | faiss.IndexFlatIP]): The Faiss index object.
        embeddings (Optional[ndarray]): The embeddings stored in the index.

    """

    def __init__(self: BaseFaissAnn, index_type: str = "L2") -> None:
        """Initialize the BaseFaissAnn with a specific index type.

        Args:
        ----
            index_type (str): Specifies the type of Faiss index to create ("L2" or "IP").

        """
        super().__init__()
        self.index_type: str = index_type
        self.index: IndexFlatIP | IndexFlatL2
        self.embeddings: ndarray

    def _fit(self: BaseFaissAnn, embeddings: NDArray[float32]) -> None:
        """Initialize the Faiss index and add embeddings.

        Args:
        ----
            embeddings (NDArray[float32]): The data to fit into the ANN structure.

        """
        LOGGER.info(msg="Start fit BaseFaissAnn")
        if not isinstance(embeddings, ndarray):
            msg: str = f"Embeddings must be an ndarray, got {type(embeddings).__name__}"
            raise TypeError(msg)

        self.embeddings = embeddings
        d: int = embeddings.shape[1]
        if self.index_type == "L2":
            self.index = IndexFlatL2(d)
        elif self.index_type == "IP":
            self.index = IndexFlatIP(d)
        else:
            msg = "Invalid index type specified, use indexes as 'IP' or 'L2."
            raise ValueError(msg)

        self.index.add(embeddings)  # type: ignore  # noqa: PGH003
        LOGGER.info("Fit faiss (%s) with shape dim: %s", self.index_type, d)

    def query(
        self: BaseFaissAnn,
        embedding: Tensor | ndarray[Any, dtype[Any]],
        n_neighbors: int,
    ) -> tuple[NDArray[float32], NDArray[int32]]:
        """Query the index for nearest neighbors.

        Args:
        ----
            embedding (Tensor | ndarray[Any, dtype[Any]): Embedding vector query nearest neighbors.
            n_neighbors (int): The number of nearest neighbors to retrieve.

        Returns:
        -------
            tuple[NDArray[float32], ndarray]: Distances and indices of the nearest neighbors.

        Raises:
        ------
            ValueError: If the index has not been initialized.
            TypeError: If the embedding is not an ndarray.

        """
        if self.index is None:
            msg = "Index not initialized, please fit the model before querying."
            raise ValueError(msg)

        if not isinstance(embedding, ndarray):
            msg = "Query embedding must be an ndarray."
            raise TypeError(msg)

        if isinstance(embedding, Tensor):
            embedding = embedding.cpu().numpy()

        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)

        LOGGER.info("Query embedding with number of neighbors: %s", n_neighbors)

        indices: NDArray[int32]
        distances: NDArray[float32]
        distances, indices = self.index.search(embedding, n_neighbors)  # type: ignore  # noqa: PGH003
        return distances, indices  # Skipping self in results
