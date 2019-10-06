#    Ablation Spot Placer
#    Copyright (C) 2019. Kosta Crnobrnja
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    You can contact author at k.s.crnobrnja@gmail.com

from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from tkinter.scrolledtext import ScrolledText
from tkinter.simpledialog import askstring 
from os import listdir
from sys import platform
from collections import deque
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import copy
import cv2
import PIL.Image, PIL.ImageTk
import pytesseract
import shutil, os 

# the user inputs folders which represent samples 
# each folder contains images which are loaded in with the folder
# folders are called groups (of images) in-program
# the user edits each image within a group by placing circles on them
# when the user is done placing circles he clicks the "CREATE PDF" button
# this button creates a pdf displaying groups of images labeled accordingly
# each page of the pdf has 3 columns of images
###
# the main hierarchical structure is achieved by creating a main_list that looks like this:
# main_list = [ [group_number, group_name, main_image_list], ...]
# main_image_list = [ [image_number, image_iteration_list, thumbnail image, circle radius], ...]
# image_iteration_list = [base image, base image + 1 circle, base image + 2 circles, base image + 3 circles, ...]

main_list = deque() # set main_list to an empty list at the start of the program

# functions to call when clicking the file and help menus

def NewProject():
    global main_list
    result = messagebox.askquestion("Begin a new project", "All your data in this session will be lost. Are you sure?", icon = 'warning')
    if result == 'yes':
        canvas_l4.itemconfig(image_on_canvas_l4, image = photo2)
        canvas_l3.itemconfig(image_on_canvas_l3, image = photo2)
        canvas_l2.itemconfig(image_on_canvas_l2, image = photo2)
        canvas_l1.itemconfig(image_on_canvas_l1, image = photo2)
        canvas_0.itemconfig(image_on_canvas_0, image = photo2)
        canvas_r1.itemconfig(image_on_canvas_r1, image = photo2)
        canvas_r2.itemconfig(image_on_canvas_r2, image = photo2)
        canvas_r3.itemconfig(image_on_canvas_r3, image = photo2)
        canvas_r4.itemconfig(image_on_canvas_r4, image = photo2)
        canvas_m.itemconfig(image_on_canvas_m, image = photo)
        group_name_textbox.configure(state = NORMAL)
        group_name_textbox.delete(0, END)
        group_name_textbox.insert(0, '')
        group_name_textbox.configure(state = DISABLED)
        image_number_textbox.configure(state = NORMAL)
        image_number_textbox.delete(0, END)
        image_number_textbox.insert(0, '0')
        image_number_textbox.configure(state = DISABLED)
        main_list = deque()
    else:
        return


def About():
    about_window = Toplevel(root)
    about_window.title("About")
    about_window.geometry("300x80")
    about_window.resizable(0,0)

    about_window.grab_set()
    
    about_label = Label(about_window, text = 'Ablation Spot Placer\n\n by Kosta Crnobrnja 2019.')
    about_label.pack()    

    licence_button = Button(about_window, text = 'Licence', command = Licence)
    licence_button.pack(side = LEFT)

    close_button = Button(about_window, text = 'Close', command = about_window.destroy)
    close_button.pack(side = RIGHT)

def Licence():
    licence_window = Toplevel(root)
    licence_window.title("Licence")
    licence_window.resizable(0,0)
 
    licence_window.grab_set()    

    with open('gpl-3.0.txt', 'r') as file:
        licence_string = file.read()
    licence_textbox = ScrolledText(licence_window)
    licence_textbox.pack()
    licence_textbox.insert(INSERT, licence_string)
    licence_textbox.configure(state = DISABLED)

# define the main window with it's attributes
root = Tk()
root.title("Ablation Spot Placer")
root.wm_attributes('-zoomed', 1)

# add menubar
menu = Menu(root)
root.config(menu=menu)

file_menu = Menu(menu)
menu.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='New Project', command = NewProject)

help_menu = Menu(menu)
menu.add_cascade(label='Help', menu=help_menu)
help_menu.add_command(label='About', command = About)

# create frame that holds upper part of the main window
upper_frame = Frame(root)
upper_frame.pack(side = TOP, anchor = NW)

# upper_frame has a frame for holding the 'CREATE PDF' button in the upper left corner
createpdf_button_frame = Frame(upper_frame)
createpdf_button_frame.pack(side = LEFT)

