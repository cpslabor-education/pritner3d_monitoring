import cv2
import os
import time
import threading
import keyboard
from os import listdir
#######################################################################
#-----------------------Read it first:--------------------------------#
#######################################################################
#   The program has three threads, which runs parallel,               #
#   The first one is responsible for the termination of the other two #
#   The second is a timer, which commands the third one               #
#   The third one ensure the continuous webcam picture and takes the  #
#   photos when the second commands it.                               #
#   The fourht thread is an extension for the image classification    #    
#######################################################################

cam = cv2.VideoCapture(0)

# paths:
taken_img_path = r'D:\personal_stuff\08_msc\mechatro_msc\99_diploma_munka\07_captured_imgs'
img_path = r'D:\personal_stuff\08_msc\mechatro_msc\99_diploma_munka\08_from_colab\04_epoch_40_with_new_pics\img'
eval_path = r'D:\personal_stuff\08_msc\mechatro_msc\99_diploma_munka\08_from_colab\04_epoch_40_with_new_pics\evaluation'
tagged_img_path = r'D:\personal_stuff\08_msc\mechatro_msc\99_diploma_munka\09_category_labeled_images'

sample_rate = 5


def terminating():
    print("Terminating process is running")
    print("Press 'q' key to terminate the program.")
    global terminating_status
    terminating_status = False
    while True:
        if keyboard.read_key() == 'q':
            terminating_status = True
            print("Closing up loose threads")
            break


def counter():
    print("Timer started! ")
    my_timer = 0
    global command
    command = False

    while True:
        my_timer += 1
        #print(my_timer)
        if terminating_status is True:
            #Timer is terminating.
            break
        elif my_timer % sample_rate == 0 and my_timer > 0:
            command = True
            time.sleep(0.03)
            command = False
        else:
            command = False
        #print("The command status is: {}".format(command))
        time.sleep(1)
    return command


def camera():
    print("Camera started!")
    img_counter = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("3d printing supervision", frame)
        cv2.waitKey(1)
        if terminating_status is True:
            #camera is terminating.
            break
        elif command == True:
            #print("The command status in picture taker is: {}".format(command))
            img_name = "3Dp_supervision_{}.png".format(img_counter)
            # cv2.imwrite(img_name, frame)
            cv2.imwrite(os.path.join(taken_img_path, img_name), frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()
    cv2.destroyAllWindows()


def img_reader():
    prev_img_name = " "
    window_name = 'Image'
    img_list = [ ]

    while True:
        # Look for the jpg files in the folder
        if len(os.listdir(img_path)) < 2:
            continue
        elif terminating_status is True:
            break
        else:
            for img in os.listdir(img_path):
                # print(img_name)
                if (img.endswith(".jpg") or img.endswith("jpeg")):
                    img_list.append(img)

            img_name = img_list[-1]

            if prev_img_name == img_name:
                # print("Waiting for new image...")
                continue
            elif prev_img_name != img_name:
                # The paths with file names:
                eval_path_with_txt = eval_path + "\\" + img_name[:-4] + ".txt"
                img_path_with_img = img_path + "\\" + img_name

                # Open the txt file:
                with open(eval_path_with_txt, 'r') as file:
                    # read all content from a file using read()
                    statement = file.read()

                # Read txt file content
                if statement == "OK":
                    print("The printing is going on the expected way!")
                    img_label = "The printing is OK!"
                    image = cv2.imread(img_path_with_img)
                    # Using cv2.putText() method
                    image_labeled = cv2.putText(image, img_label, (20, 280), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0, 255, 0), 2)
                else:
                    print("Oh no...the filament is stuck!")
                    img_label = "The printing is NOK!"
                    image = cv2.imread(img_path_with_img)
                    # Using cv2.putText() method
                    image_labeled = cv2.putText(image, img_label, (20, 280), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0, 0, 255), 2)

                # Saving image
                filename = img_name + ".jpg"
                cv2.imwrite(os.path.join(tagged_img_path, filename), image_labeled)

                # Displaying the image
                cv2.imshow(window_name, image_labeled)
                cv2.waitKey(3000)

                prev_img_name = img_name

# calling threads
terminating_thread = threading.Thread(target=terminating)
terminating_thread.start()
countdown_thread = threading.Thread(target=counter)
countdown_thread.start()
camera_thread = threading.Thread(target=camera)
camera_thread.start()
img_reader_thread = threading.Thread(target=img_reader)
img_reader_thread.start()
