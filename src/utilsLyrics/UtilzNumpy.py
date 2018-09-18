'''
Created on May 22, 2015

@author: joro
'''
import numpy as np


def detail_array_differences(array1, array2):
    arr_diff = abs(array1  - array2)

    print("abs diff:")
    print(np.max(arr_diff))
    
    # print vallues of top 10 most different values 
    indices = arr_diff.ravel().argsort()[-10:]
    indices = (np.unravel_index(i, arr_diff.shape) for i in indices)
    print([(array1[i], array2[i], i) for i in indices])


def assertListsEqual(list1, list2):
    '''
    assert python lists are equal
    '''
    assert all([a==b for a,b in zip(list1, list2)])
  
def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def map_span(value, sourceMin, sourceMax, targetMin, targetMax):
    '''
    map a value from an source span to a target span 
    '''
    # Figure out how 'wide' each range is
    sourceSpan = sourceMax - sourceMin
    targetSpan = targetMax - targetMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - sourceMin) / float(sourceSpan)

    # Convert the 0-1 range into a value in the right range.
    return targetMin + (valueScaled * targetSpan)