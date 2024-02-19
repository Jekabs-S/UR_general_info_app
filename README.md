# UR_general_info_app

This is a simple app that I made to help out a friend that fetches data from the [Latvian Enterprise Register (UR)](https://data.gov.lv/dati/lv/dataset/uz/resource/25e80bf3-f107-4ab4-89ef-251b5b9374e9) using an input .xlsx file. The input file should contain a single column named "entity_name", where the values are the names of registered entities in the UR.

The app searches the UR data source for general registry information and saves the found entities to an "entity_ur_data.xlsx" file.

## Considerations

- The entities will only be found if the given names are exactly as they are found in the UR data source.
- The script uses 8 threads to speed up the process. However, a large number of values might still take time. Don't worry if the script keeps going for a long time in those cases, it will get there eventually.

## Usage

1. Prepare your .xlsx file with a column named "entity_name" containing the names of the entities you want to search for.
2. You can run the `fetching_ur_data.py` script as a standalone by adding the input.xlsx file to the repository and then running `fetching_ur_data.py`. Or use the Flask app as an interface, by running `app.py` and then navigating to (http://localhost:5000) in your browser and then uploading the input .xlsx file and pressing "Process data".
3. In either case the scripts will then create an "entity_ur_data.xlsx" file with the found entities as the end result.

## Dependencies

This project requires Python 3 and the following Python libraries installed:

- [Flask](https://flask.palletsprojects.com/)
- [pandas](https://pandas.pydata.org/)
- [openpyxl](https://openpyxl.readthedocs.io/)
- [requests](https://requests.readthedocs.io/)

You can install these dependencies using `pip`:

```sh
pip install -r requirements.txt
