# coding: utf8
from dataclasses import dataclass
from xml.etree import ElementTree as ET
import sys

#Variables for save coords
coord_multi = []
coord_one = []

@dataclass
class Fields:
    name: str
    type: str
    tag: str
    flag: int
    childtag: str = ''
    value: str = ''


# 0 - внешний тег
# 1 - внутри тега land_record
# 2 - необходимо спуститься к потомкам

list_of_fields = [Fields('cadnumber', 'Char(18)', 'cad_number', 1),
                  Fields('quartal', 'Char(13)', 'cadastral_number', 0),
                  Fields('parentnum', 'Char(17)', 'common_land_cad_number', 2, 'cad_number', value='--'),
                  Fields('utildoc', 'Char(254)', 'by_document', 1),
                  Fields('utiltype', 'Char(254)', 'land_use_mer', 2, 'value'),
                  Fields('category', 'Char(50)', 'category', 2, 'value'),
                  Fields('area', 'Decimal(20,2)', 'area', 2, 'value'),
                  Fields('inaccur', 'Decimal(20,2)', 'inaccuracy', 1),
                  Fields('resdate', 'Char(10)', 'date_formation', 0),
                  Fields('address', 'Char(254)', 'readable_address', 1),
                  Fields('Деклар', 'integer', '', 0, value='0'),
                  Fields('ДекларКП', 'integer', '', 0, value='0'),
                  Fields('Дата_изм', 'Char(10)', '', 0, value=''),
                  Fields('Дата_рег', 'Char(10)', '', 0, value=''),
                  Fields('Изменился', 'integer', '', 0, value='0')
                  ]


log_file = open('output_files/logs.txt', 'w', encoding='cp1251')
mif_file = open('output_files/response.mif', 'w', encoding='cp1251')
mid_file = open('output_files/response.mid', 'w', encoding='cp1251')
head = u'Version 300' + '\n' + 'Charset "WindowsCyrillic"' + '\n' + \
               'Delimiter ","' + '\n' + 'CoordSys NonEarth Units "m" Bounds (200000, 2000000) (800000, 2500000)' + \
               '\n' + 'Columns ' + str(len(list_of_fields)) + '\n'
str_head = head.encode('cp1251').decode('cp1251')

# Flags
contur = 0
conturs = 0
land_records = 0
add_flag = ''

#
def get_field_from_tag(tag):
    global list_of_fields
    for field in list_of_fields:
        if tag == field.tag:
            return field
    return False

#Запись шапки mif-файла
mif_file.write(str_head)
for field in list_of_fields:
    mif_file.write('  ' + field.name + ' ' + field.type + '\n')
mif_file.write('Data' + 2 * '\n')

xml_iter = ET.iterparse('Response №50-27939031.xml', events=('start', 'end'))
for event, elem in xml_iter:
    text = elem.text
    current_field = get_field_from_tag(elem.tag)
    # Открывающий тэг, данные потомка и элемента пока недоступны
    if event == 'start':
        # Признак начала объекта (одноконтурный или часть многоконтурного)
        if elem.tag == 'contour':
            contur = 1
        # Признак КПТ_УЧАСТКИ
        elif elem.tag == 'land_records':
            land_records = 1
        if land_records:
            if current_field and current_field.flag == 2:
                 add_flag = current_field.tag
        else:
            if current_field and current_field.flag == 0:
                current_field.value = text
# Закрывающий тэг, доступны узлы-потомки, текстовые узлы
    elif event == 'end':
# Слой КПТ_Участки завершен
        if elem.tag == 'land_records':
            land_records = 0
        if land_records:
            if add_flag == elem.tag:
                add_flag = ''
            if add_flag:
                child_field = get_field_from_tag(add_flag)
                if child_field.childtag == elem.tag:
                    child_field.value = text
            if current_field:
                if current_field.flag == 1:
                    current_field.value = text
    # Объект закончился, данные по нему считаны, записываем в файл
    #----------------------------------------------------------------------------------------
            elif elem.tag == 'contours':
                conturs = 0
                print('writing')
                # Проверка, что данные не пустые
                if len(coord_multi) > 0:
                    mif_file.write(' ' + 'Region ')
                    # Число участков в контуре
                    mif_file.write(str(len(coord_multi)) + '\n')
                    # Кадастровый номер
                    i = 0
                    for field in list_of_fields:
                        if i < (len(list_of_fields) - 1):
                            if 'Char' in field.type:
                                mid_file.write('"' + field.value + '"' + ',')
                            else:
                                mid_file.write(field.value + ',')
                        else:
                            mid_file.write('"' + field.value + '"' + '\n')
                        i += 1
                    for items in coord_multi:
                        if (len(items)) > 0:
                            # Записываем число координат
                            # Деление пополам - т.к в списке обе координаты x и y
                            mif_file.write(str(len(items)//2) + '\n')
                            # Цикл записи координат x и y, x занимает нечетную позицию в списке,y - четную
                            i = 0
                            while i < len(items):
                                mif_file.write(items[i])
                                mif_file.write(' ')
                                mif_file.write(items[i+1])
                                mif_file.write('\n')
                                i += 2
                            mif_file.write('\n')
                    # Очищаем массив для последующих данных
                    coord_multi.clear()
                # Удаляем элементы прочитанной части дерева
                elem.clear()
    #----------------------------------------------------------------------------------------
    # Признак того, что элементы контура закончились
    # Перезаписываем координаты в список для записи coord_multi
            elif elem.tag == 'contour':
                contur = 0
                if len(coord_one) > 0:
                    coord_multi.append(coord_one)
                    coord_one = []
    # Сохраняем в список координаты одного контура
            if contur:
                if elem.tag == 'x':
                    coord_one.append(text)
                elif elem.tag == 'y':
                    coord_one.append(text)
#--------------------------------------


mif_file.close()
mid_file.close()
