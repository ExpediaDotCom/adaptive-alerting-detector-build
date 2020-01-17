from pandas import read_csv


def read_timeseries_csv(csv_filename: str):
    """
    Reads a CSV file and returns a Pandas DataFrame with a DateTimeIndex and column of values.
    CSV File format: <datetime>, <value>
    CSV file assumptions:
    - First column contains datetime values and can be used as an index
    - Second column contains the values to be used
    - Subsequent columns may exist but are not used
    - The file may or may not have a header line
    :param csv_filename: Path to csv file
    :return: Pandas DataFrame
    """
    df = read_csv(csv_filename,
                  index_col=0,      # The first column is to be used as an index
                  parse_dates=True) # The index column can be parsed as a datetime
    return df