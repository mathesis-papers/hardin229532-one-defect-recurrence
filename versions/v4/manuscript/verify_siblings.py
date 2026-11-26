import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path


CASES = [
    ('column-2', 'row', 2, [6, -9], 4, [1, 4, 20, 84, 324, 1188]),
    ('column-3', 'row', 3, [10, -29, 20, -4], 6, [2, 8, 58, 356, 2038, 11184]),
    ('column-4', 'row', 4, [14, -57, 56, -16], 6, [6, 36, 361, 3064, 24344, 185808]),
    ('column-5', 'row', 5,
     [28, -286, 1290, -2373, 304, 3551, -2846, -546, 1308, -505, 76, -4],
     14, [16, 112, 1588, 19276, 221096, 2451728]),
    ('row-2', 'column', 2, [4, 0, -8, -4], 5, [0, 4, 8, 36, 112, 368]),
    ('row-3', 'column', 3, [6, -1, -28, -4, 16, -4], 9, [0, 20, 58, 361, 1588, 7460]),
    ('row-4', 'column', 4,
     [6, 23, -102, -288, 250, 787, -238, -741, 124, 196, -16, -16],
     15, [0, 84, 356, 3064, 19276, 130854]),
]

ROOTS = {
    'column-2': [1, -3],
    'column-3': [1, -5, 2],
    'column-4': [1, -7, 4],
    'column-5': [1, -14, 45, -15, -36, 19, -2],
    'row-2': [1, -2, -2],
    'row-3': [1, -3, -4, 2],
    'row-4': [1, -3, -16, 3, 25, -2, -4],
}


