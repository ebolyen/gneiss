# ----------------------------------------------------------------------------
# Copyright (c) 2016--, gneiss development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import numpy as np
import pandas as pd
import pandas.util.testing as pdt
from skbio import TreeNode
from gneiss.util import (match, match_tips, rename_internal_nodes,
                         _type_cast_to_float, random_tree,
                         block_diagonal, band_diagonal)
import numpy.testing as npt


class TestUtil(unittest.TestCase):

    def test_match(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['o1', 'o2', 'o3', 'o4'])
        metadata = pd.DataFrame([['a', 'control'],
                                 ['b', 'control'],
                                 ['c', 'diseased'],
                                 ['d', 'diseased']],
                                index=['s1', 's2', 's3', 's4'],
                                columns=['Barcode', 'Treatment'])
        exp_table, exp_metadata = table, metadata
        res_table, res_metadata = match(table, metadata)

        # make sure that the metadata and table indeces match
        pdt.assert_index_equal(res_table.index, res_metadata.index)

        res_table = res_table.sort_index()
        exp_table = exp_table.sort_index()

        res_metadata = res_metadata.sort_index()
        exp_metadata = exp_metadata.sort_index()

        pdt.assert_frame_equal(exp_table, res_table)
        pdt.assert_frame_equal(exp_metadata, res_metadata)

    def test_match_empty(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['o1', 'o2', 'o3', 'o4'])
        metadata = pd.DataFrame([['a', 'control'],
                                 ['b', 'control'],
                                 ['c', 'diseased'],
                                 ['d', 'diseased']],
                                index=['a1', 'a2', 'a3', 'a4'],
                                columns=['Barcode', 'Treatment'])

        with self.assertRaises(ValueError):
            match(table, metadata)

    def test_match_immutable(self):
        # tests to make sure that the original tables don't change.
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['o1', 'o2', 'o3', 'o4'])
        metadata = pd.DataFrame([['a', 'control'],
                                 ['c', 'diseased'],
                                 ['b', 'control']],
                                index=['s1', 's3', 's2'],
                                columns=['Barcode', 'Treatment'])

        exp_table = pd.DataFrame([[0, 0, 1, 1],
                                  [2, 2, 4, 4],
                                  [5, 5, 3, 3],
                                  [0, 0, 0, 1]],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['o1', 'o2', 'o3', 'o4'])
        exp_metadata = pd.DataFrame([['a', 'control'],
                                     ['c', 'diseased'],
                                     ['b', 'control']],
                                    index=['s1', 's3', 's2'],
                                    columns=['Barcode', 'Treatment'])
        match(table, metadata)
        pdt.assert_frame_equal(table, exp_table)
        pdt.assert_frame_equal(metadata, exp_metadata)

    def test_match_duplicate(self):
        table1 = pd.DataFrame([[0, 0, 1, 1],
                               [2, 2, 4, 4],
                               [5, 5, 3, 3],
                               [0, 0, 0, 1]],
                              index=['s2', 's2', 's3', 's4'],
                              columns=['o1', 'o2', 'o3', 'o4'])
        metadata1 = pd.DataFrame([['a', 'control'],
                                  ['b', 'control'],
                                  ['c', 'diseased'],
                                  ['d', 'diseased']],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['Barcode', 'Treatment'])

        table2 = pd.DataFrame([[0, 0, 1, 1],
                               [2, 2, 4, 4],
                               [5, 5, 3, 3],
                               [0, 0, 0, 1]],
                              index=['s1', 's2', 's3', 's4'],
                              columns=['o1', 'o2', 'o3', 'o4'])
        metadata2 = pd.DataFrame([['a', 'control'],
                                  ['b', 'control'],
                                  ['c', 'diseased'],
                                  ['d', 'diseased']],
                                 index=['s1', 's1', 's3', 's4'],
                                 columns=['Barcode', 'Treatment'])

        with self.assertRaises(ValueError):
            match(table1, metadata1)
        with self.assertRaises(ValueError):
            match(table2, metadata2)

    def test_match_scrambled(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['o1', 'o2', 'o3', 'o4'])
        metadata = pd.DataFrame([['a', 'control'],
                                 ['c', 'diseased'],
                                 ['b', 'control'],
                                 ['d', 'diseased']],
                                index=['s1', 's3', 's2', 's4'],
                                columns=['Barcode', 'Treatment'])
        exp_table = table
        exp_metadata = pd.DataFrame([['a', 'control'],
                                     ['b', 'control'],
                                     ['c', 'diseased'],
                                     ['d', 'diseased']],
                                    index=['s1', 's2', 's3', 's4'],
                                    columns=['Barcode', 'Treatment'])

        res_table, res_metadata = match(table, metadata)
        # make sure that the metadata and table indeces match
        pdt.assert_index_equal(res_table.index, res_metadata.index)

        res_table = res_table.sort_index()
        exp_table = exp_table.sort_index()

        res_metadata = res_metadata.sort_index()
        exp_metadata = exp_metadata.sort_index()

        pdt.assert_frame_equal(exp_table, res_table)
        pdt.assert_frame_equal(exp_metadata, res_metadata)

    def test_match_intersect(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['o1', 'o2', 'o3', 'o4'])
        metadata = pd.DataFrame([['a', 'control'],
                                 ['c', 'diseased'],
                                 ['b', 'control']],
                                index=['s1', 's3', 's2'],
                                columns=['Barcode', 'Treatment'])

        exp_table = pd.DataFrame([[0, 0, 1, 1],
                                  [2, 2, 4, 4],
                                  [5, 5, 3, 3]],
                                 index=['s1', 's2', 's3'],
                                 columns=['o1', 'o2', 'o3', 'o4'])

        exp_metadata = pd.DataFrame([['a', 'control'],
                                     ['b', 'control'],
                                     ['c', 'diseased']],
                                    index=['s1', 's2', 's3'],
                                    columns=['Barcode', 'Treatment'])

        res_table, res_metadata = match(table, metadata)
        # sort for comparison, since the match function
        # scrambles the names due to hashing.
        res_table = res_table.sort_index()
        res_metadata = res_metadata.sort_index()
        pdt.assert_frame_equal(exp_table, res_table)
        pdt.assert_frame_equal(exp_metadata, res_metadata)

    def test_match_tips(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['a', 'b', 'c', 'd'])
        tree = TreeNode.read([u"(((a,b)f, c),d)r;"])
        exp_table, exp_tree = table, tree
        res_table, res_tree = match_tips(table, tree)
        pdt.assert_frame_equal(exp_table, res_table)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_match_tips_scrambled_tips(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 3, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['a', 'b', 'c', 'd'])
        tree = TreeNode.read([u"(((b,a)f, c),d)r;"])
        exp_tree = tree
        exp_table = pd.DataFrame([[0, 0, 1, 1],
                                  [3, 2, 4, 4],
                                  [5, 5, 3, 3],
                                  [0, 0, 0, 1]],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['b', 'a', 'c', 'd'])

        res_table, res_tree = match_tips(table, tree)
        pdt.assert_frame_equal(exp_table, res_table)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_match_tips_scrambled_columns(self):
        table = pd.DataFrame([[0, 0, 1, 1],
                              [3, 2, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['b', 'a', 'c', 'd'])
        tree = TreeNode.read([u"(((a,b)f, c),d)r;"])
        exp_tree = tree
        exp_table = pd.DataFrame([[0, 0, 1, 1],
                                  [2, 3, 4, 4],
                                  [5, 5, 3, 3],
                                  [0, 0, 0, 1]],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['a', 'b', 'c', 'd'])

        res_table, res_tree = match_tips(table, tree)
        pdt.assert_frame_equal(exp_table, res_table)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_match_tips_intersect_tips(self):
        # there are less tree tips than table columns
        table = pd.DataFrame([[0, 0, 1, 1],
                              [2, 3, 4, 4],
                              [5, 5, 3, 3],
                              [0, 0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['a', 'b', 'c', 'd'])
        tree = TreeNode.read([u"((a,b)f,d)r;"])
        exp_table = pd.DataFrame([[0, 0, 1],
                                  [2, 3, 4],
                                  [5, 5, 3],
                                  [0, 0, 1]],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['a', 'b', 'd'])
        exp_tree = tree
        res_table, res_tree = match_tips(table, tree)
        pdt.assert_frame_equal(exp_table, res_table)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_match_tips_intersect_columns(self):
        # table has less columns than tree tips
        table = pd.DataFrame([[0, 0, 1],
                              [2, 3, 4],
                              [5, 5, 3],
                              [0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['a', 'b', 'd'])
        tree = TreeNode.read([u"(((a,b)f, c),d)r;"])
        exp_table = pd.DataFrame([[1, 0, 0],
                                  [4, 2, 3],
                                  [3, 5, 5],
                                  [1, 0, 0]],
                                 index=['s1', 's2', 's3', 's4'],
                                 columns=['d', 'a', 'b'])
        exp_tree = TreeNode.read([u"(d,(a,b)f)r;"])
        res_table, res_tree = match_tips(table, tree)
        pdt.assert_frame_equal(exp_table, res_table)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_match_tips_intersect_tree_immutable(self):
        # tests to see if tree chnages.
        table = pd.DataFrame([[0, 0, 1],
                              [2, 3, 4],
                              [5, 5, 3],
                              [0, 0, 1]],
                             index=['s1', 's2', 's3', 's4'],
                             columns=['a', 'b', 'd'])
        tree = TreeNode.read([u"(((a,b)f, c),d)r;"])
        match_tips(table, tree)
        self.assertEqual(str(tree), u"(((a,b)f,c),d)r;\n")

    def test_rename_internal_nodes(self):
        tree = TreeNode.read([u"(((a,b), c),d)r;"])
        exp_tree = TreeNode.read([u"(((a,b)y2, c)y1,d)y0;"])
        res_tree = rename_internal_nodes(tree)
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_rename_internal_nodes_names(self):
        tree = TreeNode.read([u"(((a,b), c),d)r;"])
        exp_tree = TreeNode.read([u"(((a,b)ab, c)abc,d)r;"])
        res_tree = rename_internal_nodes(tree, ['r', 'abc', 'ab'])
        self.assertEqual(str(exp_tree), str(res_tree))

    def test_rename_internal_nodes_names_mismatch(self):
        tree = TreeNode.read([u"(((a,b), c),d)r;"])
        with self.assertRaises(ValueError):
            rename_internal_nodes(tree, ['r', 'abc'])

    def test_rename_internal_nodes_immutable(self):
        tree = TreeNode.read([u"(((a,b)y2, c),d)r;"])
        rename_internal_nodes(tree)
        self.assertEqual(str(tree), "(((a,b)y2,c),d)r;\n")

    def test_rename_internal_nodes_mutable(self):
        tree = TreeNode.read([u"(((a,b)y2, c),d)r;"])
        rename_internal_nodes(tree, inplace=True)
        self.assertEqual(str(tree), "(((a,b)y2,c)y1,d)y0;\n")

    def test_type_cast_to_float(self):
        x = pd.DataFrame({'a': [1, 2, 3, 4, 5],
                          'b': ['1', '2', '3', '4', '5'],
                          'c': ['a', 'b', 'c', 'd', 'e'],
                          'd': [1., 2., 3., 4., 5.]})
        res = _type_cast_to_float(x)
        exp = pd.DataFrame({'a': [1., 2., 3., 4., 5.],
                            'b': [1., 2., 3., 4., 5.],
                            'c': ['a', 'b', 'c', 'd', 'e'],
                            'd': [1., 2., 3., 4., 5.]})
        pdt.assert_frame_equal(res, exp)

    def test_random_tree(self):
        np.random.seed(0)
        t = random_tree(10)
        exp = ('((7:0.0359448798595,8:0.0359448798595)y1:0.312827608797,'
               '((9:0.0272390892166,(4:0.00696620596189,6:0.00696620596189)'
               'y5:0.0202728832547)y3:0.16313179006,((0:0.00196516046521,'
               '3:0.00196516046521)y6:0.0815110118351,(1:0.0524584044569,'
               '(2:0.0215653684975,5:0.0215653684975)y8:0.0308930359593)'
               'y7:0.0310177678435)y4:0.106894706976)y2:0.15840160938)y0;\n')
        self.assertEqual(str(t), exp)

    def test_block_diagonal_4x4(self):
        np.random.seed(0)
        res = block_diagonal(4, 4, 2)
        exp = np.array([[0.5488135, 0.71518937, 0., 0.],
                        [0.60276338, 0.54488318, 0., 0.],
                        [0., 0., 0.4236548, 0.64589411],
                        [0., 0., 0.43758721, 0.891773]])
        npt.assert_allclose(res, exp, rtol=1e-5, atol=1e-5)

    def test_block_diagonal_3x4(self):
        np.random.seed(0)
        res = block_diagonal(3, 4, 2)
        exp = np.array([[0.548814, 0., 0.],
                        [0.715189, 0., 0.],
                        [0., 0.602763, 0.544883],
                        [0., 0.423655, 0.645894]])

        npt.assert_allclose(res, exp, rtol=1e-5, atol=1e-5)

    def test_block_diagonal_error(self):

        with self.assertRaises(ValueError):
            block_diagonal(3, 4, 1)

        with self.assertRaises(ValueError):
            block_diagonal(3, 4, 0)

    def test_band_diagonal(self):
        res = band_diagonal(8, 3)
        exp = np.array([[0.33333333, 0., 0., 0., 0., 0.],
                        [0.33333333, 0.33333333, 0., 0., 0., 0.],
                        [0.33333333, 0.33333333, 0.33333333, 0., 0., 0.],
                        [0., 0.33333333, 0.33333333, 0.33333333, 0., 0.],
                        [0., 0., 0.33333333, 0.33333333, 0.33333333, 0.],
                        [0., 0., 0., 0.33333333, 0.33333333, 0.33333333],
                        [0., 0., 0., 0., 0.33333333, 0.33333333],
                        [0., 0., 0., 0., 0., 0.33333333]])
        npt.assert_allclose(res, exp, rtol=1e-4, atol=1e-4)


if __name__ == '__main__':
    unittest.main()
