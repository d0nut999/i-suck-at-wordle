import pyscreenshot
import time
import easyocr
import cv2
import keyboard
import requests
import numpy as np
from random import randint


reader = easyocr.Reader(['en'], gpu=True)

url = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"


step=75
wrong_place = ''
corr_place = '.....'
miss_place = '.....'

#real wordle(785, 1135, 190, 260)
begin_x = 755 
finish_x = 1150
begin_y = 180
finish_y = 250

#Colors (R, G, B) Correct(83,141, 78), Wrong Place(181, 159, 59), Wrong(58, 58, 60) Real wordle

#Colors (R, G, B) Correct(121,184, 81), Wrong Place(243, 194, 55), Wrong(61, 64, 84) infinit wordle

#Game over color (R, G, B) (38,40,58)

def letter_squeezer(path):
    #Load the image
    img = cv2.imread(path, 0)

    #Find the letters (contours)
    contours, _ = cv2.findContours(255 - img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Get bounding boxes and sort them left to right
    bboxes = [cv2.boundingRect(c) for c in contours]
    bboxes = sorted(bboxes, key=lambda x: x[0])

    #Calculate required width dynamically
    gap = 10  # Space between letters
    total_width = sum(w for (_, _, w, _) in bboxes) + (gap * len(bboxes)) + 20
    max_height = max(h for (_, _, _, h) in bboxes) + 20

    #Create a canvas that is guaranteed to be big enough
    new_canvas = np.full((max_height, int(total_width)), 255, dtype=np.uint8)

    curr_x = 10  # Starting margin
    for x, y, w, h in bboxes:
        letter_crop = img[y:y+h, x:x+w]
        
        # We use the letter's own height/width to define the target area
        # broadcast mismatch
        new_canvas[10:10+h, curr_x:curr_x+w] = letter_crop
        curr_x += w + gap

    #Resize it 2x bigger so EasyOCR doesnt ignore it
    final_img = cv2.resize(new_canvas, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('fixed_squeezed.png', final_img)


def check_if_word_exists(begin_x, begin_y, finish_x, finish_y):
    print("Checking if word exists...")
    image = pyscreenshot.grab(bbox=(begin_x, begin_y, finish_x, finish_y))
    image.save("exist_check.png")
    img = cv2.imread('exist_check.png')
    (r, g, b) = img[60, 60][::-1]
    print(f'[Word Check] Pixel at (60, 60) - Red: {r}, Green: {g}, Blue: {b}, Analyzing...')
    if (r,g,b) == (25,26,36):
        print("Word doesn't exist, trying another one...")
        return False
    else:
        print("Word exists, proceeding...")
        return True



def did_we_win(begin_x, begin_y, finish_x, finish_y):
    image = pyscreenshot.grab(bbox=(begin_x, begin_y, finish_x, finish_y))
    image.save("exist_check.png")
    img = cv2.imread('exist_check.png')
    for x in range(5):
        (r, g, b) = img[60, 60][::-1]

        if (r, g, b) == (38,40,58):
            return True
        else:
            return False




def capture_and_save_screenshot(step, wrong_place, corr_place, miss_place,begin_x, begin_y, finish_x, finish_y):
    
    image = pyscreenshot.grab(bbox=(begin_x, begin_y, finish_x, finish_y))
    print("screenshot captured, begin_x: " + str(begin_x) + " begin_y: " + str(begin_y) + " finish_x: " + str(finish_x) + " finish_y: " + str(finish_y))
    #image.show()
    image.save("wordle_matrix.png")
    img = cv2.imread('wordle_matrix.png')

    #Processing letter placement colors
    miss_letters = []
    wrong_letters = []
    corr_letters =[]

    #6
    col_step = 60
    for x in range(5):
        (r, g, b) = img[60, col_step][::-1]
        print(f'Pixel at (60, {col_step}) - Red: {r}, Green: {g}, Blue: {b}')

        #Correct letter
        if (r, g, b) == (121,184,81):
            corr_letters.append(x)
        #Miss placed letter
        elif (r, g, b) == (243, 194, 55):
            miss_letters.append(x)
        #wrong letter
        else:
            wrong_letters.append(x)
        #74
        col_step += 70

            

    #Making the picture gray scale and saving it
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('step1_gray.png', gray)

    #taking only the white pixels (letters) and making the rest black (200,255)
    _, white_only = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    cv2.imwrite('step2_white_only.png', white_only)

    #inverting colors
    processed_img = cv2.bitwise_not(white_only)
    cv2.imwrite('step3_inverted.png', processed_img)

    #upscaling the image (3x bigger) to make the letter less pixelated
    upscaled_img = cv2.resize(processed_img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite('step4_sharpened.png', upscaled_img)

    #Last filtering to make it pure black/white
    _, sharp_img = cv2.threshold(upscaled_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('upscaled.png', sharp_img)

    letter_squeezer('upscaled.png')

    word=""
    for (bbox, text, prob) in reader.readtext("fixed_squeezed.png"):
        word_raw = text.strip()
        #Some letters are misread by easyocr, so we need to fix them
        for char in word_raw:
            if char.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                word += char.upper()
            elif char == "|":
                word += "I"
            elif char == "5":
                word += "S"
            elif char == "0":
                word += "O"
    print(f'Extracted word: {word}')
    print(wrong_letters)

    #Collect the wrong & right letters 
    for l in range(len(word)):
        if l in wrong_letters and word[l] not in wrong_place:
            wrong_place = wrong_place + word[l]
        elif l in corr_letters and word[l] not in corr_place:
            corr_place = corr_place[:l]+word[l]+corr_place[l+1:]
        elif l in miss_letters and word[l] not in miss_place:
            miss_place = miss_place[:l]+word[l]+miss_place[l+1:]
    return wrong_place, corr_place, miss_place
        
    
    #corr_res ="Correct letters are number: " + corr_letters
    #miss_res = "Miss placed letters are number: " + miss_letters
    #print(corr_res)
    #print(miss_res)

    #time.sleep(0.5)
    #result = reader.readtext("wordle_matrix.png", detail=0)
    #print(result)
    
def is_valid_yellow(word, miss_place):
    for i, char in enumerate(miss_place):
        if char == '.':
            continue
        
        # 1. The letter MUST be in the word
        if char not in word:
            return False
            
        # 2. The letter MUST NOT be in this specific spot
        if word[i] == char:
            return False
            
        # 3. Handle Duplicate Letters (Advanced)
        # If miss_place is '..a.a', the word must have at least 2 'a's
        if word.count(char) < miss_place.count(char):
            return False
            
    return True


def handle_response(response, wrong_place, corr_place, miss_place):
    if response.status_code == 200:
        words = response.text.splitlines()
        #filtered_words = [word for word in words if not any(char in word for char in wrong_place)]
        #print(filtered_words[:10])

        #avoid deleting words that have a green/yellow version of a grey letter:
        safe_letters = set(corr_place + miss_place) - {'.'}
        true_greys = [char for char in wrong_place if char not in safe_letters]
        filtered_words = [word for word in words if not any(char in word for char in true_greys)]

        for i in range(len(corr_place)):
            if corr_place[i] != '.':
                filtered_words = [word for word in filtered_words if word[i] == corr_place[i]]
        #for i in range(len(miss_place)):
        #    if miss_place[i] != '.':
        #        filtered_words = [word for word in filtered_words if miss_place[i] in word and word[i] != miss_place[i]]
        filtered_words = [word for word in filtered_words if is_valid_yellow(word, miss_place)]
        print(filtered_words[:10])
        return filtered_words[:10]


    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")


if __name__ == "__main__":
    response = requests.get(url)
    time.sleep(1)
    if response.status_code == 200:
        words = response.text.splitlines()
        keyboard.write(words[randint(0, len(words)-1)])
        keyboard.press_and_release('enter')
        time.sleep(5)
        while check_if_word_exists(begin_x, begin_y, finish_x, finish_y) == False:
            for i in range(5):
                keyboard.press_and_release('backspace')
                time.sleep(0.5)
            keyboard.write(words[randint(0, len(words)-1)])
            keyboard.press_and_release('enter')
            time.sleep(5)
        #time.sleep(5)
        print("First word accepted, starting the game...")
        for i in range(5):
            wrong_place,corr_place,miss_place = capture_and_save_screenshot(step, wrong_place,corr_place, miss_place, begin_x, begin_y, finish_x, finish_y)
            print(f"Collected wordle data, processing... try number {i+1}")
            time.sleep(2)
            response = requests.get(url)
            time.sleep(2)
            print(wrong_place)
            print(corr_place)
            print(miss_place)
            choices = handle_response(response, wrong_place.lower(),corr_place.lower(), miss_place.lower())
            time.sleep(1)
            if choices:
                if(len(choices) == 1):
                    keyboard.write(choices[0])
                    keyboard.press_and_release('enter')
                    print(f"Game won, the word is {choices[0]}!")
                    exit()
                num=0
                #list for used random words
                used=[]
                num_rand = randint(0, len(choices)-1)
                #to avoid using the same random word twice
                used.append(num_rand)
                keyboard.write(choices[num_rand])

                keyboard.press_and_release('enter')
                time.sleep(5)
                
                while check_if_word_exists(begin_x, begin_y + step, finish_x, finish_y +step) == False and num < len(choices)-1:
                    num+=1
                    for i in range(5):
                        keyboard.press_and_release('backspace')
                        time.sleep(0.5)
                    num_rand = randint(0, len(choices)-1)
                    #to avoid using the same random word twice
                    while num_rand in used:
                        num_rand = randint(0, len(choices)-1)

                    keyboard.write(choices[num_rand])
                    keyboard.press_and_release('enter')

                    used.append(num_rand)
                    time.sleep(5)
                
                if num == len(choices)-1 and check_if_word_exists(begin_x, begin_y, finish_x, finish_y) == False:
                    print("Couldn't find a valid word, trying a random one...")
                    for i in range(5):
                        keyboard.press_and_release('backspace')
                        time.sleep(0.5)
                    keyboard.write(words[randint(0, len(words)-1)])
                    keyboard.press_and_release('enter')
                    time.sleep(5)
                begin_y += step
                finish_y += step

            else:
                print("Choices are empty here!")
            #real wordle step is 70
            #step += 80
        print("Game Over")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

