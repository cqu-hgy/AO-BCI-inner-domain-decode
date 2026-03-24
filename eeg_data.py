# -*- coding: utf-8 -*-
# @author: hgy
# @created: 2025/12/27
# This class is used to load eeg data and label from files.
import os
import sys
import scipy.io as scio
import numpy as np
from scipy.signal import butter, filtfilt


class EEGTools:

    def __init__(self):
        super(EEGTools, self).__init__()

    # get electrodes index of EEG channels
    def electrode_index(self, electrodes):
        """
        get electrode index from electrodes list
        """
        all_electrodes = ['Fp1', 'Fpz', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8',
                    'FC5', 'FC1', 'FC2', 'FC6', 'PO3', 'T7', 'C3', 'Cz',
                    'C4', 'T8', 'PO4', 'CP5', 'CP1', 'CP2', 'CP6', 'PO7',
                    'P3', 'Pz', 'P4', 'PO8', 'POz', 'O1', 'Oz', 'O2']
        index = [i for i in range(len(all_electrodes)) if all_electrodes[i] in electrodes]
        
        return index

    def loss(self, t_label, p_label):
        """
        calculate accuracy by comparing true labels and predicted labels.
        """
        
        if len(t_label) != len(p_label):
            print("t_label and p_label must have the same length")
            sys.exit(1)
        acc = sum(np.array(t_label) == np.array(p_label))
        return acc / len(t_label)

    def data_mean(self, data1, data2):
        """
        calculate mean of two data arrays, keep its shape.
        """
        data = data1 + data2
        return np.array([i / 2 for i in data])

        # prepare 
    def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=6):
        """
        butter bandpass filter.
        lowcut: lowpass filter cutoff frequency
        highcut: highpass filter cutoff frequency
        fs: sample rate
        """
        if lowcut <= 0 or highcut <= 0:
            raise ValueError("lowcut and highcut must be positive")
        if lowcut >= highcut:
            raise ValueError("lowcut must be less than highcut")
        if fs <= 0:
            raise ValueError("Sampling frequency fs must be positive")
        if not isinstance(data, (list, np.ndarray)):
            raise ValueError("data must be a list or numpy array")
        if np.array(data).size == 0:
            raise ValueError("data must not be empty")

        fa = 0.5 * fs
        low = lowcut / fa
        high = highcut / fa
        b, a = butter(order, [low, high], btype='band') # type: ignore
        y = filtfilt(b, a, data)
        return y

    # function of generate reference sin signal
    def generate_mscca_references(self, freqs, srate, T, phases, n_harmonics: int = 1):
        """
        generate reference signals.
        freqs: frequency
        srate: sample rate
        T: signal length
        phases: phase
        n_harmonics: number of sine waves
        """
        freqs = freqs.flatten()
        if isinstance(freqs, int) or isinstance(freqs, float):
            freqs = [freqs]
        freqs = np.array(freqs)[:, np.newaxis]
        if phases is None:
            phases = 0
        if isinstance(phases, int) or isinstance(phases, float):
            phases = [phases]
        phases = np.array(phases)[:, np.newaxis]
        t = np.linspace(0, T, int(T * srate))

        Yf = []
        for i in range(n_harmonics):
            if i % 2 == 0:
                Yf.append(np.stack([
                    np.sin(2 * np.pi * freqs * t + np.pi * phases),
                    np.cos(2 * np.pi * freqs * t + np.pi * phases),
                ], axis=1))
            else:
                Yf.append(np.stack([
                    np.sin(4 * np.pi * freqs * t + np.pi * phases),
                    np.cos(4 * np.pi * freqs * t + np.pi * phases),
                ], axis=1))

        Yf = np.concatenate(Yf, axis=1)
        return Yf

    def reference_s(self, freq, fs, time):
        """
        create reference signals for SSVEP.
        """
        return self.generate_mscca_references(freq, srate=fs, T=time, phases=None, n_harmonics=2)




