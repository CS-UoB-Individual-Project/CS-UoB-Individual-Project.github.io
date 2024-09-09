import os
import sys
import numpy as np
from itertools import chain
from pprint import pprint


def flatten(list_):
    return list(chain.from_iterable(list_))


def load_file(in_file_path):
    lines = []
    with open(in_file_path, 'r') as in_f:
        for line in in_f:
            lines.append(line.replace('\t', '').rstrip())
    return lines


def cut_file(in_file):
    cut_lines = []
    start_found = False
    end_found = False
    for line in in_file:
        if not start_found:
            if 'START' in line:
                start_found = True
        elif not end_found:
            if 'END' in line:
                end_found = True
            elif line != '':
                cut_lines.append(line)
    return cut_lines


def load_and_cut_file(in_file_path):
    in_file = load_file(in_file_path)
    return cut_file(in_file)


def save_markdown(lines, out_file_path):
    with open(out_file_path, 'w') as out_f:
        out_f.write('---\n')
        out_f.write('geometry: margin=0.5cm, landscape\n')
        out_f.write('---\n')

        for line in lines:
            out_f.write(line + '\n')


def create_bar(max_col_sizes, is_mid_bar=False):
    num_columns = len(max_col_sizes)
    delim = '-' if not is_mid_bar else '='
    return '+'.join(['', *[delim * int(max_col_sizes[i]) for i in range(num_columns)], ''])


def get_column_max_sizes(sizes):
    return np.max(sizes, 0).astype(int)


def get_row_max_sizes(split_table_mat):
    max_row_sizes = []
    for i in range(len(split_table_mat)):
        curr_max_size = 0
        for j in range(len(split_table_mat[i])):
            len_row = len(split_table_mat[i][j])
            if len_row > curr_max_size:
                curr_max_size = len_row
        max_row_sizes.append(int(curr_max_size))
    return max_row_sizes


def split_table_across_multiple_rows(table_mat):
    split_table_mat = []
    for i, line in enumerate(table_mat):
        split_table_mat.append([])
        for j, cell in enumerate(line):
            split_table_mat[i].append(cell.lstrip().rstrip().split('<br>'))
    return split_table_mat


def pad_line(row, max_col_sizes):
    new_line = '|'
    for i, cell in enumerate(row):
        pad_to_add = max_col_sizes[i] - len(cell)
        new_line += cell + ''.join([' ' for j in range(pad_to_add)]) + '|'
    return new_line

def pad_rows(row, row_size):
    new_rows = []
    for i, cell in enumerate(row):
        pad_to_add = row_size - len(cell)
        new_cell = cell + ['' for j in range(pad_to_add)]
        new_rows.append(new_cell)
    return list(zip(*new_rows))


def create_grid_table_lines(split_table_mat, max_col_sizes, max_row_sizes):
    top_bar = create_bar(max_col_sizes)
    mid_bar = create_bar(max_col_sizes, is_mid_bar=True)

    grid_table_lines = [top_bar]

    for i, row in enumerate(split_table_mat):
        if max_row_sizes[i] == 1:
            new_row = pad_line(flatten(row), max_col_sizes)
            grid_table_lines.append(new_row)
        else:
            new_rows = pad_rows(row, max_row_sizes[i])
            for n_row in new_rows:
                new_row = pad_line(n_row, max_col_sizes)
                grid_table_lines.append(new_row)
        if i == max_row_sizes[0] - 1:
            grid_table_lines.append(mid_bar)
        else:
            grid_table_lines.append(top_bar)
            grid_table_lines.append(pad_line([' ' for i in range(len(max_col_sizes))], max_col_sizes))
            grid_table_lines.append(top_bar)
            grid_table_lines.append(pad_line([' ' for i in range(len(max_col_sizes))], max_col_sizes))
            grid_table_lines.append(top_bar)
    return grid_table_lines


def create_grid_table(table_lines):
    num_columns = table_lines[0].count('|') - 1

    table_mat = []
    for i, line in enumerate(table_lines):
        if i == 1:
            continue
        words = line.split('|')[1:-1]
        table_mat.append(words)
 
    split_table_mat = split_table_across_multiple_rows(table_mat)

    num_rows = len(split_table_mat)

    sizes = np.zeros((num_rows, num_columns))
    for i in range(num_rows):
        for j in range(num_columns):
            max_len = 0
            len(split_table_mat[i][j])

            for k in range(len(split_table_mat[i][j])):
                line_len = len(split_table_mat[i][j][k])
                if line_len > max_len:
                    max_len = line_len
            sizes[i, j] = max_len

    max_col_sizes = get_column_max_sizes(sizes)
    max_row_sizes = get_row_max_sizes(split_table_mat)

    grid_table_lines = create_grid_table_lines(split_table_mat, max_col_sizes, max_row_sizes)

    return grid_table_lines
    

def main(args):
    table_lines = load_and_cut_file(args.IN_FILE)
    grid_table_lines = create_grid_table(table_lines)
    pprint(grid_table_lines)
    if args.out_file:
        save_markdown(grid_table_lines, args.out_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Program to convert from markdown table to grid table')

    parser.add_argument('IN_FILE', type=str, help='input file to convert')
    parser.add_argument('--out-file', '-o', type=str, help='output file path')

    main(parser.parse_args())
