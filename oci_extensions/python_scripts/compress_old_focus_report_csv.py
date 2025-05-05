import os
import time
import gzip
import shutil
from datetime import datetime, timedelta

def compress_old_csv_files(parent_directory, days_threshold=5):
    """
    Searches for CSV files older than a specified number of days within a directory
    and its subdirectories, and compresses them using gzip in their respective directories.

    Args:
        parent_directory (str): The root directory to start the search from.
        days_threshold (int, optional): The number of days to consider a file "old".
            Defaults to 5.
    """
    now = datetime.now()
    threshold_date = now - timedelta(days=days_threshold)

    # Use os.walk to recursively traverse directories
    for root, _, files in os.walk(parent_directory):
        for file in files:
            if file.lower().endswith(".csv"):
                filepath = os.path.join(root, file)
                try:
                    # Get the file's last modification time
                    file_modification_time = datetime.fromtimestamp(os.path.getmtime(filepath))

                    # Check if the file is older than the threshold
                    if file_modification_time < threshold_date:
                        print(f"Compressing: {filepath}")
                        # Create the gzip file in the same directory
                        gzipped_filepath = filepath + ".gz"
                        try:
                            # Use a buffer to handle potentially large files efficiently
                            with open(filepath, 'rb') as infile, gzip.open(gzipped_filepath, 'wb') as outfile:
                                shutil.copyfileobj(infile, outfile)  # Copy the file contents

                            # Remove the original CSV file after successful compression
                            os.remove(filepath)
                            print(f"Successfully compressed and removed: {filepath}")
                        except Exception as e:
                            print(f"Error compressing {filepath}: {e}")
                except OSError as e:
                    print(f"Error accessing file {filepath}: {e}")
                    if e.errno == 2:
                        print(f"File not found: {filepath}.  It may have been deleted during processing.")
                    #else: #REMOVE this else to show all errors
                    #    print(f"OSError accessing {filepath}: {e}") #REMOVE this line



def main():
    """
    Main function to run the script.  The parent directory and age threshold are
    defined here.
    """
    # Define the parent directory here
    parent_directory = "/home/opc/oci_extensions/data/fc"  # Replace with the actual path

    # Define the age threshold in days here
    days_threshold = 2

    #check that the directory exists
    if not os.path.isdir(parent_directory):
        print(f"Error: The directory {parent_directory} does not exist.")
        return

    print(f"Searching for CSV files older than {days_threshold} days in {parent_directory} and its subdirectories and compressing them in place.")
    compress_old_csv_files(parent_directory, days_threshold)
    print("Finished processing.")



if __name__ == "__main__":
    main()

