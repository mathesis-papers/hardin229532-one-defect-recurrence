import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path


COEFFICIENTS = [-25, 240, 204, -6334, 6468, 42628, -83203, -34136,
                160400, -40816, -108224, 56184, 23849, -19128, 340,
                1854, -436, 36]


def canonical(row):
    labels = {}
    return tuple(labels.setdefault(color, len(labels)) for color in row)


def representative(row):
    return min(canonical(row), canonical(row[::-1]))


def horizontal(row):
    return sum(left == right for left, right in zip(row, row[1:]))


def crossing(previous, following):
    return sum(previous[column] == following[column + 1] for column in range(5)) + sum(
        previous[column + 1] == following[column] for column in range(5))


def multiply(vector, matrix):
    return [sum(value * matrix[source][target] for source, value in enumerate(vector))
            for target in range(len(matrix))]


def scalar(vector, terminal):
    return sum(value * terminal[index] for index, value in enumerate(vector))


def polynomial_remainder(dividend, divisor, prime):
    remainder = [value % prime for value in dividend]
    while len(remainder) >= len(divisor) and any(remainder):
        factor = remainder[-1] * pow(divisor[-1], -1, prime) % prime
        shift = len(remainder) - len(divisor)
        for index, value in enumerate(divisor):
            remainder[shift + index] = (remainder[shift + index] - factor * value) % prime
        while len(remainder) > 1 and remainder[-1] == 0:
            remainder.pop()
    return remainder


def generating_function(sequence):
    denominator = [1] + [-value for value in COEFFICIENTS[::-1]]
    numerator = [sum(denominator[index] * sequence[degree - index]
                     for index in range(min(degree, 18) + 1))
                 for degree in range(19)]
    square_root = [1, -18, 56, 81, -280, -12, 259, -78, -24, 5]
    assert denominator == [sum(square_root[left] * square_root[degree - left]
                               for left in range(10) if 0 <= degree - left < 10)
                           for degree in range(19)]
    left = [value % 101 for value in denominator]
    right = [value % 101 for value in numerator]
    degrees = [len(left) - 1, len(right) - 1]
    while any(right):
        left, right = right, polynomial_remainder(left, right, 101)
        if any(right):
            degrees.append(len(right) - 1)
    assert len(left) == 1 and left[0] != 0
    assert denominator[-1] % 101 != 0 and numerator[-1] % 101 != 0
    assert numerator[-1] == 864
    return {
        'numerator_ascending': numerator,
        'denominator_ascending': denominator,
        'denominator_square_root_ascending': square_root,
        'coprimality_prime': 101,
        'euclidean_remainder_degrees': degrees,
        'gcd_mod_101': [1],
        'height_19_recurrence_residual': numerator[-1],
        'minimal_eventual_order': 18,
    }


def direct_count(height, width=6):
    cells = [-1] * (height * width)

    def visit(position, maximum_color, defects):
        if position == len(cells):
            return int(defects == 1)
        row, column = divmod(position, width)
        total = 0
        for color in range(min(2, maximum_color + 1) + 1):
            additional = int(column > 0 and cells[position - 1] == color)
            if row > 0:
                if column > 0:
                    additional += int(cells[position - width - 1] == color)
                if column + 1 < width:
                    additional += int(cells[position - width + 1] == color)
            if defects + additional <= 1:
                cells[position] = color
                total += visit(position + 1, max(maximum_color, color), defects + additional)
        return total

    return visit(0, -1, 0)


def construct():
    rows = list(product(range(3), repeat=6))
    horizontal_cost = {row: horizontal(row) for row in rows}
    valid_rows = [row for row in rows if horizontal_cost[row] <= 1]
    states = sorted({(representative(row), remaining)
                     for row in valid_rows
                     for remaining in range(2 - horizontal_cost[row])},
                    key=lambda state: (state[1], state[0]))
    indices = {state: index for index, state in enumerate(states)}
    row_classes = {row: representative(row) for row in valid_rows}

    def transitions(previous, remaining):
        counts = [0] * len(states)
        for following in valid_rows:
            cost = crossing(previous, following) + horizontal_cost[following]
            if cost <= remaining:
                counts[indices[(row_classes[following], remaining - cost)]] += 1
        return counts

    matrix = [transitions(row, remaining) for row, remaining in states]
    lumpability_checks = 0
    for row in valid_rows:
        for remaining in range(2 - horizontal_cost[row]):
            assert transitions(row, remaining) == matrix[indices[(row_classes[row], remaining)]]
            lumpability_checks += 1
    initial = [0] * len(states)
    for row in valid_rows:
        initial[indices[(row_classes[row], 1 - horizontal_cost[row])]] += 1
    terminal = [int(remaining == 0) for row, remaining in states]
    return states, matrix, initial, terminal, lumpability_checks


