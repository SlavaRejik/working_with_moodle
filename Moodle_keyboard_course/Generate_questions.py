#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as Xml
from xml.dom import minidom
import base64
import random
import math

root_dir = 'data'
keyboard_dir = '{0}/keyboard'.format(root_dir)
images_base64 = {}
drops_dic = {}
course_id = '001.2.8'


def CDATA(text):
    element = Xml.Element("CDATA")
    element.text = text
    return element


def serialize_xml_with_CDATA(write, elem, qnames, namespaces, short_empty_elements, **kwargs):
    if elem.tag == 'CDATA':
        write("<![CDATA[{}]]>".format(elem.text))
        return
    return Xml._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)


Xml._original_serialize_xml = Xml._serialize_xml
Xml._serialize_xml = Xml._serialize['xml'] = serialize_xml_with_CDATA


def populate_drops():
    my_drops_dic = {}
    # QWERTY
    for idx1, l in enumerate('QWERTYUIOP'):
        my_drops_dic[l] = [7 + idx1 * 70, 7]
    for idx2, l in enumerate('ASDFGHJKL'):
        my_drops_dic[l] = [41 + idx2 * 70, 76]
    for idx3, l in enumerate('ZXCVBNM'):
        my_drops_dic[l] = [77 + idx3 * 70, 147]

    # ЙЦУКЕН
    for idx4, l in enumerate('ЙЦУКЕНГШЩЗХЪ'):
        my_drops_dic[l] = [7 + idx4 * 70, 7]
    for idx5, l in enumerate('ФЫВАПРОЛДЖЭ'):
        my_drops_dic[l] = [41 + idx5 * 70, 76]
    for idx6, l in enumerate('ЯЧСМИТЬБЮ'):
        my_drops_dic[l] = [77 + idx6 * 70, 147]

    return my_drops_dic


def load_image(my_images, filename, name):
    file_data = open(filename, 'r', encoding="utf-8").read()
    my_images[name] = base64.b64encode(bytes(file_data, 'utf-8')).decode("utf-8")
    return my_images


def generate_question(images, q_name, q_text, drags, drops):
    question_xml = '''\n<question type="ddimageortext">
        <name><text>{0}</text></name>
        <questiontext format="html"><text></text></questiontext>
        <generalfeedback format="html"><text></text></generalfeedback>
        <defaultgrade>1.0000000</defaultgrade>
        <penalty>0.3333333</penalty>
        <hidden>0</hidden>
        <idnumber></idnumber>
        <correctfeedback format="html"><text>Ваш ответ верный.</text></correctfeedback>
        <partiallycorrectfeedback format="html"><text>Ваш ответ частично правильный.</text></partiallycorrectfeedback>
        <incorrectfeedback format="html"><text>Ваш ответ неправильный.</text></incorrectfeedback>
        <shownumcorrect/><file name="keyboard.svg" encoding="base64">{1}</file></question>''' \
        .format(q_name, images['keyboard.svg'])
    question = Xml.fromstring(question_xml)
    question[1][0].append(CDATA("{0}<br>".format(q_text)))

    # Drag
    drag_no = {}
    for idxd, d in enumerate(drags):
        drag = Xml.SubElement(question, 'drag')
        Xml.SubElement(drag, 'no').text = '{0}'.format(idxd + 1)
        drag_no[d] = idxd + 1
        Xml.SubElement(drag, 'text').text = '{0}'.format(d)
        Xml.SubElement(drag, 'draggroup').text = '1'
        q_file = Xml.SubElement(drag, 'file')
        lang = 'ru'
        if ord('A') <= ord(d) <= ord('Z'):
            lang = 'en'
        filename = 'key_{0}_{1}.svg'.format(lang, d)
        q_file.text = images[filename]
        q_file.set('name', filename)
        q_file.set('encoding', 'base64')

    # Drop
    for idx_d, idrop in enumerate(drops):
        drop = Xml.SubElement(question, 'drop')
        Xml.SubElement(drop, 'text').text = idrop
        Xml.SubElement(drop, 'no').text = '{0}'.format(idx_d + 1)
        Xml.SubElement(drop, 'choice').text = '{0}'.format(drag_no[idrop])
        Xml.SubElement(drop, 'xleft').text = '{0}'.format(drops_dic[idrop][0])
        Xml.SubElement(drop, 'ytop').text = '{0}'.format(drops_dic[idrop][1])

    return question


