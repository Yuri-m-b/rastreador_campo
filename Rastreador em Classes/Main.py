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
        
   
        self.cmb_analisador = Combobox(self.frm_notebook1)
        self.cmb_analisador.place(x=73,y=2,width=185,height=23)    
            
#         btn = Button(self.frm_notebook1, text='Abortar Medição')
#         btn.place(x=235,y=400,width=216,height=40)
#         btn['command'] = self.dothings
        
        serials.lista_serial(self)       
        
class serials(Frame):
        def __init__(self):

            
            super().__init__()
          
        def lista_serial(self):
            portas=controle_cnc.list_serial()
            
     
            self.cmb_analisador['values'] = portas
            self.cmb_analisador.set('Escolha...')
        
#             self.cmb_cnc['values'] = portas
#             self.cmb_cnc.set('Escolha...')
        
#             self.cmb_gerador['values'] = portas
#             self.cmb_gerador.set('Escolha...')
        


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