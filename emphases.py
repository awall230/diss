from music21 import *
import os
import sys
import math
from fractions import gcd
import string
import unicodedata
import numpy as np
import matplotlib.pyplot as plt

filename = '/Users/adamwaller/Documents/Eastman/cmudict.0.4'    #pronunciation dictionary
infile = open(filename, 'r')
syllist = infile.readlines()
i = 0
while syllist[i][0] == "#": # skip comments section
    i += 1
infile.close()

filename = '/Users/adamwaller/Documents/Eastman/english_function_words'
infile = open(filename, 'r')
function_word_list = infile.readlines()
infile.close()

word_dict = {}
emphasis_dict = {}

def build_dict(function_words = False):
    """
    Builds data structure for pronunciation dictionary with relative emphasis levels
    """
    for j in range(i, len(syllist)):
    #for j in range(200, 300):
        temp = syllist[j].split()
        word = temp[0]
        #strip punctuation (can't use method below b/c this is a string, not unicode)
        word = word.translate(string.maketrans("",""), string.punctuation)
        word_dict[word] = temp[1:len(temp)]
        temp = word_dict[word] #temp now just the pronunciations
        emph_list = []
        for syl in temp:
            try:
                emphlevel = int(syl[-1])
                emph_list.append(emphlevel)
            except ValueError:
                continue
        emphasis_dict[word] = emph_list

    if function_words:
        for word in function_word_list:
            word = word.strip().upper()
            if word in emphasis_dict and len(emphasis_dict[word]) == 1:
                emphasis_dict[word] = [0]

#print emphasis_dict


def get_data(rap_file):
    """
    Parses metrical/emphasis information from a symbolic rap verse
    """
    rap_file = converter.parse(rap_file)

    i = -1
    n = None
    while not isinstance(n, stream.Part):
        i += 1
        n = rap_file[i]
    rap_index = i

    lyrics_string = ''
    measure_list = rap_file[rap_index]
    word = ''
    word_offsets = []
    unknown_words = []
    word_emphases = []
    metric_weights = []
    aggregate_emphases = []
#    for k in range(len(measure_list)):
    k = 0
    while k < len(measure_list):
        meas = measure_list[k]
        if isinstance(meas, stream.Measure):
            i = 0
            while i < len(meas):
                if isinstance(meas[i], note.Note) and meas[i].lyrics:
                    n = meas[i]
                    if n.lyrics[0].syllabic == 'single':
                        word = n.lyrics[0].text

                    #multisyllabic case: build up by syllable
                    elif n.lyrics[0].syllabic == 'begin':
                        word = n.lyrics[0].text
                        word_offsets.append(n.offset)
                        i += 1
                        #crossed barline, go on to next measure
                        if i >= len(meas):
                            k += 1
                            meas = measure_list[k]
                            i = 0
                            while not isinstance(meas[i], note.Note):
                                i += 1
                        while not meas[i].lyrics:
                            i += 1
                        n = meas[i]
                        while n.lyrics[0].syllabic != 'end':
                            word += n.lyrics[0].text
                            word_offsets.append(n.offset)
                            i += 1
                            #crossed barline, go on to next measure
                            if i >= len(meas):
                                k += 1
                                meas = measure_list[k]
                                i = 0
                                while not isinstance(meas[i], note.Note):
                                    i += 1
                            #if there's a note with no lyrics, skip it
                            n = meas[i]
                            while not n.lyrics:
                                i += 1
                                n = meas[i]

                        #reached end syllable
                        word += n.lyrics[0].text

                    #word gotten, process with offsets and emphases
                    lyrics_string += word + ' '
                    word_offsets.append(n.offset)
                    word_emphases = get_emphases(word)
                    metric_weights = [metric_weight(x) for x in word_offsets]
                    if word_emphases:
#                        print word + ' ' + str(zip(word_offsets, word_emphases, metric_weights))
                        aggregate_emphases.append(zip(word_offsets, word_emphases, metric_weights))
                    else:
                        print word + ' ' + str(word_offsets)
                    if not word_emphases:   #not found in dictionary
                        unknown_words.append(word)
                    word_offsets = []
                    word_emphases = []
                    word = ''
                i += 1
        k += 1


#    print lyrics_string
    print unknown_words