def createPdf():
    global main_list
    if main_list:
        filename = askstring('Create PDF', 'Enter filename')
        if filename is not None and filename.strip() and '/' not in filename and '\\' not in filename and ':' not in filename and '*' not in filename and '?' not in filename and '"' not in filename and '<' not in filename and '>' not in filename and '|' not in filename:
            directory = askdirectory()
            if directory is not "":

                ### define variables that will be used for x,y placement on the pdf 
                column1_x = 2.2*cm 
                next_column_x = 5.8*cm

                tallest_y = 28.5*cm
                stringline_height = 0.5*cm

                image_width = 4.9*cm
                image_height = 3.675*cm
                label_image_dist = 0.2*cm

                temp_y = tallest_y + label_image_dist + image_height + 2*stringline_height

                ### start creating the pdf
                filename = filename + ".pdf"
                pdf_canvas = canvas.Canvas(filename)

                ### rotate the main_list deque so the first group is indexed at 0
                while main_list[0][0] is not 1:
                    main_list.rotate(-1)

                ### name for the temporary file in the working directory 
                temp_jpg = "temp_file.jpg"

                ### begin the object placement on the pdf canvas
                for group in main_list:
                    print(str(group[1]) + " " + str(temp_y/cm))
                    if temp_y >= 0.5*cm + 2*image_height + 2*label_image_dist + 4*stringline_height: # checks if there is room for: gap, label, number, image and margin 
                        temp_x = column1_x 
                        temp_y = temp_y - label_image_dist - image_height - 2*stringline_height
                        pdf_canvas.drawString(temp_x, temp_y, group[1])
                        temp_y = temp_y - stringline_height
                        ### rotate the main_image_list deque so the first image is indexed at 0 
                        while group[2][0][0] is not 1:
                            group[2].rotate(-1)
                        ### counter which counts if there are 3 images in a row 
                        counter = 0 
                    else:
                        pdf_canvas.showPage()
                        temp_x = column1_x
                        temp_y = tallest_y
                        pdf_canvas.drawString(temp_x, temp_y, group[1])
                        temp_y = temp_y - stringline_height
                        ### rotate the main_image_list deque so the first image is indexed at 0 
                        while group[2][0][0] is not 1:
                            group[2].rotate(-1)
                        ### counter which counts if there are 3 images in a row 
                        counter = 0 
                    for image in group[2]:
                        if temp_y >= 0.5*cm + image_height + label_image_dist + stringline_height: # checks if there is room for: gap, number, image and margin 
                            pdf_canvas.drawString(temp_x, temp_y, str(image[0]))

                            temp_y = temp_y - label_image_dist - image_height

                            temp_cv_image = image[1][-1]
                            temp_cv_image = cv2.resize(temp_cv_image, (540, 420))
                            cv2.imwrite(temp_jpg, temp_cv_image)
                            pdf_canvas.drawInlineImage(image = temp_jpg, x = temp_x, y = temp_y, width = image_width, height = image_height)

                            temp_y = temp_y + image_height + label_image_dist
                            temp_x = temp_x + next_column_x
                            counter = counter + 1 

                            if counter % 3 == 0 and image is not group[2][-1]:
                                temp_x = column1_x
                                temp_y = temp_y - label_image_dist - image_height - stringline_height 
                        else:
                            pdf_canvas.showPage()
                            temp_x = column1_x
                            temp_y = tallest_y

                            pdf_canvas.drawString(temp_x, temp_y, group[1])

                            temp_y = temp_y - stringline_height

                            counter = 0

                            pdf_canvas.drawString(temp_x, temp_y, str(image[0]))

                            temp_y = temp_y - label_image_dist - image_height

                            temp_cv_image = image[1][-1]
                            temp_cv_image = cv2.resize(temp_cv_image, (540, 420))
                            cv2.imwrite(temp_jpg, temp_cv_image)
                            pdf_canvas.drawInlineImage(image = temp_jpg, x = temp_x, y = temp_y, width = image_width, height = image_height)

                            temp_y = temp_y + label_image_dist + image_height
                            temp_x = temp_x + next_column_x
                            counter = counter + 1 

                os.remove(temp_jpg)
                pdf_canvas.showPage() # stops editing the page and moves onto the next page
                pdf_canvas.save() # saves the file

                ### move the file from the working directory to the desired location 
                shutil.move(filename, directory)

                ### start changing the cosmetics 
                updateGroupNameTextbox()
                updateImageNumberTextbox()
                updateSlideshow()
                updateMainCanvas()
    
        elif filename is not None:
            showerror('Invalid Filename', 'Must contain at least one character other than space(s) excluding / \ : * ? " < >')
    

