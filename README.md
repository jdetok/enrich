# enrich
Python CLI for enriching a dataset with an additional column(s) by joining two datasets with a shared column

## Required .env vars
`ORA_USER`, `ORA_PASS`, `ORA_PORT`, `ORA_HOST`, `ORA_NAME`, `TEST_BANNER_ID`

## Usage example
### Run test mode
- Make sure .env file contains a valid `TEST_BANNER_ID` variable
- CLI usage:
    `python main.py -q test`
- The test functions will add the valid Banner ID to the test.csv file, run the test query against
the valid Banner ID, then remove the real Banner ID from the test.csv file

### Add Banner IDs to a CSV file containing SSNs
- Input file contents:
    ```
    "ssn","name"
    "999999999","example"
    ```
- CLI usage:
    `python main.py -f <file_with_ssn_column.csv> -i 'ssn' - o 'bid'`
- Output file contents:
    ```
    "Banner ID","ssn","name"
    "001122334","999999999","example"
    ```
