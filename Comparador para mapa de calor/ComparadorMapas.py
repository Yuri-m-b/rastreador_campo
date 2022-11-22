#Biblioteca de interface
from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
#from ttkthemes import ThemedStyle

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

class main_window(Frame):
    flag_medindo, flag_stop = False, False
    flag_grade, flag_anotacao, flag_auto_maxmin= True, True, True
    max_medido, min_medido = -99, 99
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        
    def initUI(self):
        #-Altera tema da janela
        #style = ThemedStyle(self)
        #style.set_theme("black")
        #style=Style()
        #print(style.theme_names())
        #style.theme_use("black")
        
        #-Altera todas as fontes
        def_font = font.nametofont("TkDefaultFont")
        def_font.config(size=9)
        
        #---nome da janela---------------------
        self.master.title('Comparador de Mapa de Calor')#futuro nome?
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        #notebook.add(self.frm_notebook1, text='      Comparador      ')
        
                #--Parametros de plotagem
        frm_plot = Labelframe(self.frm_notebook1, text='Menu')
        frm_plot.place(x=10,y=5,width=240,height=680)  
        
        #---Label frame da barra de cor
        frm_plot_parametro = Labelframe(frm_plot)
        frm_plot_parametro.place(x=5,y=1,width=225,height=150)
        
        #----Definição de parametros da barra de cor
        frm_plot_maxmin = Labelframe(frm_plot_parametro, text='Entrada manual:')
        frm_plot_maxmin.place(x=5,y=0,width=212,height=47)
        
        lbl_21 = Label(frm_plot_maxmin, text='MAX. :')
        lbl_21.place(x=5,y=5,width=60,height=20)
        self.var_plot_max=Entry(frm_plot_maxmin, width=8)
        self.var_plot_max.insert(END, '%d' % 10)
        self.var_plot_max.place(x=45,y=3,width=57,height=20)
        self.var_plot_max['state'] = 'disable'
        
        lbl_22 = Label(frm_plot_maxmin, text='MIN. :')
        lbl_22.place(x=110,y=5,width=60,height=20)
        self.var_plot_min=Entry(frm_plot_maxmin, width=8)
        self.var_plot_min.insert(END, '%d' % -80)
        self.var_plot_min.place(x=145,y=3,width=57,height=20)
        self.var_plot_min['state'] = 'disable'
        
        lbl_ou = Label(frm_plot_parametro, text=' OU')
        lbl_ou.place(x=95,y=47,width=30,height=15)
        
        self.btn_plt_maxmin = Button(frm_plot_parametro, text='MAX/MIN automático HABILITADO')
        self.btn_plt_maxmin.place(x=5,y=65,width=213,height=34)
        self.btn_plt_maxmin['command'] = self.plot_auto_maxmin
        
        #---Titulo do plot
        frm_plot_titulo = Labelframe(frm_plot)
        frm_plot_titulo.place(x=5,y=153,width=225,height=500)
        
        lbl_22 = Label(frm_plot_titulo, text=' Título do plot :')
        lbl_22.grid(row=0, column=0, padx= 3)
        self.var_plot_titulo=Entry(frm_plot_titulo, width=80)
        self.var_plot_titulo.insert(END, 'nome_exemplo')
        self.var_plot_titulo.place(x=5,y=25,width=210,height=20)
        
        self.btn_abrir_plot = Button(frm_plot_titulo, text='Abrir Arquivo CSV')
        self.btn_abrir_plot.place(x=5,y=65,width=213,height=34)
#         self.btn_abrir_plot['command'] =

        #---nome do frame---------------------
        frm_param = Labelframe(frm_plot_titulo, text='Informações')
        frm_param.place(x=5,y=105,width=210, height=95)
        
        frm_param.columnconfigure(0, pad=3)
        frm_param.columnconfigure(1, pad=3)
        
        frm_param.rowconfigure(0, pad=3) # Número de arquivos abertos
        frm_param.rowconfigure(1, pad=3) # Valor Máximo
        frm_param.rowconfigure(2, pad=3) # Valor Mínimo
        
        lbl_par_1 = Label(frm_param, text='Quantidade de arquivos lidos:')
        lbl_par_2 = Label(frm_param, text='Maior valor medido:')
        lbl_par_3 = Label(frm_param, text='Menor valor medido:')
        self.lbl_par_4 = Label(frm_param, text='0')
        self.lbl_par_5 = Label(frm_param, text='-99,00')
        self.lbl_par_6 = Label(frm_param, text='-99,00')
        
        lbl_par_1.grid(row=0, column=0, sticky=W)
        lbl_par_2.grid(row=1, column=0, sticky=W)
        lbl_par_3.grid(row=2, column=0, sticky=W)
        self.lbl_par_4.grid(row=0, column=1, sticky=E)
        self.lbl_par_5.grid(row=1, column=1, sticky=E)
        self.lbl_par_6.grid(row=2, column=1, sticky=E)
        
        #-----------------------------------------
        btn_plt_dado_atual = Button(frm_plot_titulo, text='Plotar Mapas de Calor')
        btn_plt_dado_atual.place(x=5,y=220,width=210,height=40)
        btn_plt_dado_atual['command'] = self.plot_arquivo_csv
    
    
    def plot_auto_maxmin(self):
        if(self.flag_auto_maxmin):
            self.btn_plt_maxmin.config(text='MAX/MIN automático DESABILITADO')
            self.var_plot_max['state'] = 'enable'
            self.var_plot_min['state'] = 'enable'
            self.flag_auto_maxmin=False
        else:
            self.btn_plt_maxmin.config(text='MAX/MIN automático HABILITADO')
            self.var_plot_max['state'] = 'disable'
            self.var_plot_min['state'] = 'disable'
            self.flag_auto_maxmin=True
            
    #Função se string contem somente numero e maior que zero     
    def verifica_string(self, string, mensagem):
        #Caso número comece com sinal negativo substitui o sinal por '0'
        if not(string.isdigit()):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        
        if(int(string)==0):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        else:
            return False
            
    def verifica_numero(self, string, mensagem):
        #Caso número comece com sinal negativo substitui o sinal por '0'
        if(string[0]=='-'):
            string=string.replace('-','0',1)
        if not(string.isdigit()):#verifica se é somente digito
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal'))
            return True
        return False
            
            
    def plot_arquivo_csv(self):
        if not (self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        if(self.verifica_string(self.var_plot_tamanho_x.get(), 'Tamanho da placa')):
            return
        if(self.verifica_string(self.var_plot_tamanho_y.get(), 'Tamanho da placa')):
            return
        try:
            data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))
            data=[]
            with open(data_caminho, 'r') as file:
                reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
                for row in reader: # each row is a list
                    data.append(row)
        except:
            return
        if(len(data)<1)or(len(data[0])<1):
            #acusa erro de arquivo csv com problema na linha ou coluna
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(map(max,data))
            vmin=min(map(min,data))
            print(vmax)
            print(vmin)
        else:
            vmax=int(self.var_plot_max.get())#função que verifica se é numero
            vmin=int(self.var_plot_min.get())#função que veririca se é numero
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
        
        if(self.var_espelhamento_x.get()):#Se espelhamento no eixo X selecionado
            for aux in data:
                aux.reverse()
                
        if(self.var_espelhamento_y.get()):#Se espelhamento no eixo Y selecionado
            data.reverse()
        
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save)
    

def resize(event):
    """Função que altera o tamanho da janela do programa."""
    print("Novo tamanho é: {}x{}".format(event.width, event.height))

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

if __name__ == '__main__':
    main()