#    print aggregate_emphases
    return aggregate_emphases

def get_counters(aggregate_emphases):
    """
    Gathers some stats from emphasis information for a particular verse
    """
    onset_counters = {}
    emph_counters = {}
    non_emph_counters = {}
    total_weights = 0
    counter = 0
    total_emph_weights = 0
    emph_counter = 0
    total_non_emph_weights = 0
    non_emph_counter = 0
    for holder in aggregate_emphases:
        for beat, emph, weight in holder:
            if beat not in onset_counters:
                onset_counters[beat] = 1
            else:
                onset_counters[beat] += 1

            if emph > 0:
                total_emph_weights += weight
                emph_counter += 1
                if beat not in emph_counters:
                    emph_counters[beat] = 1
                else:
                    emph_counters[beat] += 1
            elif emph == 0:
                total_non_emph_weights += weight
                non_emph_counter += 1
                if beat not in non_emph_counters:
                    non_emph_counters[beat] = 1
                else:
                    non_emph_counters[beat] += 1

            total_weights += weight
            counter += 1

    # print counter
    # print total_weights/counter
    #
    # print
    # print total_emph_weights/emph_counter
    #
    # print
    # print total_non_emph_weights/non_emph_counter
    #
    # print '\n\n'
    # print onset_counters
    # print '\n'
    # print emph_counters
    # print '\n'
    # print non_emph_counters



def cross_entropy(profile, master_profile):
    """
    Measures Shannon cross entropy
    """
    total = 0
    for i in range(len(profile)):
        total += profile[i,1] * math.log(master_profile[i,1], 2)
    return total * -1.0

def get_raw_profile(onset_counters):
    """
    Calculates number of onsets on each beat class
    """
    profile = []
    for i in range(16):
        beat = i/4.0
        if beat in onset_counters:
            profile.append((beat, onset_counters[beat]))
        else:
            profile.append((beat, 0))
    profile = np.array(profile)
    return profile

def get_profile(raw_profile):
    """
    Calculates percentage of total onsets represented by each beat class
    """
    profile = np.copy(raw_profile)
    profile[:,1] *= 1.0/sum(profile[:,1])
    return profile



def get_emphases(word):
    """
    Helper function to get relative emphases of each syllable in a word
    """
    #strip punctuation
    word = strip_punctuation(word)
    word = word.upper()
    if word in emphasis_dict:
        return emphasis_dict[word]
    else:
        return None

def metric_weight(off):
    """
    Self-defined function for measuring metrical weight of a beat class
    """
#    return gcd(100.0 * (4.0 - off), 400.0)/100.0
    return gcd(100.0 * (1.0 - off), 100.0)/100.0

def strip_punctuation(s):
    """
    Removes punctuation from a string (for lookup in pronunciation dictionary)
    """
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    return s.translate(string.maketrans("",""), string.punctuation)


#--main
# if len(sys.argv) > 1:
#     filename = "/Users/adamwaller/Documents/Eastman/Dissertation/transcriptions/" + str(sys.argv[1])
# else:
#     filename = "/Users/adamwaller/Documents/Eastman/Dissertation/transcriptions/lose_yourself.xml"
build_dict(function_words = True)
#(emphs, on_counters) = get_data(filename)


def measure_amws(emphs):
    """
    Gets average metrical weights (defined above) of a verse
    """
    mnum = 0
    measure_syncs = []
    temp = [0]  #placeholder
    temp_average = 0
    prev_off = 10.0 #arbitrarily large number
    for holder in emphs:
        for off, stress, m_weight in holder:
            if off < prev_off:  #new measure, reset everything
                temp_average = sum(temp)/len(temp)
                measure_syncs.append((mnum, temp_average))
                temp = []
                mnum += 1
            temp.append(m_weight)
            prev_off = off

    temp_average = sum(temp)/len(temp)
    measure_syncs.append((mnum, temp_average))
    measure_array = np.array(measure_syncs)
    return measure_array

# print measure_syncs
# measure_array = np.array(measure_syncs)
#plt.plot(measure_array[:,0], measure_array[:,1], 'o-')
#plt.show()

# print entropy(on_counters)
# profile = get_profile(on_counters)
# print profile
# plt.plot(profile[:,0], profile[:,1], 'o-')
# plt.show()



                
    
    
    
        
