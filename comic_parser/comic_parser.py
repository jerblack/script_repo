

"""
    parse a comic file name into the most likely comic details for the given comic
    
    - iterate through comics in folder
    - for each comic
        parse the file name using the potential comic details in different formats
        created multiple templates and attempt to map file name to each template format
        parse resulting data and use that to score the likelihood that the format was correct
    - details parsed into include
        title, series, year, issue_number, volume_number, extension, release_group
    - define a series of potential template formats to test for
        [title] [issue_number] ([year]) ([release_group]).
        
        
"""