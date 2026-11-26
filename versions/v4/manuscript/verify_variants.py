import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import verify
from verify_siblings import convolution


def check():
    for left, right in product(range(3), repeat=2):
        assert (left + right == 2) == (2 - left == right)
    path_exact = [0] + [3 * (width - 1) * 2 ** (width - 2) for width in range(2, 13)]
    path_at_most = [3] + [3 * (width + 1) * 2 ** (width - 2) for width in range(2, 13)]
    for sequence in (path_exact, path_at_most):
        assert all(sequence[index] == 4 * sequence[index - 1] - 4 * sequence[index - 2]
                   for index in range(2, len(sequence)))
    rows = list(product(range(3), repeat=6))
    proper_rows = [row for row in rows if verify.horizontal(row) == 0]
    states = sorted({verify.representative(row) for row in proper_rows})
    matrix = []
    for previous in states:
        counts = Counter(verify.representative(row) for row in proper_rows if verify.crossing(previous, row) == 0)
        matrix.append([counts[row] for row in states])
    initial = [sum(verify.representative(row) == state for row in proper_rows) for state in states]
    vectors = [initial]
    for index in range(211):
        vectors.append(verify.multiply(vectors[-1], matrix))
    root = [1, -18, 56, 81, -280, -12, 259, -78, -24, 5]
    residual = [sum(root[lag] * vectors[9 - lag][coordinate] for lag in range(10))
                for coordinate in range(len(states))]
    assert not any(residual)
    assert all(sum(vector) % 6 == 0 for vector in vectors)
    proper = [sum(vector) // 6 for vector in vectors]
    numerator = [sum(root[lag] * proper[degree - lag] for lag in range(min(degree, 9) + 1))
                 for degree in range(9)]
    assert numerator == [16, -108, -12, 520, -182, -430, 180, 40, -10]
    main = verify.verify()
    one_initial = main['checks']['initial_values']
    exact = [6 * value for value in one_initial]
    at_most = [6 * (one + zero) for one, zero in zip(one_initial, proper)]
    assert exact[:6] == [240, 2208, 44760, 785124, 13031664, 208867428]
    assert at_most[:6] == [336, 3288, 58752, 971844, 15547380, 242861616]
    for sequence in (exact, at_most):
        boundary = sequence[18] - sum(coefficient * sequence[index]
                                     for index, coefficient in enumerate(verify.COEFFICIENTS))
        assert boundary == 5184
    main_numerator = main['generating_function']['numerator_ascending']
    correction = convolution(numerator, root)
    at_most_numerator = [6 * (value + (correction[index] if index < len(correction) else 0))
                         for index, value in enumerate(main_numerator)]
    return {
        'proper_states': [list(row) for row in states], 'proper_matrix': matrix,
        'proper_initial': initial, 'proper_recurrence_root_ascending': root,
        'proper_vector_shift': 0, 'proper_vector_residual': residual,
        'proper_numerator_ascending': numerator, 'proper_initial_counts': proper[:20],
        'A269033_initial': exact, 'A269050_initial': at_most,
        'A269033_numerator_ascending': [6 * value for value in main_numerator],
        'A269050_numerator_ascending': at_most_numerator,
        'shared_denominator_ascending': convolution(root, root),
        'height_19_residual_both': 5184, 'minimal_eventual_order_both': 18,
        'sum_two_path_exact_widths_1_to_12': path_exact,
        'sum_two_path_at_most_widths_1_to_12': path_at_most,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('variant-certificate.json'))
    args = parser.parse_args()
    certificate = check()
    args.output.write_text(json.dumps(certificate, indent=2) + '\n')
    print('The sum-two involution, ten-state proper sector and both width-six recurrences have exact certificates.')


if __name__ == '__main__':
    main()
