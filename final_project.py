import zipfile
import PIL
import pytesseract
import cv2 as cv
import numpy as np
from IPython.display import display
from PIL import ImageFont, ImageDraw, Image

WORDSHEIGHT = 40
ZERO = 0
THUMBNAILWIDTH = 100
THUMBNAILHEIGHT = 100
# unzip the zip file and store unzipped images to image objects.

# convert the english in the pictures to text and store them into a data structure that can be identified according to
# different newspaper pages.


# crop and store all detected faces and store them into a data structure that can be identified according to
# different newspaper papes.

def get_dict_img(file_path, scaleFactor):
    
    
    zip_file = zipfile.ZipFile(file_path)
    
    dict_img = {}
    
    for file in zip_file.infolist():
        
        print(file.filename)
        image = PIL.Image.open(zip_file.open(file))

        image.info['dpi'] = (300, 300)
        
        dict_img[file.filename] = []
        dict_img[file.filename].append(image)

        text = pytesseract.image_to_string(image)

        dict_img[file.filename].append(text)

        # loading the face detection classifier
        face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

        face_pic = []

        cv_img = np.array(dict_img[file.filename][0])
        gray = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)
        faces_rect = face_cascade.detectMultiScale(gray, scaleFactor)

        pil_img = dict_img[file.filename][0]

        try:

            for x,y,w,h in faces_rect:
                cropped_img = pil_img.crop((x,y,w+x,h+y))
                cropped_img.thumbnail((100,100))
                face_pic.append(cropped_img)

            dict_img[file.filename].append(face_pic)

        except:

            dict_img[file.filename].append(None)

    return dict_img

    
# test if a word to be searched is in any specific newspaper. Create a contact sheet and produce appropriate output.
def searchndisplay(name, filepath, scaleFactor):
    dict_img = get_dict_img(filepath, scaleFactor)
    disp_con_sheet(dict_img, name)

def height_of_contact_sheet(dict_img, name):
    height = 0
    for filename in dict_img.keys():
        if (is_name_in_text(name, dict_img, filename)):
            if (is_contact_sheet_tmp(filename, dict_img)):
                height += dict_img[filename][3].height + WORDSHEIGHT
            else:
                height += WORDSHEIGHT * 2
    return height

def is_name_in_text(name, dict_img, filename):
    return name in dict_img[filename][1]

def get_position(filename, dict_img, name):
    height_0 = 0
    height_1 = 0
    
    for file_name in dict_img.keys():
        if is_name_in_text(name, dict_img, file_name):
            if file_name != filename:
                if dict_img[file_name][3] != None:
                    print("{}'s height is {}".format(file_name, dict_img[file_name][3].height))
                    height_0 += dict_img[file_name][3].height + WORDSHEIGHT
                    print("height_0 is {}".format(height_0))
                else:
                    print("{} entered".format(file_name))
                    height_0 += WORDSHEIGHT * 2
                
            else:
                break
        
    height_1 = height_0 + WORDSHEIGHT
    return [(ZERO, height_0), (ZERO, height_1)]

def is_contact_sheet_tmp(filename, dict_img):
    return dict_img[filename][3] != None
    
def disp_con_sheet(dict_img, name):

    dict_img_f = con_sheet_tmp(dict_img, name)
    contact_sheet = PIL.Image.new(dict_img_f[list(dict_img_f.keys())[0]][0].mode, (100*5,
                                                                        height_of_contact_sheet(dict_img_f, name)))
    
    contact_sheet_txt = PIL.Image.new('RGB', (contact_sheet.width, contact_sheet.height))
    # get a font
    fnt = ImageFont.truetype('readonly/fanwood-webfont.ttf', 36)
    # get a drawing context
    d = ImageDraw.Draw(contact_sheet)
    
    for filename in dict_img_f.keys():
        print("{}{}".format(name in dict_img_f[filename][1], filename))
        if (is_contact_sheet_tmp(filename, dict_img_f)):
            display(dict_img_f[filename][3])
            print("thumbnail position {}".format(get_position(filename, dict_img_f, name)[1]))
            contact_sheet.paste(dict_img_f[filename][3], get_position(filename, dict_img_f, name)[1])
            d.rectangle([get_position(filename, dict_img_f, name)[0][0],
                        get_position(filename, dict_img_f, name)[0][1],
                        get_position(filename, dict_img_f, name)[0][0]+THUMBNAILWIDTH*5,
                        get_position(filename, dict_img_f, name)[0][1]+WORDSHEIGHT], (255,255,255), (255,255,255))
            d.text(get_position(filename, dict_img_f, name)[0], "Results found in file {}".format(filename), font=fnt, fill=(0,0,0))
            print("text position {}".format(get_position(filename, dict_img_f, name)[0]))
            contact_sheet_txt.paste(contact_sheet, (0, 0))
        elif (is_name_in_text(name, dict_img_f, filename)):
            # draw text
            print("{} entered to draw".format(filename))
            d.rectangle([get_position(filename, dict_img_f, name)[0][0],
                        get_position(filename, dict_img_f, name)[0][1],
                        get_position(filename, dict_img_f, name)[0][0]+THUMBNAILWIDTH*5,
                        get_position(filename, dict_img_f, name)[0][1]+WORDSHEIGHT],  (255,255,255), (255,255,255))
            d.text(get_position(filename, dict_img_f, name)[0], "Results found in file {}".format(filename), font=fnt, fill=(0,0,0))
            print("text position {}".format(get_position(filename, dict_img_f, name)[0]))
            d.rectangle([get_position(filename, dict_img_f, name)[1][0],
                        get_position(filename, dict_img_f, name)[1][1],
                        get_position(filename, dict_img_f, name)[1][0]+THUMBNAILWIDTH*5,
                        get_position(filename, dict_img_f, name)[1][1]+WORDSHEIGHT],  (255,255,255), (255,255,255))
            d.text(get_position(filename, dict_img_f, name)[1], "But there were no faces in the file".format(filename), font=fnt, fill=(0,0,0))
            print("t-text position {}".format(get_position(filename, dict_img_f, name)[1]))
            contact_sheet_txt.paste(contact_sheet, (0, 0))

    display(contact_sheet_txt)


def con_sheet_tmp(dict_img, name):
    for filename in dict_img.keys():
        if name in dict_img[filename][1]:
            
            try:
                
                images = dict_img[filename][2]
                num = len(images)
                first_image = images[0]
                contact_sheet_tmp = PIL.Image.new(first_image.mode, (THUMBNAILWIDTH*5,THUMBNAILHEIGHT*((num - 1)//5 + 1)))
                x=0
                y=0

                for img in images:
                    # Lets paste the current image into the contact sheet
                    contact_sheet_tmp.paste(img, (x, y) )
                    # Now we update our X position. If it is going to be the width of the image, then we set it to 0
                    # and update Y as well to point to the next "line" of the contact sheet.
                    if x+THUMBNAILWIDTH == contact_sheet_tmp.width:
                        x=0
                        y=y+THUMBNAILHEIGHT
                    else:
                        x=x+THUMBNAILWIDTH
                dict_img[filename].append(contact_sheet_tmp)

            except:
        
                dict_img[filename].append(None)
        else:
            dict_img[filename].append(None)

    return dict_img

            
#for scaleFactor in range(11, 20, 1):
#    print("scaleFactor:{}".format(scaleFactor/10))
scaleFactor = 1.7

searchndisplay("Christopher", './readonly/small_img.zip', scaleFactor)
searchndisplay("Mark", './readonly/images.zip', scaleFactor)



