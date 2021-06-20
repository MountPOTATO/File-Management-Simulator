'''
Author: mount_potato
Date: 2021-06-16 16:49:22
LastEditTime: 2021-06-20 21:54:41
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \File-Management-Demo\file-management.py
'''
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QLabel, QTreeWidgetItem, QWidget, QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtCore
import mainwindow
from utils import *
import time
import copy

INIT_BLOCK=4
TOTAL_MB=32
TOTAL_KB=1024*TOTAL_MB
FOLDER=1
FILE=2

class FileManagement(QMainWindow,mainwindow.Ui_MainWindow):
    
    def __init__(self):
        super(FileManagement,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("OS assignment-3 :File Management Simulator")
        self.setWindowIcon(QIcon("./resources/icon.png"))
        self.setWindowOpacity(0.95)
        #组件表
        self.widget_list_1=[self.tree_directory_view,self.btn_return,self.tbl_file_table,self.btn_new_file,
                            self.btn_new_directory,self.btn_save_exit,self.btn_format]
        self.widget_list_2=[self.edt_textbox,self.btn_quit,self.btn_save]

        #图标设置
        
        ###基础参数设置
        #当前目录名字
        self.curr_directory_name=""
        #当前文件
        self.curr_file=None
        #当前路径
        self.curr_path="current path: ./"
        self.curr_path_list=[""]
    
        #位图列表
        self.bitmap_list=[]
        #当前目录中包含的文件（文件名，初始块地址，文件大小，文件类型；"Parent\n"是返回上级目录）
        self.curr_directory_list = [["Parent\n"], [0], [0], [1]]
        #当前目录的初始块地址
        self.curr_directory_node=INIT_BLOCK
        #当前编辑的文本文档的初始块地址
        self.curr_text_node=0

        self.curr_row=0

        self.init_dir_list=[]
        self.root_path="current path: ./"
        self.init_node=INIT_BLOCK

        self.curr_root=None
        self.setup()

    ################################内存写方法#########################
    
    # 每个块的最后两个字节用来保存文件后继块（如果有）的地址，这个函数将两个字节的地址转换成整数
    def locate(self, word):
        location = int.from_bytes(word, byteorder='big')
        return location
    
    # 分配块，这里倒来倒去只是为了将被分配出去的一块在位图中的对应位置1
    def assign_memory(self):
        location = 0
        for i in range(4):
            my_tmp_array = bytearray(self.bitmap_list[i])
            for j in range(1024):
                if my_tmp_array[j] != 255:
                    tmp_str_list = bin(my_tmp_array[j])[2:]
                    while len(tmp_str_list) < 8:
                        tmp_str_list = '0' + tmp_str_list
                    tmp_str_list = list(tmp_str_list)
                    for k in range(8):
                        if tmp_str_list[k] == '0':
                            tmp_str_list[k] = '1'
                            location = i * 1024 * 8 + j * 8 + k
                            break
                    my_tmp_array[j] = int("".join(tmp_str_list), 2)
                    self.bitmap_list[i] = bytes(my_tmp_array)
                    return location
        QMessageBox. critical(self, 'Error','Memory overflow！\nThe file management system will be formatted。') 
        QApplication.quit()
    
    # 向一块中写入数据
    def add_data(self, location, data, next):
        next = next.to_bytes(2, byteorder='big')
        my_tmp_array = bytearray(self.bitmap_list[location])
        for i in range(1022):
            if i < len(data):
                my_tmp_array[i] = data[i]
            else:
                my_tmp_array[i] = 0       
        my_tmp_array[1022] = next[0]
        my_tmp_array[1023] = next[1]
        self.bitmap_list[location] = bytes(my_tmp_array)
    
    # 清除一个块中的数据，并将位图中的相应位置0
    def erase_data(self, location):
        my_tmp_array = bytearray(self.bitmap_list[location])
        for i in range(1024):
            my_tmp_array[i] = 0
        self.bitmap_list[location] = bytes(my_tmp_array)
        i = location // (1024 * 8)
        j = (location - i * 1024 * 8) // 8
        k = location % 8
        my_tmp_array = bytearray(self.bitmap_list[i])
        tmp_str_list = bin(my_tmp_array[j])[2:]
        while len(tmp_str_list) < 8:
            tmp_str_list = '0' + tmp_str_list
        tmp_str_list = list(tmp_str_list)
        tmp_str_list[k] = '0'
        my_tmp_array[j] = int("".join(tmp_str_list), 2)
        self.bitmap_list[i] = bytes(my_tmp_array)


    # 把目录从列表打包成字节串
    def dir_list_to_str(self,my_list):
        packed_bytes = b''
        str_list, location_list, size_list, type_list = my_list
        for i in range(len(str_list)):
            packed_bytes += str_list[i].encode(encoding = 'utf-8') \
                            + b'\xff' \
                            + location_list[i].to_bytes(2, byteorder='big') \
                            + size_list[i].to_bytes(2, byteorder='big')  + \
                            type_list[i].to_bytes(2, byteorder='big') + b'\xff'
        return packed_bytes            
    
    # 把目录从字节串还原成列表
    def dir_str_to_list(self,packed_bytes):
        i = 0
        str_list = []
        location_list = []
        size_list = []
        type_list = []

        while i<len(packed_bytes):
            while(packed_bytes[i] != 255):
                i += 1 
            str_list.append(packed_bytes[0:i].decode(encoding = 'utf-8'))
            location_list.append(int.from_bytes(packed_bytes[i + 1:i + 3], byteorder='big'))
            size_list.append(int.from_bytes(packed_bytes[i + 3:i + 5], byteorder='big'))
            type_list.append(int.from_bytes(packed_bytes[i + 5:i + 7], byteorder='big'))
            packed_bytes = packed_bytes[i + 8:]
            i = 0
        return [str_list, location_list, size_list, type_list]

    # 读取文件，254对应b"\xfe"，连续两个254就是EOF
    def read_file(self, start_location):
        file_bytes = b''
        tmp_location = start_location
        while tmp_location != 0:
            if self.locate(self.bitmap_list[tmp_location][1022:]) != 0:
                file_bytes += self.bitmap_list[tmp_location][:1022]
            else:
                i = -1
                while i < 1022:
                    i += 1
                    if self.bitmap_list[tmp_location][i] == 254 and self.bitmap_list[tmp_location][i + 1] == 254:
                        break
                file_bytes += self.bitmap_list[tmp_location][:i]
            tmp_location = self.locate(self.bitmap_list[tmp_location][1022:])
        return file_bytes
    
    # 截短到0，由于写入时候是整块写入，所以这里实际上并没有清除初始块中的数据
    def cut_to_zero_file(self, start_location):
        block_list = []
        tmp_location = start_location
        while tmp_location != 0:
            block_list.append(tmp_location)
            tmp_location = self.locate(self.bitmap_list[tmp_location][1022:])
        release_or_not = False
        for i in block_list:
            if release_or_not == True:
                self.erase_data(i)
            else:
                release_or_not = True
    
    # 写入文件
    def write_file(self, start_location, packed_data):
        length = len(packed_data) // 1022 + 1
        if length % 1022 == 1021:
            packed_data = packed_data + b'\xfe'
        elif length % 1022 != 0:
            packed_data = packed_data + b'\xfe\xfe'
        while(length > 0):
            length -= 1
            if length == 0:
                self.add_data(start_location, packed_data[:1022], 0)
            else:
                tmp_location = self.assign_memory()
                self.add_data(start_location, packed_data[:1022], tmp_location)
                start_location = tmp_location
            packed_data = packed_data[1022:]


    def setup(self):

        '''
        触发函数设置
        '''
        #按钮函数设置
        self.btn_new_file.clicked.connect(self.on_new_file_btn_clicked)
        self.btn_new_directory.clicked.connect(self.on_new_folder_btn_clicked)
        self.btn_save_exit.clicked.connect(self.on_save_exit_btn_clicked)
        self.btn_format.clicked.connect(self.on_format_btn_clicked)
        self.btn_return.clicked.connect(self.on_return_btn_clicked)
        self.btn_save.clicked.connect(self.on_save_btn_clicked)
        self.btn_quit.clicked.connect(self.on_quit_btn_clicked)

        #右键点击菜单的设置
        self.right_click_menu=QMenu(self)
        open_action=QAction('open',self)
        rename_action=QAction('rename',self)
        delete_action=QAction('delete',self)
        open_action.triggered.connect(self.on_open_action_triggered)
        rename_action.triggered.connect(self.on_rename_action_triggered)
        delete_action.triggered.connect(self.on_delete_action_triggered)
        self.right_click_menu.addAction(open_action)
        self.right_click_menu.addAction(rename_action)
        self.right_click_menu.addAction(delete_action)
        self.tbl_file_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_file_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tbl_file_table.customContextMenuRequested.connect(self.show_menu)
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        '''
        存储于磁盘中的数据设置
        '''
        source_path="./root.mimg"
        if not os.path.exists(source_path):
            #111110000,
            self.bitmap_list.append(b"\xf8" + b"\x00" * 1023) #1kb  
            
            for i in range(0,TOTAL_KB-1):
                self.bitmap_list.append(b"\x00" * 1024)
            
            self.curr_directory_list=[["Parent\n"], [0], [0], [1]]
            dir_byte_str=self.dir_list_to_str(self.curr_directory_list)    
            self.write_file(INIT_BLOCK,dir_byte_str)

            #print(dir_byte_str)
        else:
            #存在文件,读取信息
            srcfile_data=open(source_path,'rb')
            for times in range(0,TOTAL_KB):
                tmp_bytes=srcfile_data.read(1024)
                self.bitmap_list.append(tmp_bytes)
            srcfile_data.close()
            
            self.curr_directory_list=self.dir_str_to_list(self.read_file(4))
            for i in range(1,len(self.curr_directory_list[0])):
                #添加表格中的文件内容
                if self.curr_directory_list[3][i]==0:
                    file_name=self.curr_directory_list[0][i]
                    text_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
                    text_size=self.curr_directory_list[2][self.curr_directory_list[1].index(text_node)]
                    self.table_add(
                        FILE,str(self.curr_directory_list[0][i]),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "txt file",
                            str(text_size)+" B"
                    )
                else:
                    value=self.curr_directory_list[0][i]
                    self.table_add( FOLDER,str(value),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "folder",
                            " ")
        self.set_widget_list_available(True,False)
        if self.curr_directory_name=="":
            self.btn_return.setEnabled(False)
        print(self.curr_path_list)
        print(self.curr_directory_list)
        
        self.init_dir_list=self.curr_directory_list
        
        self.update_tree_view()
        #根目录
        
        
            
        # 显示右键菜单
    def show_menu(self, pos):
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        source = self.sender()
        # 确定被点击的是列表中的哪一项
        item = source.itemAt(pos)
        if item != None:
            row=self.tbl_file_table.currentRow()
            self.curr_row=row
            self.right_click_menu.exec_(source.mapToGlobal(pos))

        
        

    ##################################触发函数########################################

    #1
    def on_new_file_btn_clicked(self):        
        counter=1
        #重命名逻辑
        while True:
            for i in range(0,self.tbl_file_table.rowCount()):
                if self.tbl_file_table.item(i,0).text()=="new file"+("" if counter==1 else " "+str(counter-1)):
                    counter+=1
                    break
            else:
                break
        init_str="new file"+("" if counter==1 else " "+str(counter-1))
        value,ok=QInputDialog.getText(self,"New File","Please input the file name: ",QLineEdit.Normal,init_str)
        if not ok:
            return
        if str(value)=="" or str(value).isspace():
            QMessageBox.warning(self,"Error!","The file name cannot be empty.")
            return
        for i in range(0,self.tbl_file_table.rowCount()):
            if self.tbl_file_table.item(i,0).text()==value:#加图修改
                QMessageBox.warning(self,"Error!","File name must be unique in the same directory.")
                return
        else:
            ##更新可视化逻辑
            self.table_add( FILE,str(value),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "txt file",
                            "0 B")
            new_assign=self.assign_memory()
            self.curr_directory_list_add(value,new_assign,0,0)
            self.write_file(new_assign,b"\xfe\xfe")
            self.cut_to_zero_file(self.curr_directory_node)
            self.write_file(self.curr_directory_node,self.dir_list_to_str(self.curr_directory_list))
            self.update_tree_view()

    #2
    def on_new_folder_btn_clicked(self):
        counter=1
        #重命名逻辑
        while True:
            for i in range(0,self.tbl_file_table.rowCount()):
                if self.tbl_file_table.item(i,0).text()=="new folder"+("" if counter==1 else " "+str(counter-1)):
                    counter+=1
                    break
            else:
                break   
        init_str="new folder"+("" if counter==1 else " "+str(counter-1))   
        value,ok=QInputDialog.getText(self,"New folder","Please input the folder name: ",QLineEdit.Normal,init_str)
        if not ok:
            return
        if str(value)=="" or str(value).isspace():
            QMessageBox.warning(self,"Error!","The folder's name cannot be empty.")
            return
        for i in range(0,self.tbl_file_table.rowCount()):
            if self.tbl_file_table.item(i,0).text()==value:
                QMessageBox.warning(self,"Error!","The folder's name must be unique in the same directory.")
                return
        else:
            ##更新可视化逻辑
            self.table_add( FOLDER,str(value),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "folder",
                            " ")
            new_assign=self.assign_memory()
            self.curr_directory_list_add(value,new_assign,0,1)
            dir_str=self.dir_list_to_str([["Parent\n"], [self.curr_directory_node], [0], [1]])
            self.write_file(new_assign,dir_str)
            self.cut_to_zero_file(self.curr_directory_node)
            self.write_file(self.curr_directory_node,self.dir_list_to_str(self.curr_directory_list))
            self.update_tree_view()
        
    #3
    def on_format_btn_clicked(self):
        choice=QMessageBox.question(self,"Formatting...","Are you sure you want to delete all the files?",QMessageBox.Yes|QMessageBox.No)
        if choice==QMessageBox.Yes:
            self.tbl_file_table.clearContents()
            self.tbl_file_table.setRowCount(0)
            self.edt_textbox.clear()
            self.curr_directory_name=""
            self.curr_path="current path: ./"
            self.lbl_file_name.setText(self.curr_path)
            self.set_widget_list_available(True,False)
            self.btn_return.setEnabled(False)
            self.curr_path_list=[""]
            self.bitmap_list=[]
            self.curr_directory_list = [["Parent\n"], [0], [0], [1]]
            self.curr_directory_node=INIT_BLOCK
            self.curr_text_node=0
            self.curr_row=0
            self.bitmap_list.append(b"\xf8" + b"\x00" * 1023) #1kb           
            for i in range(0,TOTAL_KB-1):
                self.bitmap_list.append(b"\x00" * 1024)
            dir_byte_str=self.dir_list_to_str(self.curr_directory_list)    
            self.write_file(INIT_BLOCK,dir_byte_str)
            self.update_tree_view()
        
            

    #4
    def on_save_exit_btn_clicked(self):
        if self.btn_save.isEnabled():
            self.on_save_btn_clicked()
        dir_str=self.dir_list_to_str(self.curr_directory_list)
        self.cut_to_zero_file(self.curr_directory_node)
        self.write_file(self.curr_directory_node,dir_str)

        source_path="./root.mimg"
        srcfile_data=open(source_path,"wb")
        for i in self.bitmap_list:
            srcfile_data.write(i)
        srcfile_data.close()
        QApplication.quit()

    #5
    def on_return_btn_clicked(self):
        self.curr_path=self.curr_path[:-(len(self.curr_directory_name)+2)] \
                if  self.curr_path[-2]=="\n" \
                else self.curr_path[:-(len(self.curr_directory_name)+1)]
        self.lbl_file_name.setText(self.curr_path)
        self.tbl_file_table.clearContents()
        self.tbl_file_table.setRowCount(0)
        self.curr_path_list.pop()
        self.curr_directory_name=self.curr_path_list[-1]
        if self.curr_directory_name=="":
            self.btn_return.setEnabled(False)
        self.cut_to_zero_file(self.curr_directory_node)
        self.write_file(self.curr_directory_node,self.dir_list_to_str(self.curr_directory_list))
        self.curr_directory_node=self.curr_directory_list[1][0]
        self.curr_directory_list=self.dir_str_to_list(self.read_file(self.curr_directory_node))
        for i in range(1,len(self.curr_directory_list[0])):
            if self.curr_directory_list[3][i]==0: #文本
                    #获取文本文件大小
                    file_name=self.curr_directory_list[0][i]
                    text_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
                    text_size=self.curr_directory_list[2][self.curr_directory_list[1].index(text_node)]
                    self.table_add(
                        FILE,str(self.curr_directory_list[0][i]),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "txt file",
                            str(text_size)+" B"
                    )
            else: #文件
                self.table_add(
                    FOLDER,str(self.curr_directory_list[0][i]),
                        str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                        "folder",
                        " "
                )#大小待定
        

    #6
    def on_save_btn_clicked(self):
        text=self.edt_textbox.toPlainText().encode(encoding='utf-8')
        self.edt_textbox.clear()
        self.set_widget_list_available(True,False)
        text_len=len(text)//1022+1
        #添加EOF
        if text_len%1022==1021:
            text+=b'\xfe'
        elif text_len%1022!=0:
            text+=b'\xfe\xfe'
        self.cut_to_zero_file(self.curr_text_node)
        self.write_file(self.curr_text_node,text)
        self.curr_directory_list[2][self.curr_directory_list[1].index(self.curr_text_node)]=len(text)
        self.btn_return.setEnabled(False)
        if self.curr_directory_name !="":
            self.btn_return.setEnabled(True)
        self.lbl_file_name.setText(self.curr_path)
        
        #修改表格处文件大小显示
        text_size=self.curr_directory_list[2][self.curr_directory_list[1].index(self.curr_text_node)]
        self.tbl_file_table.setItem(self.curr_row,3,QtWidgets.QTableWidgetItem(str(text_size)+" B"))
        self.tbl_file_table.setItem(self.curr_row,1,QtWidgets.QTableWidgetItem(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
    
    #7
    def on_quit_btn_clicked(self):
        self.edt_textbox.clear()
        self.set_widget_list_available(True,False)
        self.btn_return.setEnabled(False)
        if self.curr_directory_name !="":
            self.btn_return.setEnabled(True)
        self.lbl_file_name.setText(self.curr_path)

    #打开文件
    def on_open_action_triggered(self):
        row=self.curr_row
        file_name=self.tbl_file_table.item(row,0).text()
        file_type=self.tbl_file_table.item(row,2).text()
        if file_type=="folder":
            self.curr_directory_name=file_name
            content_len=len(self.curr_path)%30
            self.curr_path+=self.curr_directory_name
            curr_len=len(self.curr_path)%30
            if curr_len-content_len<=0 or content_len==0:
                self.curr_path+="\n/"
            else:
                self.curr_path+="/"
            self.lbl_file_name.setText(self.curr_path)
            #表格修改
            self.tbl_file_table.clearContents()
            self.tbl_file_table.setRowCount(0)
            self.curr_path_list.append(file_name)
            self.btn_return.setEnabled(True)
            #打开
            self.update_tree_view()
            self.cut_to_zero_file(self.curr_directory_node)
            self.write_file(self.curr_directory_node,self.dir_list_to_str(self.curr_directory_list))
            self.curr_directory_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
            self.curr_directory_list=self.dir_str_to_list(self.read_file(self.curr_directory_node))
            
            for i in range(1,len(self.curr_directory_list[0])):
                if self.curr_directory_list[3][i]==0: #文本
                    #获取文本文件大小
                    file_name=self.curr_directory_list[0][i]
                    text_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
                    text_size=self.curr_directory_list[2][self.curr_directory_list[1].index(text_node)]
                    self.table_add(
                        FILE,str(self.curr_directory_list[0][i]),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "txt file",
                            str(text_size)+" B"
                    )
                else: #文件
                    self.table_add(
                        FOLDER,str(self.curr_directory_list[0][i]),
                            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                            "folder",
                            " "
                    )#大小待定
        else: #文件
            self.set_widget_list_available(False,True)#设置文件编辑区可用
            self.curr_text_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
            #文件大小
            self.lbl_file_name.setText("file size: "+str(self.curr_directory_list[2][self.curr_directory_list[1].index(self.curr_text_node)])+" B")
            text=str(self.read_file(self.curr_text_node),encoding="utf-8")
            self.edt_textbox.setPlainText(text)   
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    #重命名文件
    def on_rename_action_triggered(self):
        row=self.curr_row
        file_name=self.tbl_file_table.item(row,0).text()
        file_type=self.tbl_file_table.item(row,2).text()
        value,ok=QInputDialog.getText(self,"Rename folder","Please input the folder name: ",QLineEdit.Normal,file_name)
        if not ok:
            return
        if str(value)=="" or str(value).isspace():
            QMessageBox.warning(self,"Error!","The folder's name cannot be empty.")
            return
        for i in range(0,self.tbl_file_table.rowCount()):
            if self.tbl_file_table.item(i,0).text()==value and i!=row:
                QMessageBox.warning(self,"Error!","The folder's name must be unique in the same directory.")
                return
        else:
            image_path="./resources/folder.png" if file_type=="folder" else "./resources/txt.png"
            self.tbl_file_table.setItem(row,0,QtWidgets.QTableWidgetItem(QIcon(image_path),value))
            self.tbl_file_table.setItem(row,1,QtWidgets.QTableWidgetItem(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
            self.curr_directory_list[0][self.curr_directory_list[0].index(file_name)] = value
            self.cut_to_zero_file(self.curr_directory_node)
            self.write_file(self.curr_directory_node, self.dir_list_to_str(self.curr_directory_list))   

        self.update_tree_view()
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    #删除文件
    def on_delete_action_triggered(self):
        row=self.curr_row
        file_name=self.tbl_file_table.item(row,0).text()
        file_type=self.tbl_file_table.item(row,2).text()

        if file_type=="folder":
            self.recur_delete_directory(self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
        else: #file_type=="txt file"
            self.cut_to_zero_file(self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
            self.erase_data(self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
        
        for i in range(3,-1,-1):
            del self.curr_directory_list[i][self.curr_directory_list[0].index(file_name)]
        self.tbl_file_table.removeRow(row)

        self.cut_to_zero_file(self.curr_directory_node)
        self.write_file(self.curr_directory_node,self.dir_list_to_str(self.curr_directory_list))
        self.curr_directory_list=self.dir_str_to_list(self.read_file(self.curr_directory_node))
        self.update_tree_view()
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    def recur_delete_directory(self,node):
        dir_list=self.dir_str_to_list(self.read_file(node))
        for i in range(1,len(dir_list[0])):
            if dir_list[3][i]==1:
                self.recur_delete_directory(dir_list[1][i])
            self.cut_to_zero_file(dir_list[1][i])
            self.erase_data(dir_list[1][i])


    #关闭窗体
    def on_close_window_clicked(self,QCloseEvent):
        box_text='''"DO you want to leave without saving?\n
                    If not, close this message box and click \"%s\".
        '''.format(self.btn_save_exit.text())

        choice=QMessageBox.warning(self,box_text,QMessageBox.Yes|QMessageBox.No)

        if choice==QMessageBox.Yes:
            QCloseEvent.accept()
        if choice==QMessageBox.No:
            QCloseEvent.ignore()

    def set_widget_list_available(self,bool1,bool2):
        for i in self.widget_list_1:
            i.setEnabled(bool1)
        for i in self.widget_list_2:
            i.setEnabled(bool2)
    
    def curr_directory_list_add(self,c1,c2,c3,c4):
        self.curr_directory_list[0].append(c1)
        self.curr_directory_list[1].append(c2)
        self.curr_directory_list[2].append(c3)
        self.curr_directory_list[3].append(c4)
    
    def table_add(self,type,c1,c2,c3,c4):
        self.tbl_file_table.insertRow(self.tbl_file_table.rowCount())
        image_path="./resources/folder.png" if type==FOLDER else "./resources/txt.png"
        self.tbl_file_table.setItem(self.tbl_file_table.rowCount()-1, 0, QtWidgets.QTableWidgetItem(QIcon(image_path),c1))
        self.tbl_file_table.setItem(self.tbl_file_table.rowCount()-1, 1, QtWidgets.QTableWidgetItem(c2))
        self.tbl_file_table.setItem(self.tbl_file_table.rowCount()-1, 2, QtWidgets.QTableWidgetItem(c3))
        self.tbl_file_table.setItem(self.tbl_file_table.rowCount()-1, 3, QtWidgets.QTableWidgetItem(c4))
        self.tbl_file_table.scrollToBottom()

    def update_tree_view(self):
        self.tree_directory_view.clear()
        if self.curr_path==self.root_path:
            self.init_dir_list=self.curr_directory_list
        self.update_tree(self.init_dir_list,self.init_node,QTreeWidgetItem(self.tree_directory_view),"root")

    def update_tree(self,list,node,root,name):
        #设置根节点
        root.setText(0,name)
        root.setIcon(0,QIcon("./resources/folder.png"))
        #add
        if list==self.curr_directory_list:
            self.curr_root=root
        print(list)
        for i in range(0,len(list[0])):
            if i==0:
                continue
            if list[3][i]==0: #文本
                txt_child=QTreeWidgetItem(root)
                txt_child.setIcon(0,QIcon("./resources/txt.png"))
                txt_child.setText(0,list[0][i])
                root.addChild(txt_child)
            else: #文件
                folder_child=QTreeWidgetItem(root)
                folder_child.setIcon(0,QIcon("./resources/folder.png"))
                folder_name=list[0][i]
                folder_child.setText(0,folder_name)
                root.addChild(folder_child)
                
                tmp_node=node
                tmp_dir_list=list
                self.cut_to_zero_file(tmp_node)
                self.write_file(tmp_node,self.dir_list_to_str(tmp_dir_list))
                tmp_node=tmp_dir_list[1][tmp_dir_list[0].index(folder_name)]
                tmp_dir_list=self.dir_str_to_list(self.read_file(tmp_node))
                self.update_tree(tmp_dir_list,tmp_node,folder_child,folder_name)                
                
        self.tree_directory_view.addTopLevelItem(root)
        self.tree_directory_view.expandAll()




if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet(QSS_READER.read("./style/style.qss"))
    window=FileManagement()
    window.show()
    sys.exit(app.exec())

    

        
    

        
        
