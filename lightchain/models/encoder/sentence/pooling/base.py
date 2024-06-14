"""The module defines the BasePooling class and associated functions.

Token pooling strategies are used to aggregate or transform sets of token embeddings,
into a single representation,
which can be beneficial in various natural language processing tasks to reduce dimensionality,
and capture important features of the data.

The module provides several pooling methods such as:
- CLS token pooling: Uses the embedding of the CLS token as the representation.
- Maximum token pooling: Selects the maximum value over all tokens.
- Mean token pooling: Calculates the arithmetic mean of tokens.
- Mean square root token pooling: Calculates the square root of the mean of tokens.
- Weighted mean token pooling: Applies a weighted mean operation on tokens.

These pooling strategies can be configured dynamically when an instance of BasePooling is created.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from torch._tensor import Tensor

from .func import pooling_funcs

if TYPE_CHECKING:
    from collections.abc import Callable

    from torch import Tensor


class BasePooling:
    """A class for applying various token pooling operations based on configuration flags.

    Attributes:
    ----------
    word_embedding_dimension (int): Dimensionality of the word embeddings.
    pooling_functions (Sequence[Callable]): A list of pooling function callables.

    Methods:
    -------
    __init__(self, word_embedding_dimension: int, **pooling_modes: bool):
        Initializes the Pooling instance with specified embedding dimension and pooling modes.

    apply_pooling(self, output_vectors: List[torch.Tensor], features: Dict[str, Any],
        token_embeddings: torch.Tensor) -> None:
        Applies the selected pooling functions to the given token embeddings.

    Args:
    ----
        word_embedding_dimension (int): The dimension of the embeddings used for pooling.
        **pooling_modes (bool): Arbitrary keyword arguments where keys are the mode.

    Example usage:
    --------------
        pooling_instance = Pooling(
            word_embedding_dimension=768,
            pooling_mode_cls_token=True,
            pooling_mode_mean_tokens=True
            )
        output_vectors = []
        features = {'attention_mask': torch.tensor([...])}
        token_embeddings = torch.randn(10, 768)
        pooling_instance.apply_pooling(output_vectors, features, token_embeddings)

    """

    def __init__(self: BasePooling, word_embedding_dimension: int, **pooling_modes: bool) -> None:
        """Initialize the BasePooling instance with specified embedding dimension and pooling modes.

        Args:
        ----
            word_embedding_dimension (int): The dimension of the embeddings used for pooling.
            **pooling_modes (bool): Arbitrary keyword arguments where keys are the mode names
                and values are booleans indicating whether to activate the corresponding mode.

        """
        self.word_embedding_dimension: int = word_embedding_dimension
        self.pooling_functions: list[Callable[[list[Tensor], dict[str, Any]], None]] = []

        # Append the correct functions based on configuration
        for mode, func in pooling_funcs.items():
            if pooling_modes.get(f"{mode}", False):
                self.pooling_functions.append(func)  # type: ignore  # noqa: PGH003

    def apply_pooling(
        self: BasePooling,
        output_vectors: list,
        features: dict[str, Any],
    ) -> list[Tensor]:
        """Apply the configured pooling functions to the given token embeddings.

        Args:
        ----
            output_vectors (list[torch.Tensor]): The list to which the results of pooling operations.
            features (dict[str, Any]): A dictionary containing relevant features such as the attention mask.

        Returns:
        -------
            List[Tensor]: The list containing all the pooled results.

        """  # noqa: E501
        for func in self.pooling_functions:
            func(output_vectors, features)
        return output_vectors
