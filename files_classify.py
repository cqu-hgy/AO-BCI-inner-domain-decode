# -*- coding: utf-8 -*-
# @author: hgy
# @created: 2025/12/27
# This class is used to classify eeg files to different paradigms.

import os
import scipy.io as scio


class FilesClassify:
    def __init__(self):
        super(FilesClassify, self).__init__()
    

    def charge_data_event(self, file_data, file_event):
        """
        check data file and event file match.
        """
        for data_pth, event_pth in zip(file_data, file_event):
            if data_pth[:-14] != event_pth[:-14]: # get file id_num
                return False
        return True

    def fileload(self, pth_subject, version):
        """
        load event and data files of visual feedback of three paradigms.
        """
        list_pth = os.listdir(pth_subject)
        list_pth.sort(key=lambda x: int(x[-18:-14]))  # sort by number
        # print(f'list_pth: {list_pth}')

        # create container
        event_mark = 'stimevent'
        event, data = [], []
        for pth in list_pth:
            if event_mark in pth:
                event.append(pth)
            else:
                data.append(pth)

        event_para1, data_para1 = [], []
        event_para2, data_para2 = [], []
        event_para3, data_para3 = [], []
        if version==0: # old version
            for i, (ei, di) in enumerate(zip(event, data)):
                e = os.path.join(pth_subject, ei)
                d =  os.path.join(pth_subject, di)
                if i < 4:
                    event_para1.append(e)
                    data_para1.append(d)
                elif i < 8:
                    event_para2.append(e)
                    data_para2.append(d)
                elif i < 12:
                    event_para3.append(e)
                    data_para3.append(d)

        elif version==1: # new version
            for i, (ei, di) in enumerate(zip(event, data)):
                e, d = os.path.join(pth_subject, ei), os.path.join(pth_subject, di)  # add path
                event_info = scio.loadmat(e)['stimevent'][0][0]

                L_R = event_info['L_or_R']
                stim = event_info['stimMode']
                feedback = event_info['IsFeedback']
                if feedback == 0:
                    if stim == 7:
                        event_para2.append(e)
                        data_para2.append(d)
                    elif stim == 6:
                        if L_R == 2:
                            event_para1.append(e)
                            data_para1.append(d)
                        elif L_R == 1:
                            event_para3.append(e)
                            data_para3.append(d)
        # files inspection between data and event
        result = []
        result.append(self.charge_data_event(data_para1, event_para1))
        result.append(self.charge_data_event(data_para2, event_para2))
        result.append(self.charge_data_event(data_para3, event_para3))
        if False in result:
            print("data and event file not match, file load error!")
            quit()

        return event_para1, data_para1, event_para2, data_para2, event_para3, data_para3

    def fileload_feedback(self, pth_subject, version):
        """
        load event and data files of motor feedback of three paradigms.
        """
        list_pth = os.listdir(pth_subject)
        list_pth.sort(key=lambda x: int(x[-18:-14]))
        fb_list_pth = list_pth[24:] # remove visual feedback files

        event, data = [], []
        event_mark = 'stimevent'
        for pth in fb_list_pth:
            if event_mark in pth:
                event.append(pth)
            else:
                data.append(pth)

        # create container
        event_s = 'stimevent'
        event_fb_para1, data_fb_para1 = [], []
        event_fb_para3, data_fb_para3 = [], []
        if version==0:
            len_file = len(fb_list_pth)/2
            mark_len = len_file if len_file % 2 == 0 else len_file + 1

            for i, (ei, di) in enumerate(zip(event, data)):
                e = os.path.join(pth_subject, ei)
                d = os.path.join(pth_subject, di)
                if i < mark_len/2:
                    event_fb_para1.append(e)
                    data_fb_para1.append(d)
                else:
                    event_fb_para3.append(e)
                    data_fb_para3.append(d)
        elif version==1:
            for i, (ei, di) in enumerate(zip(event, data)):
                e, d = os.path.join(pth_subject, ei), os.path.join(pth_subject, di)  # add path
                event_info = scio.loadmat(e)['stimevent'][0][0]
                L_R = event_info['L_or_R']
                stim = event_info['stimMode']
                feedback = event_info['IsFeedback']
                if feedback == 1:
                    if stim == 6 and L_R == 2:
                        event_fb_para1.append(e)
                        data_fb_para1.append(d)
                    elif stim == 6 and L_R == 1:
                        event_fb_para3.append(e)
                        data_fb_para3.append(d)

        # print(f'event_fb_para1: {event_fb_para1}')
        # print(f'data_fb_para1: {data_fb_para1}')
        # print(f'event_fb_para3: {event_fb_para3}')
        # print(f'data_fb_para3: {data_fb_para3}')
        # files inspection between data and event
        result = []
        result.append(self.charge_data_event(data_fb_para1, event_fb_para1))
        result.append(self.charge_data_event(data_fb_para3, event_fb_para3))
        if False in result:
            print("data and event file not match, file load error!")
            quit()
        return event_fb_para1, data_fb_para1, event_fb_para3, data_fb_para3

if __name__ == "__main__":
    import ao_dataset
    import sys
    files, caps, subs, versions = ao_dataset.AODataSet().get_dataset(day=0)
    for f, c, s, v in zip(files, caps, subs, versions):
        print(f'Processing subject: {s}, cap: {c}, version: {v}')
        pth_subject = f
        fc = FilesClassify()
        event_para1, data_para1, event_para2, data_para2, event_para3, data_para3 = fc.fileload(pth_subject, v)
        print(f'Visual Feedback - Paradigm 1: {len(event_para1)} trials')
        print(f'Visual Feedback - Paradigm 2: {len(event_para2)} trials')
        print(f'Visual Feedback - Paradigm 3: {len(event_para3)} trials')

        event_fb_para1, data_fb_para1, event_fb_para3, data_fb_para3 = fc.fileload_feedback(pth_subject, v)
        print(f'Motor Feedback - Paradigm 1: {len(event_fb_para1)} trials')
        print(f'Motor Feedback - Paradigm 3: {len(event_fb_para3)} trials')
        # sys.exit(0)