class EEGData(EEGTools):
    def __init__(self):
        super(EEGTools, self).__init__()

    def get_online_acc(self, event_files):
        '''
        获取在线准确率
        '''
        acc = []
        for event in (event_files):
            # load total MAT data
            event_iter = scio.loadmat(event)['stimevent'][0][0]

            # get data we need
            right_label = [i.item() for i in event_iter['stimnum'][:, 0] if i != 0]
            online_label = [i.item() for i in event_iter['stimnum'][:, 1] if i != 0]
            acc.append(np.round(100*self.loss(right_label, online_label), 2))

        return acc

    def EventData(self, pth_event):
        '''
        获取采样时间点/采样数据点
        '''
        # load total MAT data
        event = scio.loadmat(pth_event)['stimevent'][0][0]

        # get data we need
        toc = [i.item() for i in event['toc'][..., 0] if i != 0]
        stimnum = [i.item() for i in event['stimnum'][:, 0] if i != 0]
        return toc, stimnum

    def get_freq(self, event):
        '''
        获取刺激频率
        '''
        return scio.loadmat(event)['stimevent'][0][0]['fps']

    # load data matrix
    def EEGData(self, pth_data):
        data_comp = scio.loadmat(pth_data)['data_comp2']
        return data_comp

    def DataDeal(self, col_index, toc, data_comp, dots, fs):
        data_use = []
        # column slice
        data_comp = np.array(data_comp[..., col_index])  # extract column

        for time_iter in toc:
            value = int(time_iter * fs)
            data = data_comp[int(value):int(value + dots), ...].T
            data_use.append(data)
        # print(f'shape of data_use: {np.shape(data_use)}')

        return data_use

    
    # -----------------------------------load datas and labels-----------------------------------

    # data concatenate for raw data
    def raw_data(self, event, data, fs, time, cap):
        '''
        raw data without filter and any other process
        '''
        dot = time * fs
        raw_temp = []
        label_temp = []
        # choose channels
        # ANT
        if cap == 'old':
            # electrodes = ['PO7', 'P3', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2']
            # electrodes = ['PO7', 'P3', 'Pz', 'PO8', 'POz', 'O1', 'Oz', 'O2']
            electrodes = ['PO7', 'P3', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2'] # visual area electrodes
            cols = self.electrode_index(electrodes)
        # GREENTEK
        elif cap == 'new':
            # electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2']
            # electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'PO8', 'POz', 'O1', 'Oz', 'O2']
            electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'PO8', 'POz', 'O1', 'Oz', 'O2'] # visual area electrodes
            # electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'P4', 'POz', 'O1', 'Oz'] # cross equipments
            cols = self.electrode_index(electrodes)
        # all electrodes
        else:
            cols = [i for i in range(32)]

        for i in range((len(event))):
            toc, stimnum = self.EventData(event[i])
            data_tmp = self.EEGData(data[i])
            data_deal = self.DataDeal(cols, toc, data_tmp, dot, fs)
            if i == 0:
                raw_temp = data_deal
                label_temp = stimnum
            else:
                raw_temp = np.concatenate((data_deal, raw_temp), 0)
                label_temp = np.concatenate((stimnum, label_temp), 0)

        raw_data = np.array(raw_temp)
        label = np.array(label_temp)

        return raw_data, label

    def mean_action_data(self, data, label):
        '''
        获取每个动作的平均数据
        data: shape(n_trials, 1500, 8)
        label: shape(8, )
        return: shape(8, 1500)
        '''
        # get unique label
        y_label = np.unique(label)
        data_1, data_2, data_3, data_4 = [], [], [], []

        # get data for each label
        for i in range(len(label)):
            if label[i] == y_label[0]:
                data_1.append(data[i])
            elif label[i] == y_label[1]:
                data_2.append(data[i])
            elif label[i] == y_label[2]:
                data_3.append(data[i])
            elif label[i] == y_label[3]:
                data_4.append(data[i])
        data_1 = np.stack([data[i] for i in range(len(label)) if label[i] == y_label[0]], axis=0)
        data_2 = np.stack([data[i] for i in range(len(label)) if label[i] == y_label[1]], axis=0)
        data_3 = np.stack([data[i] for i in range(len(label)) if label[i] == y_label[2]], axis=0)
        data_4 = np.stack([data[i] for i in range(len(label)) if label[i] == y_label[3]], axis=0)
        
        # shape(8,1500)
        data_1, data_2, data_3, data_4 = np.array(data_1.mean(axis=0)), \
            np.array(data_2.mean(axis=0)), np.array(data_3.mean(axis=0)), np.array(data_4.mean(axis=0))

        return data_1, data_2, data_3, data_4

    # data concatenate
    def filter_data(self, event, data, fs, time, cap):
        dot = time * fs
        low_pass = 3
        high_pass = 30

        filtered_temp = []
        label_temp = []
        # choose channels
        # ANT
        if cap == 'old':
            electrodes = ['PO7', 'P3', 'Pz', 'P4', 'PO8', 'POz', 'O1', 'Oz', 'O2'] # v1
            # electrodes = ['PO7', 'P3', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2'] # v2
            cols = self.electrode_index(electrodes)
            # cols = [23, 24, 25, 26, 28, 29, 30, 31] # cross_paras/ cross_days
        # GREENTEK
        elif cap == 'new':
            # electrodes = ['PO7', 'P3', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2'] # visual area electrodes
            # electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'POz', 'O1', 'Oz', 'O2'] # v1
            # electrodes = ['PO7', 'P3', 'Pz', 'P4', 'PO8', 'POz', 'O1', 'Oz', 'O2'] # cross subjects
            # cols = self.electrode_index(electrodes)
            cols = [12, 18, 23, 25, 27, 28, 29, 30, 31] # cross_paras/ cross_days
            # cols = [12, 18, 23, 25, 28, 29, 30, 31] # cross_subs

        for i in range((len(event))):
            toc, stimnum = self.EventData(event[i])
            data_tmp = self.EEGData(data[i])
            data_deal = self.DataDeal(cols, toc, data_tmp, dot, fs)
            if i == 0:
                filtered_temp = self.butter_bandpass_filter(data_deal, low_pass, high_pass, fs, order=6)
                label_temp = stimnum
            else:
                filtered_temp = np.concatenate((self.butter_bandpass_filter(data_deal, low_pass, high_pass, fs, order=6),
                                                filtered_temp), axis=0)
                label_temp = np.concatenate((stimnum, label_temp), axis=0)

        filtered_data = np.array(filtered_temp)
        label = np.array(label_temp)

        return filtered_data, label

    # data concatenate for feedback
    def feedback_data(self, event, data, fs, time, cap):
        dot = time * fs
        low_pass = 3
        high_pass = 30

        filtered_temp = []
        label_temp = []
        # ANT
        if cap == 'old':
            electrodes = ['PO7', 'P3', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2']
            cols = self.electrode_index(electrodes)
        # GREENTEK
        elif cap == 'new':
            electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'P4', 'POz', 'O1', 'Oz', 'O2']
            # electrodes = ['PO3', 'PO4', 'PO7', 'Pz', 'P4', 'POz', 'O1', 'Oz'] # cross equipments
            cols = self.electrode_index(electrodes)

        for i in range((len(event))):
            toc, stimnum = self.EventData(event[i])
            data_tmp = self.EEGData(data[i])
            data_deal = self.DataDeal(cols, toc, data_tmp, dot, fs)
            if i == 0:
                filtered_temp = self.butter_bandpass_filter(data_deal, low_pass, high_pass, fs, order=6)
                label_temp = stimnum
            else:
                filtered_temp = np.concatenate((self.butter_bandpass_filter(data_deal, low_pass, high_pass, fs, order=6),
                                                filtered_temp), axis=0)
                label_temp = np.concatenate((stimnum, label_temp), axis=0)

        feedback_data = np.array(filtered_temp)
        label = np.array(label_temp)

        return feedback_data, label