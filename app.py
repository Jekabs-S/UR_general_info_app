from flask import Flask, request, send_file, make_response
import pandas as pd
import io
import os
import tempfile
import fetching_ur_data as ur_data  # make sure fetching_ur_data.py is in the same directory

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        # Save the file to a temporary file on disk
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)

        # Read the file into a pandas DataFrame
        df = pd.read_excel(temp_file.name)

        try:
            # Try to get the 'entity_name' column
            entity_names = df['entity_name'].tolist()
        except KeyError:
            # If the 'entity_name' column does not exist, return an error message
            return ('The uploaded file is incorrectly formatted. Please make sure it has only one column named "entity_name".', 400)

        # Fetch the data for the entity names
        records = ur_data.fetch_and_insert_data(entity_names)

        # Convert the records to a DataFrame
        processed_df = pd.DataFrame(records)

        # Save the DataFrame to a BytesIO object as an .xlsx file
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        processed_df.to_excel(writer, sheet_name='Sheet1')
        writer.close()  # Close the Pandas Excel writer
        output.seek(0)  # Seek to the start of the stream
        # Delete the temporary file
        os.unlink(temp_file.name)

        # Return the .xlsx file as a download
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=entity_ur_data.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Search for entity names in UR registry</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #121212; /* Dark background */
                color: #f0f0f0; /* Light text */
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .container {
                width: 80%;
                max-width: 800px;
                padding: 20px;
                background-color: #1f1f1f; /* Darker container */
                box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1); /* Light shadow */
                text-align: center;
            }
            h1 {
                color: #f0f0f0; /* Light text */
            }
            p {
                line-height: 1.6;
            }
            #uploadForm {
                margin-top: 20px;
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
            footer {
                padding: 20px;
                background-color: #1f1f1f; /* Darker footer */
                color: #f0f0f0; /* Light text */
                text-align: center;
            }
            #processing {
                width: 100%;
                height: 20px;
                background-color: #f3f3f3;
                border: 1px solid #bbb;
                display: none;
                overflow: hidden;  /* Add this line */
            }
            #processing div {
                height: 100%;
                width: 100%;  /* Change this from 50% to 100% */
                background-color: #bbb;
                animation: progress 2s linear infinite;
            }
            @keyframes progress {
                from { transform: translateX(-100%); }  /* Change this from margin-left: -50%; to transform: translateX(-100%); */
                to { transform: translateX(100%); }  /* Change this from margin-left: 100%; to transform: translateX(100%); */
            }
        </style>
        <script>
            function submitForm() {
                var form = document.getElementById('uploadForm');
                var formData = new FormData(form);
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/', true);
                xhr.responseType = 'blob';
                xhr.onload = function () {
                    document.getElementById('processing').style.display = 'none';
                    if (this.status === 200) {
                        var blob = new Blob([this.response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
                        var link = document.createElement('a');
                        link.href = window.URL.createObjectURL(blob);
                        link.download = 'entity_ur_data.xlsx';
                        link.click();
                    } else {
                        alert('The uploaded file is incorrectly formatted. Please make sure it has only one column named "entity_name".');
                    }
                };
                xhr.send(formData);
                document.getElementById('processing').style.display = 'block';
                return false;
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Search for entity names in UR registry</h1>
            <p>This is a simple app to seach for entity names in UR registry.</p>
            <p>The output Excel file will contain the found entity general information from "https://data.gov.lv/dati/lv/dataset/uz/resource/25e80bf3-f107-4ab4-89ef-251b5b9374e9".</p>
            <p>Please make sure your input Excel file is formatted correctly. There should only be one column called "entity_name".</p>
            <form id="uploadForm" method=post enctype=multipart/form-data onsubmit="return submitForm()">
                <input type=file name=file>
                <input type=submit value="Process data">
            </form>
            <div id="processing"><div></div></div>
        </div>
        <footer>
            <p>Made by <a href="https://github.com/Jekabs-S" style="color: #fff;">Jekabs-S</a></p>
        </footer>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)