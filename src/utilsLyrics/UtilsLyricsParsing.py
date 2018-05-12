'''
Created on 24/04/2018

@author: joro
'''
import re
import codecs
import json
import sys



def load_section_annotations(lyrics_URI):
    '''
    load sections from a file
    
    Parameters
    -----------------
    lyrics_URI: string
        the lyrics lines have to be in the format <start_ts> <end_ts> <line> separated by tabs 
    '''
    if lyrics_URI.endswith('json'):
        return load_section_annotations_json(lyrics_URI)
    
    ########## load from tab-delimited file. an empty line marks the end of a new section

    start_times, end_times, lines = load_delimited(lyrics_URI, [float, float, str], delimiter='\t') # puts marker -1 at an empty line
    start_timestamps = []
    all_sections_lyrics = []
    should_start_section = 1
    for start_time, end_time, line in zip( start_times, end_times, lines):
        
        
        if line != -1: #next line
            if should_start_section:
                section_lyrics = []
                start_timestamps.append(start_time); should_start_section = 0
            section_lyrics.append(line)
              
        else: # end of section
            should_start_section = 1
            section_lyrics_str = "\n".join(section_lyrics) # because it is uniformedly parsed later for all cases
            all_sections_lyrics.append(section_lyrics_str)
    return start_timestamps, all_sections_lyrics








def load_delimited_variants(filename, delimiter=r'\s+'):
    '''
    load from delimited file
    
    '''
#     str_ = lambda val:float(val.replace(u'\u2028', ''))
    starts = None
    ends = None
#     try:
    starts, ends, labels = load_delimited(filename, [float, float, str], delimiter) # start times and end times given
#     except Exception as e: # no times given
#         labels = load_delimited(filename, [str], delimiter)
    return  starts, ends, labels


def load_delimited(filename, converters, delimiter=r'\s+'):
    r"""Utility function for loading in data from an annotation file where columns
    are delimited.  The number of columns is inferred from the length of
    the provided converters list.

    Examples
    --------
    >>> # Load in a one-column list of event times (floats)
    >>> load_delimited('events.txt', [float])
    >>> # Load in a list of labeled events, separated by commas
    >>> load_delimited('labeled_events.csv', [float, str], ',')

    Parameters
    ----------
    filename : str
        Path to the annotation file
    converters : list of functions
        Each entry in column ``n`` of the file will be cast by the function
        ``converters[n]``.
    delimiter : str
        Separator regular expression.
        By default, lines will be split by any amount of whitespace.

    Returns
    -------
    columns : tuple of lists
        Each list in this tuple corresponds to values in one of the columns
        in the file.

    """
    # Initialize list of empty lists
    n_columns = len(converters)
    columns = tuple(list() for _ in range(n_columns))

    # Create re object for splitting lines
    splitter = re.compile(delimiter)

    # Note: we do io manually here for two reasons.
    #   1. The csv module has difficulties with unicode, which may lead
    #      to failures on certain annotation strings
    #
    #   2. numpy's text loader does not handle non-numeric data
    #
#     with _open(filename, mode='r') as input_file:
    with codecs.open(filename, 'rU', encoding='utf8', errors='ignore') as input_file:
        for row, line in enumerate(input_file, 1):
            stripped_line = strip_line(line)
            # Split each line using the supplied delimiter
            data = splitter.split(stripped_line, n_columns - 1)
            
            if data == ['']: # puts -1 marker for an empty line:
                for column in columns:
                    column.append(-1); 
                continue
            # Throw a helpful error if we got an unexpected # of columns
            if n_columns != len(data):
                raise ValueError('Expected {} columns, got {} at '
                                 '{}:{:d}:\n\t{}'.format(n_columns, len(data),
                                                         filename, row, line))

            for value, column, converter in zip(data, columns, converters):
                # Try converting the value, throw a helpful error on failure
                try:
                    converted_value = converter(value)
                except:
                    raise ValueError("Couldn't convert value {} using {} "
                                     "found at {}:{:d}:\n\t{}".format(
                                         value, converter.__name__, filename,
                                         row, line))
                column.append(converted_value)

    # Sane output
    if n_columns == 1:
        return columns[0]
    else:
        return columns
    
    
def strip_line(line):
    '''
    right strip any type of end line signs
    '''
    line = line.replace('\u2028', '')
#         line = line.replace('\xe2\x80\xa8','') # replace end of line
    line = line.rstrip()
    return line



def load_section_annotations_json(lyrics_URI):
    '''
    load from json format using explicitly given section field
    not used so far 
    '''
    f = open(lyrics_URI, 'r')
    sectionMetadata = json.load(f)
    if 'sections' in sectionMetadata:
        scoreSectionAnnos = sectionMetadata['sections']
    else:
        sys.exit("cannot find neither key sections nor segmentations in score metadata" )
    
    begin_timestamps = []
    section_lyrics = []
    for section in scoreSectionAnnos:
        if  'begin_ts' in section:
            begin_timestamps.append( float(section['begin_ts']) )
        
        if 'lyrics' in section:
            lyrics = section['lyrics']
            section_lyrics.append( lyrics )
      
    return begin_timestamps, section_lyrics
