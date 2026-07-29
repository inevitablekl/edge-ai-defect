from __future__ import annotations

import sys
import unittest
from pathlib import Path

import cv2
import numpy as np


TOOLS = Path(__file__).resolve().parents[1] / "tools" / "validation"
sys.path.insert(0, str(TOOLS))

from generate_stage_k_level_b_reference import (  # noqa: E402
    INPUT_BYTES,
    INPUT_SHAPE,
    OUTPUT_BYTES,
    OUTPUT_ELEMENTS,
    OUTPUT_SHAPE,
    preprocess,
    tensor_contract,
)


class GenerateStageKReferenceTest(unittest.TestCase):
    def test_frozen_tensor_contract_constants(self) -> None:
        self.assertEqual(INPUT_SHAPE, [1, 3, 640, 640])
        self.assertEqual(OUTPUT_SHAPE, [1, 10, 8400])
        self.assertEqual(INPUT_BYTES, 1_228_800 * 4)
        self.assertEqual(OUTPUT_BYTES, OUTPUT_ELEMENTS * 4)
        self.assertEqual(
            tensor_contract("float32", "BCN", OUTPUT_SHAPE, OUTPUT_ELEMENTS, OUTPUT_BYTES)["byte_order"],
            "little_endian",
        )

    def test_preprocess_reuses_frozen_letterbox_contract(self) -> None:
        image = np.zeros((201, 319, 3), dtype=np.uint8)
        image[:, :, 0] = 11
        image[:, :, 1] = 22
        image[:, :, 2] = 33
        tensor, transform = preprocess(image)
        self.assertEqual(tensor.dtype, np.float32)
        self.assertEqual(list(tensor.shape), INPUT_SHAPE)
        self.assertTrue(tensor.flags.c_contiguous)
        self.assertTrue(np.isfinite(tensor).all())
        self.assertEqual(transform["original_width"], 319)
        self.assertEqual(transform["original_height"], 201)
        self.assertEqual(cv2.cvtColor(image, cv2.COLOR_BGR2RGB).shape, (201, 319, 3))
