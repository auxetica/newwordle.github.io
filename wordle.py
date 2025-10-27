#!/usr/bin/python
print('Content-type: text/html\n')

f_answers = open('data/wordle_answers.txt')
wordle_answers = f_answers.read()
f_valid = open('data/valid_words.txt')
valid_words = f_valid.read()
f_template = open('data/wordle_template.html')
template_html = f_template.read()
f_default = open('data/default_template.html')
default_html = f_default.read()

import cgitb #
cgitb.enable() #These 2 lines will allow error messages to appear on a web page in the browser

import cgi
import random

#answer = wordle_answers.split()[100]
# aptly

wintext ='''
<p> You did it! It took you GUESS_QUANTITY attempts! </p>
<a href="http://homer.stuy.edu/~jruan70/final/wordle.py?ID=RANDOM_ID">Try again?</a>
'''

losetext='''
<p> Oh no! You've ran out of guesses. The correct answer was WORDLE_ANSWER. </p>
<a href="http://homer.stuy.edu/~jruan70/final/wordle.py?ID=RANDOM_ID">Try again?</a>
'''

formtext ='''
    <form action="wordle.py" method="GET">
     <input type="text" name="GUESS_INFO" value="" minlength="5" maxlength="5">
     <input type="submit">
    </form>
'''

split_layout = 'qwertyuiop,asdfghjkl,zxcvbnm'
whole_layout = 'qwertyuiopasdfghjklzxcvbnm'

data = cgi.FieldStorage()
# generates if there is no query string
def default_page():
    if len(data) == 0:
        print(default_html.replace('ID_NUMBER', str(random.randint(1000000000,9999999999))))
        # length of id is 10 digits
default_page()

        

def hub(html):
    # get queryname and queryval
    if len(data) > 0:
        queryname = str(list(data)[0])
        queryval = data[str(list(data)[0])].value
    else:
        return
    # runs if theres no guesses yet
    if 'ID' in data:
        id_number = int(queryval)
        return setup(html, id_number, [], '')
    else:
        id_number = int(queryname[:10])

    guess_rows = []
    guess_string = queryname[10::] + queryval
    # gets guesses
    while len(guess_string) > 0:
        if guess_string[0:5].lower() in valid_words:
            guess_rows.append(guess_string[0:5].upper())
        guess_string = guess_string[5::]
    guess_string = ''.join(guess_rows)

    return setup(html, id_number, guess_rows, guess_string)
    
    
# assembles all the html
def setup(html, id_number, guess_rows, guess_string):
    if len(guess_rows) == 6:
        html = lose(id_number, html, guess_rows)
    html = win(id_number, html, guess_rows)
    html = make_table(guess_rows, html, id_number)
    html = make_blank(6-len(guess_rows), html)
    html = html.replace('GUESS_INFO', str(id_number) + guess_string)
    html = make_keyboard(html, make_letter_colors(id_number, guess_rows))
    return html
        
# makes rows with filled guesses
def make_table(guess_rows, html, id_number):
    guess_HTML = ''
    i = 0
    if guess_rows == None or len(guess_rows) == 0:
        return html.replace('TABLE_HTML', '')
    for guess in guess_rows:
        guess_HTML += '<tr>\n'
        for letter in guess:
            guess_HTML += '    <td class=\"' + classify(id_number, guess.lower(), i) + '\">' + letter + '</td>\n'
            i+=1
        guess_HTML += '</tr>\n'
        i=0
    return(html.replace('TABLE_HTML', guess_HTML))

# makes empty rows
def make_blank(n, html):
    i = 0
    j = 0
    blank_HTML = ''
    while i < n:
        blank_HTML += '<tr>\n'
        while j < 5:
            blank_HTML +='    <td> </td>\n'
            j+=1
        blank_HTML += '</tr>\n'
        i += 1
        j = 0
    return(html.replace('BLANK_HTML', blank_HTML))

