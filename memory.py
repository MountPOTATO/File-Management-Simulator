'''
Author: mount_potato
Date: 2021-06-24 11:04:14
LastEditTime: 2021-06-24 14:31:08
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \File-Management-Demo\memory-access.py
'''


from PyQt5.QtWidgets import  QApplication, QMessageBox



def locate(word):
    return int.from_bytes(word, byteorder='big')

def assign_memory(file_system):
    location = 0
    for i in range(0,4):
        arr = bytearray(file_system.bitmap_list[i])
        j=0
        while j!=1024:
            if arr[j] != 256-1:
                str_list = bin(arr[j])[2:]
                while len(str_list) < 8:
                    str_list = '0' + str_list
                str_list = list(str_list)
                for k in range(8):
                    if str_list[k] == '0':
                        str_list[k] = '1'
                        location = i * 1024 * 8 + j * 8 + k
                        break
                arr[j] = int("".join(str_list), 2)
                file_system.bitmap_list[i] = bytes(arr)
                return location
            j+=1
    QMessageBox. critical(file_system, 'Error','Memory overflow！\nThe file management system will be formatted。') 
    QApplication.quit()



def read_file(file_system, start_location):
    read_file_bytes = b''
    location = start_location
    while location != 0:
        tmp_list=file_system.bitmap_list[location]
        if locate(tmp_list[1022:]) == 0:
            i = -1
            while i < 1022:
                i += 1
                if tmp_list[i] == 254 and tmp_list[i + 1] == 254:
                    break
            read_file_bytes += tmp_list[:i]
        else:
            read_file_bytes += tmp_list[:1022]
        location = locate(tmp_list[1022:])
    return read_file_bytes

def write_file(file_system, start_location, packed_data):
    length = int(len(packed_data) / 1022) + 1
    if length % 1022 == 1021:
        packed_data += b'\xfe'
    elif length % 1022 != 0:
        packed_data += b'\xfe\xfe'
    while length > 0:
        length -= 1
        if length != 0:
            location = assign_memory(file_system)
            add_data(file_system,start_location, packed_data[:1022], location)
            start_location = location                
        else:
            add_data(file_system,start_location, packed_data[:1022], 0)
        packed_data = packed_data[1022:]



def add_data(file_system, location, data, next):
    next = next.to_bytes(2, byteorder='big')
    arr = bytearray(file_system.bitmap_list[location])
    i=0
    while i!=1022:
        arr[i]=data[i] if i<len(data) else 0
        i+=1    
    
    for i in range(0,2):
        arr[1022+i]=next[i]
    file_system.bitmap_list[location] = bytes(arr)

def erase_data(file_system, location):
    arr = bytearray(file_system.bitmap_list[location])
    for i in arr:
        i=0  
    file_system.bitmap_list[location] = bytes(arr)
    i = int(location / (1024 * 8))
    j = int((location - i * 1024 * 8) / 8)
    k = location % 8

    str_list = bin(bytearray(file_system.bitmap_list[i])[j])[2:]
    str_list = list('0'*(8-len(str_list))+str_list)
    arr[j] = int("".join(str_list), 2)
    str_list[k] = '0'
    file_system.bitmap_list[i] = bytes(arr)

def dir_list_to_str(list):
    dir_converted_str = b''
    lst_str, lst_location, lst_size, lst_type = list
    for i in range(0,len(lst_str)):
        str_info=lst_str[i].encode(encoding = 'utf-8')
        loc_info=lst_location[i].to_bytes(2, byteorder='big')
        size_info=lst_size[i].to_bytes(2, byteorder='big')
        type_info=lst_type[i].to_bytes(2, byteorder='big')
        dir_converted_str += (str_info + b'\xff' + loc_info + size_info + type_info + b'\xff')
    return dir_converted_str  

def dir_str_to_list(packed_bytes):

    i = 0
    res_list=[[],[],[],[]]

    while i<len(packed_bytes):
        while(packed_bytes[i] != 255):
            i += 1 
        res_list[0].append(packed_bytes[0:i].decode(encoding = 'utf-8')) #lst_str
        res_list[1].append(int.from_bytes(packed_bytes[i + 1:i + 3], byteorder='big')) #lst_location
        res_list[2].append(int.from_bytes(packed_bytes[i + 3:i + 5], byteorder='big')) #lst_size
        res_list[3].append(int.from_bytes(packed_bytes[i + 5:i + 7], byteorder='big')) #lst_type
        packed_bytes = packed_bytes[i + 8:]
        i = 0
    return res_list

def cut_to_zero_file(file_system, start_location):
    list_block = []
    location = start_location
    while location != 0:
        list_block.append(location)
        location = locate(file_system.bitmap_list[location][1022:])
    is_released = False
    for i in list_block:
        if is_released == False:
            is_released = True
        else:
            erase_data(file_system,i)