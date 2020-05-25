#Последний рабочий вариант

from xml.etree import ElementTree as ET

#Variables for save coords
coord_multi = []
coord_one = []

mif_file = open('response.mif', 'w', encoding='cp1251')
mid_file = open('response.mid', 'w', encoding='cp1251')
str_heading = 'Version 300' + '\n' + 'Charset "WindowsCyrillic"' + '\n' + \
               'Delimiter ","' + '\n' + 'CoordSys NonEarth Units "m" Bounds (200000, 2000000) (800000, 2500000)' + \
               '\n' + 'Columns 1' + '\n' + '  ' + 'КН Char(30)' + '\n' + 'Data' + 2*'\n'
# Flags
contur = 0
conturs = 0
land_records = 0

mif_file.write(str_heading)

xml_iter = ET.iterparse('Response №50-27939031.xml', events=('start', 'end'))
for event, elem in xml_iter:
    text = elem.text
# Открывающий тэг, данные потомка и элемента пока недоступны
    if event == 'start':
# Признак начала объекта (одноконтурный или часть многоконтурного)
        if elem.tag == 'contour':
            contur = 1
# Признак КПТ_УЧАСТКИ
        elif elem.tag == 'land_records':
            land_records = 1
# Закрывающий тэг, доступны узлы-потомки, текстовые узлы
    elif event == 'end':
# Слой КПТ_Участки завершен
        if elem.tag == 'land_records':
            land_records = 0
        if land_records:
            # Сохраняем в переменную кадастровый номер
            if elem.tag == 'cad_number':
                cad_number = text
    # Объект закончился, данные по нему считаны, записываем в файл
    #----------------------------------------------------------------------------------------
    #        elif elem.tag == 'contours' or elem.tag == 'cadastral_blocks':
            elif elem.tag == 'contours':
                conturs = 0
                print('writing')
                # Проверка, что данные не пустые
                if len(coord_multi) > 0:
                    mif_file.write(' ' + 'Region ')
                    # Число участков в контуре
                    mif_file.write(str(len(coord_multi)) + '\n')
                    # Кадастровый номер
                    mid_file.write('"' + cad_number + '"' + '\n')
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