# create the 'CREATE PDF' button
createpdf_button = Button(createpdf_button_frame, text = 'Create\nPDF', bg = 'red', activebackground = 'orange', command = createPdf)   
createpdf_button.pack(side = LEFT)

# upper_frame has a subframe containing two subsubframes - one for labels and one for a slideshow 
upper_subframe = Frame(upper_frame, width = 1280)
upper_subframe.pack(side = RIGHT)

# subsubframe for holding a  slideshow of images in a group 
slideshow_frame = Frame(upper_subframe, width = 1280)
slideshow_frame.pack(side = TOP)

# create the canvases for the slideshow and pack them in slideshow_frame
cv_img2 = cv2.imread("default_sml.png")
photo2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv_img2))

#

canvas_l4 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_l4.pack(side = LEFT, padx = (0,10))
image_on_canvas_l4 = canvas_l4.create_image(0, 0, image = photo2, anchor = NW)

canvas_l3 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_l3.pack(side = LEFT, padx = 10)
image_on_canvas_l3 = canvas_l3.create_image(0, 0, image = photo2, anchor = NW)

canvas_l2 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_l2.pack(side = LEFT, padx = 10)
image_on_canvas_l2 = canvas_l2.create_image(0, 0, image = photo2, anchor = NW)

canvas_l1 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_l1.pack(side = LEFT, padx = 10)
image_on_canvas_l1 = canvas_l1.create_image(0, 0, image = photo2, anchor = NW)

#

canvas_0 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_0.pack(side = LEFT, padx = 30)
image_on_canvas_0 = canvas_0.create_image(0, 0, image = photo2, anchor = NW)

#

canvas_r1 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_r1.pack(side = LEFT, padx = 10)
image_on_canvas_r1 = canvas_r1.create_image(0, 0, image = photo2, anchor = NW)

canvas_r2 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_r2.pack(side = LEFT, padx = 10)
image_on_canvas_r2 = canvas_r2.create_image(0, 0, image = photo2, anchor = NW)

canvas_r3 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_r3.pack(side = LEFT, padx = 10)
image_on_canvas_r3 = canvas_r3.create_image(0, 0, image = photo2, anchor = NW)

canvas_r4 = Canvas(slideshow_frame, width = 120, height = 90)
canvas_r4.pack(side = LEFT, padx = (10,0))
image_on_canvas_r4 = canvas_r4.create_image(0, 0, image = photo2, anchor = NW)

#

# subsubframe for holding labels and buttons above the main_image_frame for navigating the images and groups 
navigation_frame = Frame(upper_subframe, width = 1280)
navigation_frame.pack(side = BOTTOM, anchor = W)

# define function that when given the appropriate image calculates the radius of a circle in pixels that represents 30 micrometers irl
def calculateRadius(image):
    # convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # crop two parts of the image - the numerical and graphical parts of the scalebar 
    gray_num = gray[884:916, 862:968]
    gray_gra = gray[894:895, 1006:1279]
    
    # median blur the numerical to remove noise
    gray_num = cv2.medianBlur(gray_num, 3)
    
    # apply OCR to the numerical
    num_scale_str = pytesseract.image_to_string(gray_num)
    
    # truncate everything except the numbers in the numerical scale string and convert the string into integer
    num_scale_str = re.sub('[^0123456789]', '', num_scale_str)
    num_scale_int = int(num_scale_str)
    
    # invert the color values of the graphical and then count the black pixels i.e. the length of line 

    gray_gra = cv2.bitwise_not(gray_gra)
    
    length=0
    end_of_line = 0
    
    while end_of_line == 0:
        gray_gra_pixel = gray_gra[0:1, length:(length+1)]
        if cv2.countNonZero(gray_gra_pixel) == 0:
            length = length + 1
        else:
            end_of_line = 1

    radius = int((15 * length) / num_scale_int)
    return radius

# define the function that updates the group_name_textbox
def updateGroupNameTextbox():
    group_name_textbox.configure(state = NORMAL)
    group_name_textbox.delete(0, END)
    group_name_textbox.insert(0, main_list[0][1])
    group_name_textbox.configure(state = DISABLED)

# define the function that updates the image_number_textbox
def updateImageNumberTextbox():
    global main_list
    main_image_list = main_list[0][2][0]
    image_number_textbox.configure(state = NORMAL)
    image_number_textbox.delete(0, END)
    image_number_textbox.insert(0, main_image_list[0])
    image_number_textbox.configure(state = DISABLED)