# creates a list for a 5-letter word that assigns each letter its color coding
def create_word_colors(answer, word):
    letter_quantities = {}
    colors = ['white'] * 5
    i = 0
    for letter in answer:
        if letter not in letter_quantities:
            letter_quantities[letter] = 1
        elif letter in letter_quantities:
            letter_quantities[letter] += 1
    for letter in word:
        if answer[i] == letter:
            colors[i] = 'green'
            letter_quantities[letter] -= 1
        i+=1
    i=0
    for letter in word:
        if answer[i] != letter:
            if letter not in answer:
                colors[i] = 'white'
            elif letter in answer:
                if letter_quantities[letter] > 0:
                    colors[i] = 'yellow'
                    letter_quantities[letter] -= 1
                else:
                    colors[i] = 'white'
                    letter_quantities[letter] = 0
        i+=1
    return colors

# returns one color coding based on a word and the index of the letter
def classify(id_number, word, index):
    answer = wordle_answers.split()[id_number % len(wordle_answers.split())]
    return create_word_colors(answer, word)[index]

# makes a dictionary where the keys are q, w, e ... n, m and the values are the correct colors for the keyboard
# important to make sure no yellow overrides a green, or a gray overrides a yellow, etc.
def make_letter_colors(id_number, guess_rows):
    answer = wordle_answers.split()[id_number % len(wordle_answers.split())]
    color_dict = {}
    for letter in whole_layout:
        color_dict[letter] = 'blank'
    for guess in guess_rows:
        for letter in guess:
            if create_word_colors(answer, guess.lower())[guess.index(letter)] == 'green':
                color_dict[letter.lower()] = 'green'
            elif create_word_colors(answer, guess.lower())[guess.index(letter)] == 'yellow':
                if color_dict[letter.lower()] != 'green':
                    color_dict[letter.lower()] = 'yellow'
            elif create_word_colors(answer, guess.lower())[guess.index(letter)] == 'white':
                if color_dict[letter.lower()] != 'green' and color_dict[letter.lower()] != 'yellow':
                    color_dict[letter.lower()] = 'white'
    return color_dict

# makes table code for keyboard
def make_keyboard(html, color_dict):
    keyboard_HTML = ''
    for row in split_layout.split(','):
        keyboard_HTML += '<tr>\n'
        for letter in row:
            keyboard_HTML += '    <td class=\"keyboard ' + color_dict[letter] + '\">' + letter.upper() + '</td>\n'
        keyboard_HTML += '</tr>\n'
    return(html.replace('KEYBOARD_HTML', keyboard_HTML))
        
# runs if you win!!
def win(id_number, html, guess_rows):
    answer = wordle_answers.split()[id_number % len(wordle_answers.split())]
    for guess in guess_rows:
        if guess.lower() == answer:
            html = html.replace('WIN_TEXT', wintext)
            html = html.replace('RANDOM_ID', str(random.randint(1000000000,9999999999)))
            html = html.replace('GUESS_QUANTITY', str(len(guess_rows)))
            html = html.replace('FORM_TEXT', '')
    html = html.replace('WIN_TEXT', '')
    html = html.replace('FORM_TEXT', formtext)
    return html

# aw man you lost!
def lose(id_number, html, guess_rows):
    answer = wordle_answers.split()[id_number % len(wordle_answers.split())]
    
    for guess in guess_rows:
        if guess.lower() not in valid_words or answer == guess.lower():
            return html
    html = html.replace('WIN_TEXT', losetext)
    html = html.replace('RANDOM_ID',  str(random.randint(1000000000,9999999999)))
    html = html.replace('WORDLE_ANSWER', answer.upper())
    html = html.replace('FORM_TEXT', '')
    return html


            
# testing purposes
def stringify(g):
    out = ''
    for i in g:
        out += str(i)
    return out

# testing purposes, i think? i dont even remember what i used this for.
def listify(s):
    g = []
    g.append(s)
    return g

# prints it all
print(hub(template_html))