# Write pretty xml
def write_xml(input_xml, out_filename):
    pretty = minidom.parseString(Xml.tostring(input_xml)).toprettyxml(indent=' ' * 2)
    out = '\n'.join([my_line for my_line in pretty.split('\n') if my_line.strip()])
    with open(out_filename, 'w', encoding="utf-8") as f:
        f.write(out)


# Generate questions and write to file
def generate_questions(my_root, topic_num, test_num, my_drags, my_drops):
    # QWERTY intro

    question = Xml.SubElement(my_root, 'question')
    question.set('type', 'category')

    category = Xml.SubElement(question, 'category')
    Xml.SubElement(category, 'text').text = '$course$/top/Test_{0}_{1:02d}'.format(topic_num, test_num)

    info = Xml.SubElement(question, 'info')
    info.set('format', 'moodle_auto_format')
    Xml.SubElement(info, 'text').text = ''
    Xml.SubElement(question, 'idnumber')

    q_num = 1

    for word in my_drops:
        out_drops = list(word)
        out_drops.sort()

        out_drags = list(my_drags)
        if my_drags == "AS_DROPS":
            out_drags = list(word)
        out_drags.sort()

        my_root.append(generate_question(images_base64, '{0}.{1}.{2}.{3} {4}'.
                                         format(course_id, topic_num, test_num, q_num, word), '', out_drags, out_drops))
        q_num += 1
    return root


def generate_random_sequence(text, min_size, max_size, count):
    ret = {}
    if max_size == 0:
        max_size = len(text)
    while len(ret) < count:
        c = random.randint(min_size, max_size)
        sub_ret = {}
        while len(sub_ret) < c:
            sub_ret[random.choice(text)] = 1
        ret[''.join(sorted(sub_ret.keys()))] = 1
    ret_list = list(ret.keys())
    random.shuffle(ret_list)
    return ret_list


def first_step(my_line):
    out_list = []
    x = 3
    y = 6
    out_line = ''
    while x > -1 or y < len(my_line):
        if x > -1:
            out_line = '{0}{1}'.format(my_line[x], out_line)
            x -= 1
        if y < len(my_line):
            out_line = '{0}{1}'.format(out_line, my_line[y])
            y += 1
        out_list.append(out_line)
    out_list.append('{0}{1}'.format(my_line[0:5], my_line[6:len(my_line)]))
    out_list.append(my_line)
    return out_list


# Load keyboard image
images_base64 = load_image(images_base64, '{0}/keyboard.svg'.format(keyboard_dir), 'keyboard.svg')

# Load EN key images
all_en_drags = []
for k in range(ord('A'), ord('Z') + 1):
    all_en_drags.append(chr(k))
    images_base64 = load_image(images_base64, '{0}/en/key_en_{1}.svg'.format(keyboard_dir, chr(k)),
                               'key_en_{0}.svg'.format(chr(k)))

# Load RU key images
all_ru_drags = []
for k in range(ord('А'), ord('Я') + 1):
    all_ru_drags.append(chr(k))
    images_base64 = load_image(images_base64, '{0}/ru/key_ru_{1}.svg'.format(keyboard_dir, chr(k)),
                               'key_ru_{0}.svg'.format(chr(k)))

# ## START
drops_dic = populate_drops()

for line_idx, line in enumerate(['ASDFGHJKL', 'QWERTYUIOP', 'ZXCVBNM', 'EN_FULL',
                                 'ФЫВАПРОЛДЖЭ', 'ЙЦУКЕНГШЩЗХЪ', 'ЯЧСМИТЬБЮ', 'RU_FULL']):

    if line == 'EN_FULL':
        tests = []
        for i in range(1, 11):
            tests.append([all_en_drags, generate_random_sequence(all_en_drags, 3, 10, 10)])

    elif line == 'RU_FULL':
        tests = []
        for i in range(1, 11):
            tests.append([all_ru_drags, generate_random_sequence(all_ru_drags, 3, 10, 10)])
    else:
        tests = [['AS_DROPS', first_step(line)]]
        my_min = 3
        my_max = len(line)

        for i in range(1, 10):
            my_max = 1 + math.ceil((10 - i) * (len(line) - 2) / 9)
            my_min = my_max - 1

            tests.append([line, generate_random_sequence(line, my_min, my_max, 10)])

    root = Xml.Element("quiz")

    for idx, test in enumerate(tests):
        root = generate_questions(root, line_idx + 1, idx + 1, test[0], test[1])
    write_xml(root, '{0}/{1}.{2}.xml'.format(root_dir, course_id, line_idx + 1))
