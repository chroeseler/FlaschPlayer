import numpy as np
import pytest

from layout import full_layout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_unique(matrix) -> bool:
    flat = matrix.flatten()
    return len(flat) == len(set(flat.tolist()))


def _expected_range(matrix, n_boxes: int) -> bool:
    flat = sorted(matrix.flatten().tolist())
    return flat == list(range(n_boxes * 20))


# ---------------------------------------------------------------------------
# Single-box (1×1) baseline
# ---------------------------------------------------------------------------

class TestSingleBox:
    def test_shape_no_rotate(self):
        m = full_layout(1, 1)
        assert m.shape == (4, 5)

    def test_shape_rotate_90(self):
        m = full_layout(1, 1, rotate_90=True)
        assert m.shape == (5, 4)

    def test_values_cover_0_to_19(self):
        m = full_layout(1, 1)
        assert _expected_range(m, 1)

    def test_values_unique(self):
        assert _all_unique(full_layout(1, 1))

    def test_rotate_values_cover_0_to_19(self):
        m = full_layout(1, 1, rotate_90=True)
        assert _expected_range(m, 1)

    def test_top_left_is_zero(self):
        # [0,1,2,3,4] is the first row — LED 0 is top-left
        assert full_layout(1, 1)[0][0] == 0

    def test_rotate_top_right_is_zero(self):
        # After rotate_90 the snake starts at top-right
        assert full_layout(1, 1, rotate_90=True)[0][3] == 0


# ---------------------------------------------------------------------------
# Multi-box tiling
# ---------------------------------------------------------------------------

class TestTiling:
    def test_2x1_shape(self):
        assert full_layout(2, 1).shape == (4, 10)

    def test_1x2_shape(self):
        assert full_layout(1, 2).shape == (8, 5)

    def test_2x2_shape(self):
        assert full_layout(2, 2).shape == (8, 10)

    def test_2x1_values(self):
        m = full_layout(2, 1)
        assert _expected_range(m, 2)
        assert _all_unique(m)

    def test_3x2_values(self):
        m = full_layout(3, 2)
        assert _expected_range(m, 6)
        assert _all_unique(m)

    def test_second_box_offset_by_20(self):
        # In a 2×1 layout the second box starts at LED 20
        m = full_layout(2, 1)
        second_box_leds = sorted(m[:, 5:].flatten().tolist())
        assert second_box_leds == list(range(20, 40))

    def test_rotate_2x1_shape(self):
        assert full_layout(2, 1, rotate_90=True).shape == (5, 8)

    def test_rotate_1x2_shape(self):
        assert full_layout(1, 2, rotate_90=True).shape == (10, 4)

    def test_rotate_2x2_values(self):
        m = full_layout(2, 2, rotate_90=True)
        assert _expected_range(m, 4)
        assert _all_unique(m)


# ---------------------------------------------------------------------------
# fliplr / flipud
# ---------------------------------------------------------------------------

class TestFlips:
    def test_fliplr_reverses_columns(self):
        normal = full_layout(1, 1)
        flipped = full_layout(1, 1, fliplr=True)
        np.testing.assert_array_equal(flipped, np.fliplr(normal))

    def test_flipud_reverses_rows(self):
        normal = full_layout(1, 1)
        flipped = full_layout(1, 1, flipud=True)
        np.testing.assert_array_equal(flipped, np.flipud(normal))

    def test_fliplr_twice_is_identity(self):
        m = full_layout(2, 2)
        np.testing.assert_array_equal(
            full_layout(2, 2, fliplr=True),
            np.fliplr(m),
        )

    def test_flipud_twice_is_identity(self):
        m = full_layout(2, 2)
        np.testing.assert_array_equal(
            full_layout(2, 2, flipud=True),
            np.flipud(m),
        )

    def test_fliplr_preserves_all_leds(self):
        assert _all_unique(full_layout(2, 2, fliplr=True))
        assert _expected_range(full_layout(2, 2, fliplr=True), 4)

    def test_flipud_preserves_all_leds(self):
        assert _all_unique(full_layout(2, 2, flipud=True))
        assert _expected_range(full_layout(2, 2, flipud=True), 4)


# ---------------------------------------------------------------------------
# rotate_90 correctness
# ---------------------------------------------------------------------------

class TestRotate90:
    def test_rotate_swaps_dimensions(self):
        normal = full_layout(3, 2)
        rotated = full_layout(3, 2, rotate_90=True)
        # Normal: (y_boxes*4, x_boxes*5); Rotated: (y_boxes*5, x_boxes*4)
        assert normal.shape == (8, 15)
        assert rotated.shape == (10, 12)

    def test_rotate_covers_all_leds(self):
        m = full_layout(3, 2, rotate_90=True)
        assert _expected_range(m, 6)
        assert _all_unique(m)