# define function that updates the slideshow
def updateSlideshow():
    global main_list
    global temphoto_l4 
    global temphoto_l3 
    global temphoto_l2 
    global temphoto_l1
    global temphoto_r1 
    global temphoto_r2 
    global temphoto_r3 
    global temphoto_r4
    global temphoto_0

    main_list[0][2].rotate(4)
    temphoto_l4 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_l4.itemconfig(image_on_canvas_l4, image = temphoto_l4)

    main_list[0][2].rotate(-1)
    temphoto_l3 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_l3.itemconfig(image_on_canvas_l3, image = temphoto_l3)

    main_list[0][2].rotate(-1)
    temphoto_l2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_l2.itemconfig(image_on_canvas_l2, image = temphoto_l2)

    main_list[0][2].rotate(-1)
    temphoto_l1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_l1.itemconfig(image_on_canvas_l1, image = temphoto_l1)

    main_list[0][2].rotate(-2)
    temphoto_r1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_r1.itemconfig(image_on_canvas_r1, image = temphoto_r1)

    main_list[0][2].rotate(-1)
    temphoto_r2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_r2.itemconfig(image_on_canvas_r2, image = temphoto_r2)

    main_list[0][2].rotate(-1)
    temphoto_r3 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_r3.itemconfig(image_on_canvas_r3, image = temphoto_r3)

    main_list[0][2].rotate(-1)
    temphoto_r4 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_r4.itemconfig(image_on_canvas_r4, image = temphoto_r4)

    main_list[0][2].rotate(4)
    temphoto_0 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
    canvas_0.itemconfig(image_on_canvas_0, image = temphoto_0)

# define function that updates the main canvas
def updateMainCanvas():
    global main_list
    global temphoto_m
    temphoto_m = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][1][-1]))
    canvas_m.itemconfig(image_on_canvas_m, image = temphoto_m)


# create buttons and labels for navigating the images and groups

# define function to choose a folder from which to load images (i.e. one sample)

group_number = 0
group_name = 'default group name'

def loadImages(path): # for a given directory (path) returns a list of [ [image_number, image_iteration_list, thumbnail image], ...] 
    imagesList = listdir(path)
    loadedImages = []
    i = 1
    if platform == 'linux' or platform == 'linux2' or platform == 'darwin': # checks which OS is running so that the path is correct / or \ 
        for image in sorted(imagesList): # sorts files alphanumerically
            if "CLI.tif" in image: # takes only the "CLI" tif files
                base_image = cv2.imread(path + "/" + image)
                thumbnail_image = cv2.resize(base_image, (120, 90)) 
                radius = calculateRadius(base_image)
                img_with_number = [i, [base_image], thumbnail_image, radius] # the [base_image] is the image_iteration_list 
                i = i + 1
                loadedImages.append(img_with_number)
    elif platform == 'win32': # same as ^
        for image in sorted(imagesList):
            if "CLI.tif" in image:
                base_image = cv2.imread(path + "\\" + image)
                thumbnail_image = cv2.resize(base_image, (120, 90))
                radius = calculateRadius(base_image)
                img_with_number = [i, [base_image], thumbnail_image, radius] 
                i = i + 1
                loadedImages.append(img_with_number)
    return loadedImages

def load_folder():
    global main_list
    global group_number
    global group_name
    global group_name_textbox
     
    directory = askdirectory()
    if directory is not "":
        if any("CLI.tif" in image for image in listdir(directory)):
            group_name = askstring('Load group', 'Name of sample group')
            # If the user clicks cancel, None is returned
            # .strip is used to ensure the user doesn't
            # enter only spaces ' '
            if group_name is not None and group_name.strip():
                if main_list:
                    while main_list[0][0] is not 1:
                        main_list.rotate(-1)
                group_number = group_number + 1
                main_list.append([group_number, group_name, deque(loadImages(directory))]) 
                main_list.rotate(1)
    
                ### START CHANGING THE COSMETICS ###
    
                # make the group_name_textbox show the now loaded group's name
                updateGroupNameTextbox()
    
                # make the image_number_textbox show "1" indicating the first image in the group
                updateImageNumberTextbox()
    
                # in slideshow display thumbnails from main_image_list 
                updateSlideshow()
    
                # display image on main canvas
                updateMainCanvas()
    
            elif group_name is not None:
                showerror('Invalid String', 'You must enter something!')
        else:
            showerror('Invalid Directory', "The directory doesn't contain the expected files!")

