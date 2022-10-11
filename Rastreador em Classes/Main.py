from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
import tkinter as tk

#Biblioteca do mapa de calor
import matplotlib
import matplotlib.pyplot as plt
#from matplotlib.colors import LinearSegmentedColormap
#from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import serial.tools.list_ports   #Biblioteca de conecção serial
import time                      #Biblioteca para delay
import csv                       #Biblioteca salvar dados em arquivo csv
import numpy as np               #Biblioteca de array
from datetime import datetime, timedelta    #Biblioteca do tempo da maquina
import os


#Escrita e Leitura serial com grbl
from cnc_controle import controle_cnc
from analisador_controle import controle_analisador
from gerador_controle import controle_gerador

class main_window(Frame):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.serial_cnc = None
        self.visa_analisador = None
        self.visa_gerador = None
    
    def initUI(self):
        #-Altera todas as fontes
        def_font = font.nametofont("TkDefaultFont")
        def_font.config(size=9)
        
        #---nome da janela---------------------
        self.master.title('Controle Auto Scan')#futuro nome?
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
        frm_01 = Labelframe(self.frm_notebook1, text='Serial')
        frm_01.place(x=10,y=1,width=440,height=95)
        
        #---configuração da linha/coluna------
        frm_01.columnconfigure(0, pad=3)
        frm_01.columnconfigure(1, pad=3)
        frm_01.rowconfigure(0, pad=3)
        frm_01.rowconfigure(1, pad=3)
        frm_01.rowconfigure(2, pad=3)
        frm_01.rowconfigure(3, pad=3)
        frm_01.rowconfigure(4, pad=3)
        
        #---configuração linha analisador-----
        lbl_01 = Label(frm_01, text='Analisador:')
        lbl_01.place(x=5,y=3,width=90,height=20)
        
        self.cmb_analisador = Combobox(frm_01)
        self.cmb_analisador.place(x=73,y=2,width=185,height=23)      
   
        self.btn_open_analisador = Button(frm_01, text='Abrir')
        self.btn_open_analisador.place(x=267,y=1,width=80,height=25)
        self.btn_open_analisador['command'] = serials.abrir_visa_analisador
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.place(x=5,y=30,width=90,height=20)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.place(x=73,y=29,width=185,height=23)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.place(x=267,y=27,width=80,height=25)
        self.btn_open_cnc['command'] = serials.abrir_serial_cnc

            
        
        serials.lista_serial(self)       
        
class serials(Frame):
        def __init__(self):

            
            super().__init__()
          
        def lista_serial(self):
            portas=controle_cnc.list_serial()
            
     
            self.cmb_analisador['values'] = portas
            self.cmb_analisador.set('Escolha...')
        
            self.cmb_cnc['values'] = portas
            self.cmb_cnc.set('Escolha...')
        
#             self.cmb_gerador['values'] = portas
#             self.cmb_gerador.set('Escolha...')

        def abrir_visa_analisador():
#             if (self.verifica_medicao()):
#                 return
            com_port =  self.cmb_analisador.get()
            self.visa_analisador=controle_analisador.open_visa_analisador(com_port, self.visa_analisador)
            
            if(self.visa_analisador==None):
                self.btn_open_analisador['text'] = 'Abrir'
            else:
                self.btn_open_analisador['text'] = 'Fechar'
            self.att_freq()
            
       
        def abrir_serial_cnc(self):
            if (self.verifica_medicao()):
                return
            com_port =  self.cmb_cnc.get()
            self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc)
            
            if(self.serial_cnc==None):
                self.btn_open_cnc['text'] = 'Abrir'
            else:
                self.btn_open_cnc['text'] = 'Fechar'
                
        def abrir_visa_gerador(self):
            if (self.verifica_medicao()):
                return
            com_port =  self.cmb_gerador.get()
            self.visa_gerador=controle_gerador.open_visa_gerador(com_port, self.visa_gerador)
            if(self.visa_gerador==None):
                self.btn_open_gerador['text'] = 'Abrir'
            else:
                self.btn_open_gerador['text'] = 'Fechar'
            self.att_ger()
        


def main():
    """Função que gera a janela da interface junto com suas características."""
    #---Gera janela-----------------------
    root = Tk()
    root.geometry('1080x720')
    
    #retorna tamanho da janela
    #root.bind("<Configure>", resize)
    
    #maximiza a janela
    #root.state('zoomed')
    
    #janela modo tela cheia
    #root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    
    #desabilita resize
    #root.resizable(0, 0)
    root.call('tk', 'scaling', 1.3)          #define escala (funciona porém quando fica muito alta continua problema
    #windll.shcore.SetProcessDpiAwareness(1) #altera dpi do sistema operacional (não funciona)
    #---icone da janela-------------------
    try:
        icone = PhotoImage(file = os.path.realpath(__file__).replace(os.path.basename(__file__),'')+'labcem_icone.png') 
        root.iconphoto(False, icone)
    except Exception as e:
        print(e)
    #-------------------------------------
    app = main_window()
    root.mainloop()

if __name__ == "__main__":
    main()