def convolution(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for first, first_value in enumerate(left):
        for second, second_value in enumerate(right):
            result[first + second] += first_value * second_value
    return result


def canonical(row):
    labels = {}
    return tuple(labels.setdefault(color, len(labels)) for color in row)


def representative(row):
    return min(canonical(row), canonical(row[::-1]))


def internal(row, orientation):
    return sum(left == right for left, right in zip(row, row[1:])) if orientation == 'row' else 0


def between(previous, following, orientation):
    diagonals = sum(previous[index] == following[index + 1] for index in range(len(previous) - 1))
    diagonals += sum(previous[index + 1] == following[index] for index in range(len(previous) - 1))
    return diagonals + (sum(left == right for left, right in zip(previous, following))
                        if orientation == 'column' else 0)


def multiply(vector, matrix):
    return [sum(value * matrix[source][target] for source, value in enumerate(vector))
            for target in range(len(matrix))]


def construct(orientation, size):
    rows = list(product(range(3), repeat=size))
    states = sorted({(representative(row), budget) for row in rows for budget in (0, 1)
                     if internal(row, orientation) <= 1 - budget}, key=lambda state: (state[1], state[0]))
    indices = {state: index for index, state in enumerate(states)}

    def transitions(previous, budget):
        counts = Counter()
        for following in rows:
            cost = between(previous, following, orientation) + internal(following, orientation)
            if cost <= budget:
                counts[indices[representative(following), budget - cost]] += 1
        return [counts[index] for index in range(len(states))]

    matrix = [transitions(row, budget) for row, budget in states]
    pairs = 0
    for row in rows:
        for budget in (0, 1):
            if internal(row, orientation) <= 1 - budget:
                assert transitions(row, budget) == matrix[indices[representative(row), budget]]
                pairs += 1
    initial = [0] * len(states)
    for row in rows:
        cost = internal(row, orientation)
        if cost <= 1:
            initial[indices[representative(row), 1 - cost]] += 1
    terminal = [int(budget == 0) for row, budget in states]
    return states, matrix, initial, terminal, pairs


def check(case):
    name, orientation, size, coefficients, threshold, expected = case
    states, matrix, initial, terminal, pairs = construct(orientation, size)
    order = len(coefficients)
    vectors = [initial]
    for index in range(max(80, order + len(states) + 2)):
        vectors.append(multiply(vectors[-1], matrix))
    labelled = [sum(value * terminal[index] for index, value in enumerate(vector)) for vector in vectors]
    counts = []
    for index, value in enumerate(labelled):
        if orientation == 'row' and size == 2 and index == 0:
            assert value == 3
            counts.append(1)
        else:
            assert value % 6 == 0
            counts.append(value // 6)
    assert counts[:len(expected)] == expected
    shifts = []
    for shift in range(len(states) + 1):
        residual = [vectors[shift + order][coordinate] - sum(
            coefficient * vectors[shift + order - lag - 1][coordinate]
            for lag, coefficient in enumerate(coefficients)) for coordinate in range(len(states))]
        if not any(residual):
            shifts.append(shift)
            break
    assert shifts, name
    vector_shift = shifts[0]
    assert threshold > order
    residuals = [counts[height - 1] - sum(coefficient * counts[height - lag - 2]
                 for lag, coefficient in enumerate(coefficients))
                 for height in range(threshold, len(counts) + 1)]
    assert not any(residuals), name
    denominator = [1] + [-coefficient for coefficient in coefficients]
    root = ROOTS[name]
    assert denominator == convolution(root, root)
    numerator = [sum(denominator[index] * counts[degree - index]
                     for index in range(min(degree, order) + 1)) for degree in range(threshold - 1)]
    while numerator and numerator[-1] == 0:
        numerator.pop()
    expected_numerators = {
        'column-3': [2, -12, 36, -32, 8],
        'column-4': [6, -48, 199, -274, 105],
        'row-2': [0, 4, -8, 4],
        'row-3': [0, 20, -62, 33, 40, -3, -16, 4],
    }
    if name in expected_numerators:
        assert numerator == expected_numerators[name]
    if name == 'column-5':
        mathar = [56, -774, 3422, -4472, -4384, 9787, -1410, -3840, 2168, -425, 28]
        assert numerator == [16 * (denominator[index] if index < len(denominator) else 0)
                             + (2 * mathar[index - 1] if 1 <= index <= len(mathar) else 0)
                             for index in range(len(numerator))]
    proper_indices = [index for index, (row, budget) in enumerate(states) if budget == 1]
    proper_matrix = [[matrix[source][target] for target in proper_indices] for source in proper_indices]
    proper_initial = [initial[index] for index in proper_indices]
    proper_vectors = [proper_initial]
    for index in range(len(vectors) - 1):
        proper_vectors.append(multiply(proper_vectors[-1], proper_matrix))
    proper_counts = [sum(vector) for vector in proper_vectors]
    at_most_counts = [one + zero for one, zero in zip(labelled, proper_counts)]
    proper_shifts = []
    for shift in range(len(states) + 1):
        residual = [proper_vectors[shift + order][coordinate] - sum(
            coefficient * proper_vectors[shift + order - lag - 1][coordinate]
            for lag, coefficient in enumerate(coefficients)) for coordinate in range(len(proper_matrix))]
        if not any(residual):
            proper_shifts.append(shift)
            break
    assert proper_shifts
    assert not any(at_most_counts[height - 1] - sum(coefficient * at_most_counts[height - lag - 2]
                   for lag, coefficient in enumerate(coefficients))
                   for height in range(threshold, len(at_most_counts) + 1))
    previous_residual = counts[threshold - 2] - sum(
        coefficient * counts[threshold - lag - 3]
        for lag, coefficient in enumerate(coefficients) if threshold - lag - 3 >= 0)
    return {
        'name': name, 'orientation': orientation, 'slice_size': size,
        'states': [[list(row), budget] for row, budget in states], 'matrix': matrix,
        'initial': initial, 'terminal': terminal, 'valid_labelled_slice_budget_pairs': pairs,
        'coefficients_lag_order': coefficients, 'valid_from': threshold,
        'vector_identity_shift': vector_shift,
        'finite_scalar_bridge_heights': list(range(threshold, order + vector_shift + 1)),
        'vector_residual': [0] * len(states),
        'initial_counts': counts[:max(threshold, len(expected))],
        'scalar_range': [threshold, len(counts)], 'scalar_residuals': residuals,
        'gf_variable': 'z', 'gf_convention': 'sum(a(n)*z**(n-1), n>=1)',
        'numerator_ascending': numerator, 'denominator_ascending': denominator,
        'denominator_square_root_ascending': root,
        'proper_states': [list(states[index][0]) for index in proper_indices],
        'proper_matrix': proper_matrix, 'proper_initial': proper_initial,
        'proper_order_r_vector_shift': proper_shifts[0],
        'at_most_one_initial_labelled_counts': at_most_counts[:max(threshold, len(expected))],
        'at_most_one_valid_from': threshold,
        'preceding_height_residual': previous_residual,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('sibling-certificate.json'))
    args = parser.parse_args()
    certificates = [check(case) for case in CASES]
    args.output.write_text(json.dumps(certificates, indent=2) + '\n')
    for result in certificates:
        print(result['name'], 'states', len(result['states']), 'valid from', result['valid_from'],
              'vector shift', result['vector_identity_shift'], 'numerator', result['numerator_ascending'])


if __name__ == '__main__':
    main()