def load_folder_event(argument):
    load_folder()

def change_group_name():
    global main_list
    global group_name
    if main_list:
        group_name = askstring('Edit group name', 'Name of sample group')
        if group_name is not None and group_name.strip():
            main_list[0][1] = group_name
            updateGroupNameTextbox()
        elif group_name is not None:
            showerror('Invalid String', 'You must enter something!')

def change_group_name_event(argument):
    change_group_name()

def group_go_l():
    global main_list
    if main_list:
        main_list.rotate(1)
        updateGroupNameTextbox()
        updateImageNumberTextbox()
        updateSlideshow()
        updateMainCanvas()

def group_go_l_event(argument):
    group_go_l()

def group_go_r():
    global main_list
    if main_list:
        main_list.rotate(-1)
        updateGroupNameTextbox()
        updateImageNumberTextbox()
        updateSlideshow()
        updateMainCanvas()

def group_go_r_event(argument):
    group_go_r()

load_button = Button(navigation_frame, text = 'Load group', command = load_folder)  
load_button.pack(side = LEFT, padx = (0,30))
root.bind('<l>', load_folder_event)

edit_button = Button(navigation_frame, text = 'Edit group name', command = change_group_name)
edit_button.pack(side = LEFT, padx = (0,30))
root.bind('<e>', change_group_name_event)

left_group_button = Button(navigation_frame, text = '<', command = group_go_l)  
left_group_button.pack(side = LEFT)
root.bind('<Control-Left>', group_go_l_event)

group_name_textbox = Entry(navigation_frame, state = DISABLED, width = 10)
group_name_textbox.pack(side = LEFT)

right_group_button = Button(navigation_frame, text = '>', command = group_go_l)
right_group_button.pack(side = LEFT, padx = (0,142))
root.bind('<Control-Right>', group_go_r_event)

# define what the  < and > buttons next to the image number do
def image_go_l():
    global main_list
    if main_list:
        main_image_list = main_list[0][2]
        main_image_list.rotate(1)
        updateImageNumberTextbox()
        updateSlideshow()
        updateMainCanvas()

def image_go_l_event(argument):
    image_go_l()

def image_go_r():
    global main_list
    if main_list:
        main_image_list = main_list[0][2]
        main_image_list.rotate(-1)
        updateImageNumberTextbox()
        updateSlideshow()
        updateMainCanvas()

def image_go_r_event(argument):
    image_go_r()

left_image_button = Button(navigation_frame, text = '<', command = image_go_l)  
left_image_button.pack(side = LEFT)
root.bind('<Left>', image_go_l_event)

image_number = '0' 

image_number_textbox = Entry(navigation_frame, state = DISABLED, width = 4, justify = CENTER)
image_number_textbox.pack(side = LEFT)
image_number_textbox.configure(state = NORMAL)
image_number_textbox.delete(0, END)
image_number_textbox.insert(0, image_number)
image_number_textbox.configure(state = DISABLED)

right_image_button = Button(navigation_frame, text = '>', command = image_go_r)  
right_image_button.pack(side = LEFT)
root.bind('<Right>', image_go_r_event)

# create frame that holds the lower part of the main window 

lower_frame = Frame(root)
lower_frame.pack(side = RIGHT)

# lower_frame has a frame for holding the circle settings
circle_settings_frame = Frame(lower_frame)
circle_settings_frame.pack(side = LEFT, anchor = N)

# define functions for the circle settings

def undo():
    global main_list
    if main_list:
        main_image_list = main_list[0][2]
        image_iteration_list = main_image_list[0][1]
        if image_iteration_list[-1] is not image_iteration_list[0]:
            del main_list[0][2][0][1][-1] #delete the last element in the image_iteration_list... ^if the last one isn't the base_image
            temp_cv_image = copy.deepcopy(image_iteration_list[-1])
            main_list[0][2][0][2] = cv2.resize(temp_cv_image, (120, 90)) 
            updateMainCanvas()
            updateSlideshow()

def undo_event(argument):
    undo()

def reset():
    global main_list
    if main_list:
        main_image_list = main_list[0][2]
        image_iteration_list = main_image_list[0][1]
        if image_iteration_list[-1] is not image_iteration_list[0]:
            main_list[0][2][0][1] = [image_iteration_list[0]] #set the image_iteration_list back to only one element - the base_image
            temp_cv_image = copy.deepcopy(main_list[0][2][0][1][-1])
            main_list[0][2][0][2] = cv2.resize(temp_cv_image, (120, 90))
            updateMainCanvas()
            updateSlideshow()