def verify(table_path=None):
    states, matrix, initial, terminal, checks = construct()
    vectors = [initial]
    for height in range(1, 212):
        vectors.append(multiply(vectors[-1], matrix))
    annihilators = {}
    for shift in range(4):
        residual = [vectors[shift + 18][column] - sum(
            coefficient * vectors[shift + index][column]
            for index, coefficient in enumerate(COEFFICIENTS))
                    for column in range(len(states))]
        annihilators[str(shift)] = residual
    assert all(value == 0 for value in annihilators['2'])
    base_residual = scalar(vectors[19], terminal) - sum(
        coefficient * scalar(vectors[1 + index], terminal)
        for index, coefficient in enumerate(COEFFICIENTS))
    assert base_residual == 0
    sequence = [scalar(vector, terminal) // 6 for vector in vectors]
    assert all(scalar(vector, terminal) % 6 == 0 for vector in vectors)
    assert sequence[:4] == [40, 368, 7460, 130854]
    direct_values = [direct_count(height) for height in range(1, 5)]
    assert direct_values == sequence[:4]
    single_rows = [direct_count(1, width) for width in range(1, 13)]
    assert single_rows == [0, 1] + [(width - 1) * 2 ** (width - 3) for width in range(3, 13)]
    for height in range(20, 213):
        assert sequence[height - 1] == sum(
            coefficient * sequence[height - 19 + index]
            for index, coefficient in enumerate(COEFFICIENTS))
    rational_function = generating_function(sequence)
    for degree in range(19, len(sequence)):
        assert sum(rational_function['denominator_ascending'][index] * sequence[degree - index]
                   for index in range(19)) == 0
    compared = []
    if table_path:
        for line in Path(table_path).read_text().splitlines():
            if not line or line.startswith('#'):
                continue
            height, value = map(int, line.split())
            if height <= len(sequence):
                assert sequence[height - 1] == value, (height, sequence[height - 1], value)
                compared.append(height)
    state_data = [{'row': list(row), 'remaining': remaining} for row, remaining in states]
    return {
        'schema_version': 1,
        'width': 6,
        'colors': 3,
        'defects': 1,
        'states': state_data,
        'matrix': matrix,
        'initial': initial,
        'terminal': terminal,
        'coefficients_ascending': COEFFICIENTS,
        'generating_function': rational_function,
        'certificate': {
            'vector_shift': 2,
            'vector_residual': annihilators['2'],
            'scalar_base_height': 20,
            'scalar_base_residual': base_residual,
        },
        'checks': {
            'literal_rows_enumerated': 729,
            'valid_row_budget_pairs': checks,
            'states': len(states),
            'states_by_budget': dict(Counter(remaining for row, remaining in states)),
            'recurrence_heights': [20, 212],
            'table_heights': [min(compared), max(compared)] if compared else [],
            'table_entries': len(compared),
            'initial_values': sequence[:20],
            'direct_row_major_counts_heights_1_to_4': direct_values,
            'single_row_counts_widths_1_to_12': single_rows,
            'earlier_vector_identity_shifts': {
                shift: not any(residual) for shift, residual in annihilators.items()},
            'minimal_eventual_order': rational_function['minimal_eventual_order'],
            'coprimality_prime': rational_function['coprimality_prime'],
            'height_19_recurrence_residual': rational_function['height_19_recurrence_residual'],
        },
    }


def main():
    parser = argparse.ArgumentParser(description='Exact finite certificate for the width-six HDA recurrence.')
    parser.add_argument('--table', type=Path)
    parser.add_argument('--output', type=Path, default=Path('certificate.json'))
    arguments = parser.parse_args()
    result = verify(arguments.table)
    arguments.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['checks'], indent=2))
    print('All exact transfer and recurrence identities hold.')


if __name__ == '__main__':
    main()
