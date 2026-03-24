# -*- coding: utf-8 -*-
# @author: hgy
# @created: 2025/12/27
# This class is used to load file paths and related information for EEG data.
import os
import sys

class AODataSet:
    def __init__(self):
        super(AODataSet, self).__init__()

        # self.root_raw = r'D:\work_space\AO_BCI_CQU_2025\RAW'
        self.root_raw = r'D:\work_space\AO_BCI_CQU_2025\AO_BCI_CQU_RAW_v2'
        self.raw = r'D:\work_space\data\raw'
        
        # self.root_raw = r"D:\work_space\AO_BCI_CQU_2025\cross_paras"

        self.root_cross = r'D:\work_space\data\cross'

    def raw_dataset(self):
        ## for item
        file_names = [f"ANT_S{i}_test" for i in range(1,21)]
        files = [os.path.join(self.raw, i) for i in file_names]
        caps = ['old', 'old', 'new', 'old', 'old', 'old', 'new',
                    'new', 'new', 'old', 'old', 'old', 'new', 'old',
                    'old', 'old', 'old', 'old', 'old', 'old']
        sub = [f"S{i}" for i in range(1,21)]        
        versions = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
                        0, 1, 1, 1, 1, 1, 1, 1]
        return files, caps, sub, versions

    def dataset1(self):     
        ## for raw
        file_names = [f"ANT_S{i}_test" for i in range(0,28)]
        files = [os.path.join(self.root_raw, i) for i in file_names]
        # caps = ['new', 'old', 'old', 'old', 'old', 'old', 'old', 'new', 'new', 'new',
        #         'old', 'old', 'old', 'old', 'old', 'old', 'old', 'old', 'old',
        #         'old', 'old', 'old', 'old', 'old', 'old', 'old', 'old', 'old']
        caps = ['old'] * len(file_names)
        sub = [f"S{i}" for i in range(0,28)]
        versions = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1]
        return files, caps, sub, versions

    def dataset2(self, day=None):
        
        ids = list(range(10, 28))
        file_names = [f"ANT_S{i}_day{day}_test" for i in ids]
        files = [os.path.join(self.root_cross, i) for i in file_names]
        caps = ['old'] * len(file_names)
        subs = [f"S{i}" for i in ids]
        versions = [1] * len(file_names)
        return files, caps, subs, versions

    def get_dataset(self, day):
        if day == -1:
            return self.raw_dataset()
        elif day == 0:
            return self.dataset1()
        elif day ==1 or day==2:
            return self.dataset2(day)
        else:
            print("day should be 0, 1 or 2")
            sys.exit(1)

if __name__ == "__main__":
    files, caps, subs, versions = AODataSet().get_dataset(day=2)
    print(files)
    print(caps)
    print(subs)
    print(versions)