def reset_event(argument):
    reset()

def change_color():
    global circle_color
    if circle_color == 1:
        color_button.configure(text = 'Black', bg = 'black', fg = 'white', activebackground = 'white', activeforeground = 'black')
        circle_color = 0
    elif circle_color == 0:
        color_button.configure(text = 'White', bg = 'white', fg = 'black', activebackground = 'black', activeforeground = 'white') 
        circle_color = 1

def change_color_event(argument):
    change_color()




# create buttons for the circle settings

cirset_label1 = Label(circle_settings_frame, text = 'Circle\nplacement', justify = LEFT)
cirset_label1.pack(pady = 5)

undo_button = Button(circle_settings_frame, text = 'Undo', width = 4, command = undo)
undo_button.pack()
root.bind('<u>', undo_event)

reset_button = Button(circle_settings_frame, text = 'Reset', width = 4, command = reset)  
reset_button.pack()
root.bind('<r>', reset_event)

circle_color = 1

color_button = Button(circle_settings_frame, text = 'White', bg = 'white', fg = 'black', activebackground = 'black', activeforeground = 'white', command = change_color, width = 4)  
color_button.pack()
root.bind('<c>', change_color_event)






# lower_frame has a subframe for holding the main image that is being edited 
main_image_frame = Frame(lower_frame, width = 1280, height = 960, relief = "sunken")
main_image_frame.pack(side = RIGHT)

scrollbar = Scrollbar(main_image_frame)
scrollbar.pack( side = RIGHT, fill = Y )

# Load an image using OpenCV
cv_img = cv2.imread("default_lrg.png")

# Use PIL (Pillow) to convert the NumPy ndarray to a PhotoImage
photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv_img))

# Create the main canvas
canvas_m = Canvas(main_image_frame, width = 1280, height = 960, yscrollcommand = scrollbar.set)
canvas_m.pack()

scrollbar.config( command = canvas_m.yview )

# Add a PhotoImage to the Canvas
image_on_canvas_m = canvas_m.create_image(0, 0, image=photo, anchor=NW)
canvas_m.configure(scrollregion = canvas_m.bbox("all"))

def MouseWheelHandler(event):
    global count

    def delta(event):
        if event.num == 5 or event.delta < 0:
            return 1 
        return -1 

    canvas_m.yview_scroll(delta(event), "units")

canvas_m.bind("<MouseWheel>",MouseWheelHandler)
canvas_m.bind("<Button-4>",MouseWheelHandler)
canvas_m.bind("<Button-5>",MouseWheelHandler)




### making the circles

event2canvas = lambda e, c: ( int(c.canvasx(e.x)), int(c.canvasy(e.y)) )

#function to be called when mouse is clicked
def printcoords(event):
    global main_list
    global temphoto_m
    global temphoto_0
    global circle_color
    if main_list:
        image_iteration_list = main_list[0][2][0][1]
        circle_radius = main_list[0][2][0][3]
        circle_thickness = int(round(circle_radius/10))
        cx, cy = event2canvas(event, canvas_m)
        temp_cv_image = copy.deepcopy(image_iteration_list[-1])
        if circle_color == 1:
            temp_cv_image = cv2.circle(temp_cv_image, (cx,cy), circle_radius, (255, 255, 255), circle_thickness)
            image_iteration_list.append(temp_cv_image)
            main_list[0][2][0][2] = cv2.resize(temp_cv_image, (120, 90)) 
        elif circle_color == 0:
            temp_cv_image = cv2.circle(temp_cv_image, (cx,cy), circle_radius, (0, 0, 0), circle_thickness)
            image_iteration_list.append(temp_cv_image)
            main_list[0][2][0][2] = cv2.resize(temp_cv_image, (120, 90)) 
        #### update the image on the main canvas
        temphoto_m = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(image_iteration_list[-1]))
        canvas_m.itemconfig(image_on_canvas_m, image = temphoto_m)
        #### update the thumbnail on the slideshow
        temphoto_0 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(main_list[0][2][0][2]))
        canvas_0.itemconfig(image_on_canvas_0, image = temphoto_0)
        #temp_cv_image = cv2.resize(image_iteration_list[-1], (560, 420))
        #cv2.imwrite('test.jpg', temp_cv_image)
#mouseclick event
canvas_m.bind("<ButtonPress-1>",printcoords)


root.mainloop()
