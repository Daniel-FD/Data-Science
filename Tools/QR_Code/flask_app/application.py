# importing the required libraries
import os
import pandas as pd
from flask import Flask, render_template, request, send_file, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import qrcode
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image 
import os
import glob

# https://www.codeunderscored.com/upload-download-files-flask/#Serving_the_files

# INPUT!

# initialising the flask app
application = Flask(__name__)
application.secret_key = os.urandom(24)

def delete_files_from_folder(folder):
    files = glob.glob(folder + '*')
    for f in files:
        os.remove(f)

# Creating the upload folder
upload_folder = "uploads/"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)
delete_files_from_folder(upload_folder)
# Creating the download folder
download_folder = "downloads/"
if not os.path.exists(download_folder):
    os.mkdir(download_folder)
delete_files_from_folder(download_folder)
# QR Code folder
qr_codes_folder = "qr_codes/"
if not os.path.exists(qr_codes_folder):
    os.mkdir(qr_codes_folder)
delete_files_from_folder(qr_codes_folder)
# Files folder
files_folder = "files/"
if not os.path.exists(files_folder):
    os.mkdir(files_folder)
# PDF QR code
pdf_filename = 'qr_code.pdf'
# Max size of the file
application.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# Configuring the upload folder
application.config['UPLOAD_FOLDER'] = upload_folder
# Configuring the download folder
application.config['DOWNLOAD_FOLDER'] = download_folder
# Configuring the qr codes folder
application.config['QR_CODES_FOLDER'] = qr_codes_folder
# Configuring the files folder
application.config['FILES_FOLDER'] = files_folder

#
@application.route('/', methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':  # check if the method is post
        file = request.files['file']  # get the file from the files object
        # Saving the file in the required destination
        filename = secure_filename(file.filename)
        session['filename'] = filename
        delete_files_from_folder(upload_folder)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))  # this will secure the file
        # ---------------------------------------
        # ---------------------------------------
        # Step 1: convert file into pandas dataframe
        try:
            df = pd.read_excel(os.path.join(application.config['UPLOAD_FOLDER'], filename), header = 1)
        except Exception as e: 
            print(e, "Is the table in the right format?")
        # Step 2: Create the QR Codes
        file_name_list = []
        delete_files_from_folder(qr_codes_folder)
        for i in range(len(df)):
            unique_id_temp = df['Name on Frame'].iloc[i]
            if len(unique_id_temp) > 2:
                qr_code_message = str(df['Name on Frame'].iloc[i] + ' - ' + df['Customer Name'].iloc[i])
                print(qr_code_message)
                img = qrcode.make(qr_code_message)
                im = img.convert('LA')
                im = plt.imshow(im, cmap='gray')
                im = plt.title(df['Name on Frame'].iloc[i] + ': ' + df['Customer Name'].iloc[i])
                im = plt.axis('off')
                name = df['Name on Frame'].iloc[i] + '_QR_code.jpg'
                file_name_list.append(name)
                plt.savefig(os.path.join(application.config['QR_CODES_FOLDER']) + name, transparent  = True, bbox_inches = 'tight', dpi = 1000)
                plt.close()
        # Step 3: Read QR codes from folder and generate pdf
        img_folder_path = os.path.join(application.config['QR_CODES_FOLDER'])
        delete_files_from_folder(download_folder)
        pdf_path = os.path.join(application.config['DOWNLOAD_FOLDER'])
        filename_path = pdf_path + pdf_filename
        images = [Image.open(img_folder_path + f) for f in file_name_list]
        images[0].save(filename_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:])
        # 
        return render_template('upload.html')
    #
    return render_template('upload.html')
#
# Sending the file to the user
@application.route('/download/')
def download():
        filepath = os.path.join(application.config['DOWNLOAD_FOLDER']) + '/' + pdf_filename
        print("filepath.....")
        print(filepath)
        return send_file(filepath, as_attachment=True)
#
if __name__ == '__main__':
    application.debug = True
    application.run()  # running the flask app