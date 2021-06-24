'''
Author: mount_potato
Date: 2021-06-16 16:49:22
LastEditTime: 2021-06-24 19:24:18
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \File-Management-Demo\file-management.py
'''
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QLabel, QTreeWidgetItem, QWidget, QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit, QMenu, QAction
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5 import QtGui, QtCore
import mainwindow
from utils import *
import time
import copy
from memory import *

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

    
        # #位图列表
        self.bitmap_list=[]

        self.setup()

    ################################内存写方法#########################
            
    





                




    def setup(self):

        ###基础参数设置
        #当前目录名字
        self.curr_directory_name=""
        #当前路径
        self.curr_path="current path: ./"
        self.curr_path_list=[""]
    
        #目录列表:(文件名，初始块地址，文件大小，文件类型）
        self.curr_directory_list = [["Parent\n"], [0], [0], [1]]
        #当前目录的初始块地址
        self.curr_directory_node=INIT_BLOCK
        #当前编辑的文本文档的初始块地址
        self.curr_text_node=0
        #当前表格点击行
        self.curr_row=0

        self.init_dir_list=[]
        self.root_path="current path: ./"
        self.init_node=INIT_BLOCK

        self.curr_root=None
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
        source_path="./root.txt"
        if not os.path.exists(source_path):
            #111110000,
            self.bitmap_list.append(b"\xf8" + b"\x00" * 1023) #1kb  
            
            for i in range(0,TOTAL_KB-1):
                self.bitmap_list.append(b"\x00" * 1024)
            
            self.curr_directory_list=[["Parent\n"], [0], [0], [1]]
            dir_byte_str=dir_list_to_str(self.curr_directory_list)    
            write_file(self,INIT_BLOCK,dir_byte_str)

            #print(dir_byte_str)
        else:
            #存在文件,读取信息
            srcfile_data=open(source_path,'rb')
            for times in range(0,TOTAL_KB):
                tmp_bytes=srcfile_data.read(1024)
                self.bitmap_list.append(tmp_bytes)
            srcfile_data.close()
            
            self.curr_directory_list=dir_str_to_list(read_file(self,4))
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
            self.curr_row=self.tbl_file_table.currentRow()
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
        else:
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
                new_assign=assign_memory(self)
                self.curr_directory_list_add(value,new_assign,0,0)
                write_file(self,new_assign,b"\xfe\xfe")
                cut_to_zero_file(self,self.curr_directory_node)
                write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))
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
            new_assign=assign_memory(self)
            self.curr_directory_list_add(value,new_assign,0,1)
            dir_str=dir_list_to_str([["Parent\n"], [self.curr_directory_node], [0], [1]])
            write_file(self,new_assign,dir_str)
            cut_to_zero_file(self,self.curr_directory_node)
            write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))
            self.update_tree_view()
        
    #3
    def on_format_btn_clicked(self):
        choice=QMessageBox.question(self,"Formatting...","Are you sure you want to delete all the files?",QMessageBox.Yes|QMessageBox.No)
        if choice==QMessageBox.No:
            return
        else:
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
            dir_byte_str=dir_list_to_str(self.curr_directory_list)    
            write_file(self,INIT_BLOCK,dir_byte_str)
            self.update_tree_view()
        
            

    #4
    def on_save_exit_btn_clicked(self):

        cut_to_zero_file(self,self.curr_directory_node)
        write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))

        srcfile_data=open("./root.txt","wb")
        for i in self.bitmap_list:
            srcfile_data.write(i)
        srcfile_data.close()
        QApplication.quit()

    #5
    def on_return_btn_clicked(self):
        if self.curr_path =="current path: ./":
            return
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
        cut_to_zero_file(self,self.curr_directory_node)
        write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))
        self.curr_directory_node=self.curr_directory_list[1][0]
        self.curr_directory_list=dir_str_to_list(read_file(self,self.curr_directory_node))
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
        text=text+b'\xfe' if text_len%1022==1021 else ( text+b'\xfe\xfe' if text_len%1022!=0 else text)
        
        cut_to_zero_file(self,self.curr_text_node)
        write_file(self,self.curr_text_node,text)
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
            content_len=len(self.curr_path)%40
            self.curr_path+=self.curr_directory_name
            curr_len=len(self.curr_path)%40

            self.curr_path+=("\n/" if(curr_len<=content_len or content_len==0) else "/")
            
            self.lbl_file_name.setText(self.curr_path)
            #表格修改
            self.tbl_file_table.clearContents()
            self.tbl_file_table.setRowCount(0)
            self.curr_path_list.append(file_name)
            self.btn_return.setEnabled(True)
            #打开
            self.update_tree_view()
            cut_to_zero_file(self,self.curr_directory_node)
            write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))
            self.curr_directory_node=self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)]
            self.curr_directory_list=dir_str_to_list(read_file(self,self.curr_directory_node))
            
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
            self.lbl_file_name.setText("file size: " \
                                        +str(self.curr_directory_list[2][self.curr_directory_list[1].index(self.curr_text_node)]) \
                                        +" B\t\t"
                                        +'<font color = #00FFFF>%s</font>'%("please edit below ↓"))
            text=str(read_file(self,self.curr_text_node),encoding="utf-8")
            self.edt_textbox.setPlainText(text)
            self.edt_textbox.moveCursor(QTextCursor.End)   
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
            cut_to_zero_file(self,self.curr_directory_node)
            write_file(self,self.curr_directory_node, dir_list_to_str(self.curr_directory_list))   

        self.update_tree_view()
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    #删除文件
    def on_delete_action_triggered(self):
        row=self.curr_row
        file_name=self.tbl_file_table.item(row,0).text()
        file_type=self.tbl_file_table.item(row,2).text()

        if file_type=="txt file":
            cut_to_zero_file(self,self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
            erase_data(self,self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
        else: #file_type=="txt file"
            self.recur_delete_directory(self.curr_directory_list[1][self.curr_directory_list[0].index(file_name)])
        
        for i in range(3,-1,-1):
            del self.curr_directory_list[i][self.curr_directory_list[0].index(file_name)]
        self.tbl_file_table.removeRow(row)

        cut_to_zero_file(self,self.curr_directory_node)
        write_file(self,self.curr_directory_node,dir_list_to_str(self.curr_directory_list))
        self.curr_directory_list=dir_str_to_list(read_file(self,self.curr_directory_node))
        self.update_tree_view()
        self.tbl_file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    def recur_delete_directory(self,node):
        dir_list=dir_str_to_list(read_file(self,node))
        for i in range(1,len(dir_list[0])):
            if dir_list[3][i]==1:
                self.recur_delete_directory(dir_list[1][i])
            cut_to_zero_file(self,dir_list[1][i])
            erase_data(self,dir_list[1][i])



    def set_widget_list_available(self,bool1,bool2):
        for i in self.widget_list_1:
            i.setEnabled(bool1)
        for i in self.widget_list_2:
            i.setEnabled(bool2)
    
    def curr_directory_list_add(self,c1,c2,c3,c4):
        tmp=[c1,c2,c3,c4]
        for i in range(0,len(tmp)):
            self.curr_directory_list[i].append(tmp[i])
    
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
                cut_to_zero_file(self,tmp_node)
                write_file(self,tmp_node,dir_list_to_str(tmp_dir_list))
                tmp_node=tmp_dir_list[1][tmp_dir_list[0].index(folder_name)]
                tmp_dir_list=dir_str_to_list(read_file(self,tmp_node))
                self.update_tree(tmp_dir_list,tmp_node,folder_child,folder_name)                
                
        self.tree_directory_view.addTopLevelItem(root)
        self.tree_directory_view.expandAll()




if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet(QSS_READER.read("./style/style.qss"))
    window=FileManagement()
    window.show()
    sys.exit(app.exec())

    

        
    

        
        
