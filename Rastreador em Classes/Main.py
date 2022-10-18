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

class Main_Window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13
    rows_disp = 10.35  # numero de linhas apresentado
    cols_disp = 7.75 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop = False, False
    flag_grade, flag_anotacao, flag_auto_maxmin= True, True, True
    max_medido, min_medido = -99, 99
    
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
        self.btn_open_analisador['command'] = lambda : Serials.abrir_visa_analisador(self)
        
        #---Atualização de ports-----------
        btn_refresh = Button(frm_01, text='Atualizar')
        btn_refresh.place(x=353,y=12,width=75,height=53)
        btn_refresh['command'] = Serials.lista_serial
       
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.place(x=5,y=30,width=90,height=20)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.place(x=73,y=29,width=185,height=23)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.place(x=267,y=27,width=80,height=25)
        self.btn_open_cnc['command'] = lambda : Serials.abrir_serial_cnc(self)
        
        #---Configuração linha gerador-----
        lbl_03 = Label(frm_01, text='Gerador:')
        lbl_03.place(x=5,y=55,width=90,height=20)

        self.cmb_gerador = Combobox(frm_01, width=27)
        self.cmb_gerador.place(x=73,y=55,width=185,height=20)
        
        self.btn_open_gerador = Button(frm_01, text='Abrir')
        self.btn_open_gerador.place(x=267,y=52,width=80,height=24)
        self.btn_open_gerador['command'] = lambda: Serials.abrir_visa_gerador(self)
        
        #---nome do frame---------------------
        frm_inic = Labelframe(self.frm_notebook1, text='Tamanho Matriz')
        frm_inic.place(x=10,y=95,width=215,height=75)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        frm_inic.rowconfigure(1, pad=3)
        
        #---valores da matriz-----------------
        lbl_08 = Label(frm_inic, text='X :')
        lbl_08.grid(row=0, column=0)
        
        self.var_matriz_x=Entry(frm_inic, width=12)
        self.var_matriz_x.insert(END, '%d' % self.rows)
        self.var_matriz_x.grid(row=0, column=1)
        
        lbl_9 = Label(frm_inic, text='Y :')
        lbl_9.grid(row=0, column=2)
        
        self.var_matriz_y=Entry(frm_inic, width=12)
        self.var_matriz_y.insert(END, '%d' % self.cols)
        self.var_matriz_y.grid(row=0, column=3)
        
        #---botão de atualizar----------------
        btn_matriz_refresh = Button(frm_inic, text='Atualizar')
        btn_matriz_refresh.place(x=20,y=25,width=181,height=25)
        btn_matriz_refresh['command'] = lambda : Tamanho_da_Matriz.att_matriz(self) # Sem o lambda, comando não funciona
        
        #---nome do frame---------------------
        frm_param = Labelframe(self.frm_notebook1, text='Parametros')
        frm_param.place(x=235,y=95,width=215,height=215)
        
        frm_param.columnconfigure(0, pad=3)
        frm_param.columnconfigure(1, pad=3)
        
        frm_param.rowconfigure(0, pad=3)
        frm_param.rowconfigure(1, pad=3)
        frm_param.rowconfigure(2, pad=3)
        frm_param.rowconfigure(3, pad=3)
        frm_param.rowconfigure(4, pad=3)
        frm_param.rowconfigure(5, pad=3)
        frm_param.rowconfigure(6, pad=3)
        
        lbl_par_1 = Label(frm_param, text='Posição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Posição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (cm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (cm):')
        lbl_par_9 = Label(frm_param, text='Maior valor medido:')
        lbl_par_10 = Label(frm_param, text='Menor valor medido:')
        lbl_par_15 = Label(frm_param, text='Abrir arquivo CSV:')
        self.lbl_par_5 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_6 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        self.lbl_par_11 = Label(frm_param, text='-99,00')
        self.lbl_par_12 = Label(frm_param, text='-99,00')
        
        lbl_par_1.grid(row=0, column=0, sticky=W)
        lbl_par_2.grid(row=1, column=0, sticky=W)
        lbl_par_3.grid(row=2, column=0, sticky=W)
        lbl_par_4.grid(row=3, column=0, sticky=W)
        self.lbl_par_5.grid(row=0, column=1, sticky=E)
        self.lbl_par_6.grid(row=1, column=1, sticky=E)
        self.lbl_par_7.grid(row=2, column=1, sticky=E)
        self.lbl_par_8.grid(row=3, column=1, sticky=E)
        lbl_par_9.grid(row=4, column=0, sticky=W)
        lbl_par_10.grid(row=5, column=0, sticky=W)
        lbl_par_15.grid(row=6, column=0, sticky=W)
        self.lbl_par_11.grid(row=4, column=1, sticky=E)
        self.lbl_par_12.grid(row=5, column=1, sticky=E)
        
        #---nome do frame---------------------
        frm_pont = Labelframe(self.frm_notebook1, text='Definição dos pontos')
        frm_pont.place(x=10,y=165,width=215,height=65)
        
        btn_pont_start = Button(frm_pont, text='Ponto 1')
        btn_pont_start.place(x=5,y=1,width=100,height=40)
        btn_pont_start['command'] = lambda : Pontos.start_point(self)
        
        btn_pont_end = Button(frm_pont, text='Ponto 2')
        btn_pont_end.place(x=110,y=1,width=95,height=40)
        btn_pont_end['command'] = lambda : Pontos.end_point(self)
        
                #---nome do frame---------------------
        frm_freq = Labelframe(self.frm_notebook1, text='Frequência')
        frm_freq.place(x=10,y=230,width=215,height=75)
        
        frm_freq.columnconfigure(0, pad=3)
        frm_freq.columnconfigure(1, pad=3)
        frm_freq.columnconfigure(2, pad=3)
        
        frm_freq.rowconfigure(0, pad=3)
        frm_freq.rowconfigure(1, pad=3)
            
        #---valores da matriz-----------------
        lbl_08 = Label(frm_freq, text='Frequência:')
        lbl_08.place(x=5,y=3,width=90,height=20)
        
        self.var_freq=Entry(frm_freq)
        self.var_freq.insert(END, '%d' % 25)
        self.var_freq.place(x=73,y=3,width=63,height=20)
        
        self.cmb_freq = Combobox(frm_freq)
        self.cmb_freq.place(x=143,y=3,width=60,height=20)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq['state'] = 'readonly'
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.place(x=72,y=27,width=132,height=25)
        self.btn_freq_refresh['command'] = self.att_freq
        
        #---Frame do gerador----------------
        frm_gerador = Labelframe(self.frm_notebook1, text='Gerador')
        frm_gerador.place(x=10, y=300,width=440,height=90)
        
        lbl_vamp = Label(frm_gerador, text='Amplitude :')
        lbl_vamp.grid(row=0, column=0)
                
        self.vamp=Entry(frm_gerador, width=12)
        self.vamp.insert(END, '%d' % 18)
        self.vamp.grid(row=0, column=1)
        
        self.vamp_gerador_mag = Combobox(frm_gerador)
        self.vamp_gerador_mag.place(x=160,y=0,width=60,height=21)
        self.vamp_gerador_mag['values'] = ['mV', 'V']
        self.vamp_gerador_mag['state'] = 'readonly'
        self.vamp_gerador_mag.current(1)
        
        
        lbl_freq = Label(frm_gerador, text='Frequência :')
        lbl_freq.grid(row=1, column=0)
        
        self.freq_gerador=Entry(frm_gerador, width=12)
        self.freq_gerador.insert(END, '%d' % 25)
        self.freq_gerador.grid(row=1, column=1)
        
        self.freq_gerador_mag = Combobox(frm_gerador)
        self.freq_gerador_mag.place(x=160,y=20,width=60,height=21)
        self.freq_gerador_mag['values'] = ['KHz','MHz']        
        self.freq_gerador_mag['state'] = 'readonly'
        self.freq_gerador_mag.current(1)
        
        
        lbl_imp = Label(frm_gerador, text='Impedância :')
        lbl_imp.grid(row=2, column=0)
        
        self.imp=Entry(frm_gerador, width=12)
        self.imp.insert(END, '%d' %470)
        self.imp.grid(row=2, column=1)

        self.imp_gerador = Combobox(frm_gerador)
        self.imp_gerador.place(x=160,y=40,width=60,height=23)
        self.imp_gerador['values'] = ['Ω', 'KΩ']
        self.imp_gerador['state'] = 'readonly'
        self.imp_gerador.current(0)
        
        
#         btn_channel = Button(frm_gerador, text='Ligar Canal')
#         btn_channel.place(x=235, y=0, width=75, height=30)
#         lbl_channel = Label(frm_gerador, text ='Canal desligado!')
#         lbl_channel.place(x=315, y=0, width=100, heigh=30)
        
                
        btn_att_ger = Button(frm_gerador, text='Atualizar')
        btn_att_ger.place(x=235, y=17, width=75, height=30)
        btn_att_ger['command'] = self.att_ger
        
        #-Botões de atuação medição
        btn_stop = Button(self.frm_notebook1, text='Abortar Medição')
        btn_stop.place(x=235,y=400,width=216,height=40)
        btn_stop['command'] = lambda: Medicao.stop_meas(self)
        
        btn_start = Button(self.frm_notebook1, text='Iniciar Medição')
        btn_start.place(x=10,y=400,width=217,height=40)
        btn_start['command'] = lambda: Medicao.medicao(self)
        
        #---nome do frame---------------------
        frm_ctrls = Labelframe(self.frm_notebook1, text='Controle')
        frm_ctrls.place(x=10,y=445,width=440,height=240)
        
        #---configuração da linha/coluna------
        frm_ctrls.columnconfigure(0, pad=3)
        frm_ctrls.columnconfigure(1, pad=3)
        frm_ctrls.columnconfigure(2, pad=3)
        frm_ctrls.columnconfigure(3, pad=3)
        frm_ctrls.columnconfigure(4, pad=3)
        
        frm_ctrls.rowconfigure(0, pad=3)
        frm_ctrls.rowconfigure(1, pad=3)
        frm_ctrls.rowconfigure(2, pad=3)
        frm_ctrls.rowconfigure(3, pad=3)
        frm_ctrls.rowconfigure(3, pad=7)
        frm_ctrls.rowconfigure(4, pad=7)
        
        #---escrita XYZ---------------------
        lbl_03 = Label(frm_ctrls, text='Y:')
        lbl_03.grid(row=0, column=2)
        
        lbl_04 = Label(frm_ctrls, text='   X:')
        lbl_04.grid(row=2, column=0)
        
        lbl_05 = Label(frm_ctrls, text='Z:')
        lbl_05.grid(row=0, column=4)
        
        #---botão de home------------------
        btn_home = Button(frm_ctrls, text= 'Origem')
        btn_home.place(x=343,y=23,width=70,height=83)
        btn_home['command'] = lambda : Movimento.vai_origem(self) 
        
        #---configuração linhas------------   
        # Primeira linha
        btn_dig_no = Button(frm_ctrls, text=u'\u25F8')
        btn_dig_no.grid(row=1, column=1)
        
        btn_up = Button(frm_ctrls, text= u'\u25B2')
        btn_up.grid(row=1, column=2)
        btn_up['command'] = lambda direcao=self.dict_jog['up'] : Movimento.ctrl_movimento_cnc(self,direcao)      
        
        btn_dig_ne = Button(frm_ctrls, text=u'\u25F9')
        btn_dig_ne.grid(row=1, column=3)
        
        btn_z_up_btn = Button(frm_ctrls, text= u'\u25B2')
        btn_z_up_btn.grid(row=1, column=4)
        btn_z_up_btn['command'] = lambda direcao=self.dict_jog['z_up'] : Movimento.ctrl_movimento_cnc(self,direcao)
        
        # Segunda linha
        btn_left_btn = Button(frm_ctrls, text=u'\u25C0')
        btn_left_btn.grid(row=2, column=1)
        btn_left_btn['command'] = lambda direcao=self.dict_jog['left'] : Movimento.ctrl_movimento_cnc(self,direcao)
        
        btn_home_btn = Button(frm_ctrls, text=u'\u25EF')
        btn_home_btn.grid(row=2, column=2)
        
        btn_right_btn = Button(frm_ctrls, text=u'\u25B6')
        btn_right_btn.grid(row=2, column=3)
        btn_right_btn['command'] = lambda direcao=self.dict_jog['right'] : Movimento.ctrl_movimento_cnc(self,direcao)
        
        # Terceira linha       
        btn_diag_so = Button(frm_ctrls, text=u'\u25FA')
        btn_diag_so.place(x=27,y=81,width=75,height=26)
        
        btn_down = Button(frm_ctrls, text=u'\u25BC')
        btn_down.place(x=106,y=81,width=75,height=26)
        btn_down['command'] = lambda direcao=self.dict_jog['down'] : Movimento.ctrl_movimento_cnc(self,direcao)
        
        btn_diag_se = Button(frm_ctrls, text=u'\u25FF')
        btn_diag_se.place(x=185,y=81,width=75,height=26)
                
        btn_z_down = Button(frm_ctrls, text=u'\u25BC')
        btn_z_down.place(x=264,y=81,width=75,height=26)
        btn_z_down['command'] = lambda direcao=self.dict_jog['z_down'] : Movimento.ctrl_movimento_cnc(self,direcao)

        self.cmb_step = Combobox(frm_ctrls, width=5)# Janela de seleção do tamanho de passo
        self.cmb_step.grid(row=2, column=4)
        self.cmb_step['values'] = ['2','1','0.5','0.1']
        self.cmb_step.current(1)
        
        #---nome do frame Barra de Progresso---------------------
        frm_progress = Labelframe(self.frm_notebook1)
        frm_progress.place(x=460,y=640,width=608,height=45)
        
        #---tempo de progresso----------------
        self.lbl_10 = Label(frm_progress, text='Tempo estimado de '+'HH'+' : '+'MM'+' : '+'SS')
        self.lbl_10.place(x=10,y=0,width=300,height=20)
        
        #---barra de progresso----------------
        self.var_pb=DoubleVar()
        self.var_pb.set(1)        
        pb=Progressbar(frm_progress,variable=self.var_pb,maximum=100)
        pb.place(x=200,y=0,width=397,height=20)

        Serials.lista_serial(self)
        Tamanho_da_Matriz.att_matriz(self)

        
    def att_freq(self):

#         if (self.verifica_medicao()):
#             return
        
        freq = self.var_freq.get()
        
        #Verifica se string contem somente numero e maior que zero
        if (Tamanho_da_Matriz.verifica_string(self,freq, 'frequência')):
            return
        
        if(self.cmb_freq.get()=="KHz"):
            freq=int(freq)*pow(10, 3)
        elif(self.cmb_freq.get()=="MHz"):
            freq=int(freq)*pow(10, 6)
        else:
            freq=int(freq)*pow(10, 9)
        controle_analisador.receiver_frequencia(self.visa_analisador,freq)
        
    def att_ger(self):

        #Configuração da impedância do canal
        imp_ger = self.imp.get()
        
        if(self.imp_gerador.get()=="KΩ"):
            imp_ger=int(imp_ger)*pow(10, 3)
        
        controle_gerador.imp(imp_ger)

        #Configuração de frequência 
        freq_ger = self.freq_gerador.get()
        
        if (self.verifica_string(freq_ger, 'frequência')):
            return
        if(self.freq_gerador_mag.get()=="KHz"):
            freq_ger=int(freq_ger)*pow(10, 3)
        elif(self.freq_gerador_mag.get()=="MHz"):
            freq_ger=int(freq_ger)*pow(10, 6)

        controle_gerador.frequencia(freq_ger)
        
        #Configuração da amplitude de tensão 
        vamp_ger = self.vamp.get()
        
        if(self.vamp_gerador_mag.get()=="mV"):
            vamp_ger=int(vamp_ger)/pow(10, 3)
        
        controle_gerador.vamp(vamp_ger)
        
    #Função de evento de "ENTER"       
    def comp_s(self, event):
        """Função usada ao pressionar "ENTER"."""
        self.envia_cmd_cnc()
        
        
# TALVEZ USAR EM OUTRA CLASSE
#     def leitura_amplitude(self): 
#         """Função que retorna o valor lido da amplitude feita pelo analisador de espectro."""
#         #futuro ... integração com o novo analisador
#         return controle_analisador.receiver_amplitude(self.visa_analisador)

                    
    def vai_origem(self):
#         if(self.verifica_medicao()):
#             return
        controle_cnc.cnc_jog('$H',self.serial_cnc)
        time.sleep(5)
        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
            time.sleep(0.05)

            

#---------------------------------------Fim da Classe Main Window---------------------------------------------------

       
class Serials(Frame):
    def __init__(self):
        super().__init__()
                      
    def lista_serial(self):
        portas=controle_cnc.list_serial()            
     
        self.cmb_analisador['values'] = portas
        self.cmb_analisador.set('Escolha...')
        
        self.cmb_cnc['values'] = portas
        self.cmb_cnc.set('Escolha...')
        
        self.cmb_gerador['values'] = portas
        self.cmb_gerador.set('Escolha...')
        
    #Função para abrir porta serial do cnc
    def abrir_serial_cnc(self):

#         if (self.verifica_medicao()):
#             return
        com_port =  self.cmb_cnc.get()
        self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc)
        
        if(self.serial_cnc==None):
            self.btn_open_cnc['text'] = 'Abrir'
        else:
            self.btn_open_cnc['text'] = 'Fechar'
            

    def abrir_visa_analisador(self):
#         if (self.verifica_medicao()):
#             return
        com_port =  self.cmb_analisador.get()
        self.visa_analisador=controle_analisador.open_visa_analisador(com_port, self.visa_analisador)
        
        if(self.visa_analisador==None):
            self.btn_open_analisador['text'] = 'Abrir'
        else:
            self.btn_open_analisador['text'] = 'Fechar'
        self.att_freq()

            
    #Função para abrir porta serial do gerador de funções
    def abrir_visa_gerador(self):
#         if (self.verifica_medicao()):
#             return
        com_port =  self.cmb_gerador.get()
        self.visa_gerador=controle_gerador.open_visa_gerador(com_port, self.visa_gerador)
        if(self.visa_gerador==None):
            self.btn_open_gerador['text'] = 'Abrir'
        else:
            self.btn_open_gerador['text'] = 'Fechar'
        self.att_ger()
#---------------------------------------Fim da Classe Serials---------------------------------------------------
class Movimento(Frame):
    def __init__(self):
        super().__init__()
            
    #Função de movimento através do botões de controle
    def ctrl_movimento_cnc(self, direcao):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', self.cmb_step.get())
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            
#             self.txt_log.insert(END, direcao+"  ")
#             self.txt_log.insert(END, str_resposta)
#             self.txt_log.see(END)
            
    #Função de movimento durante medição        
    def meas_movimento_cnc(self, direcao, step):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', str(step))
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
#             self.txt_log.insert(END, direcao+"  ")
#             self.txt_log.insert(END, str_resposta)
#             self.txt_log.see(END)


    def vai_origem(self):
#         if(self.verifica_medicao()):
#             return
        controle_cnc.cnc_jog('$H',self.serial_cnc)
        time.sleep(5)
        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
            time.sleep(0.05)
#---------------------------------------Fim da Classe Movimento---------------------------------------------------

class Tamanho_da_Matriz(Frame):
    
    def __init__(self):
        super().__init__()
         
    def att_matriz(self):
#         if (self.flag_medindo):
#             print("Botão pressionado y="+str(row)+" x="+str(col))
#             messagebox.showwarning(title="Erro Ação impossivel",
#                                    message="Não é possivel realizar está função")
#             return
        
        valor_x = self.var_matriz_x.get()
        valor_y = self.var_matriz_y.get()
        
        #tratamento do valor de entrada
        if (Tamanho_da_Matriz.verifica_string(self,valor_x, 'X e Y') or Tamanho_da_Matriz.verifica_string(self,valor_y, 'X e Y')):
            return
        
        if(int(valor_x)==0 or int(valor_y)==0):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
            return
        
        #destruir tabela existente
        try:
            self.frm_tabela.destroy()
        except AttributeError:
            pass
        else:
            self.frame2.destroy()
            self.canvas.destroy()
            self.buttons_frame.destroy()
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    self.button_matriz[i][j].destroy()
                    
        #//////////////////////////////////////////////////////////////////////////////////
        
        self.frm_tabela = Frame(self.frm_notebook1, relief=RIDGE)
        self.frm_tabela.place(x=460,y=55,width=608,height=590)
        
        # Cria o frame para area dos botões e scrollbar
        self.frame2 = Frame(self.frm_tabela)
        self.frame2.grid(row=3, column=0, sticky=NW)
        
        # Cria area dos botões
        self.canvas = Canvas(self.frame2)
        self.canvas.grid(row=0, column=0)
        
        # Cria scrollbar vertical e anexa a area de botões
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=vsbar.set)
        
        # Cria scrollbar horizontal e anexa a area de botões
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=EW)
        self.canvas.configure(xscrollcommand=hsbar.set)

        # Cria frame que contem os botões
        self.buttons_frame = Frame(self.canvas)
        
        # Cria matriz de botões
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        
        # Adiciona botões no frame
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j] = Button(self.buttons_frame, text="m[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz[i][j].grid(row=i, column=j)
                self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.medir_ponto(var1,var2)
        
        # Cria janela para os botões
        self.canvas.create_window((0,0), window=self.buttons_frame, anchor=NW)

        self.buttons_frame.update_idletasks()  # Needed to make bbox info available.
        bbox = self.canvas.bbox(ALL)  # Get bounding box of canvas with Buttons.

        # Define the scrollable region as entire canvas with only the desired
        # number of rows and columns displayed.
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/int(valor_x)) * self.cols_disp), int((h/int(valor_y)) * self.rows_disp)
        self.canvas.configure(scrollregion=bbox, width=dw, height=dh)
        
        #//////////////////////////////////////////////////////////////////////////////////
                
        self.cols=int(valor_x)
        self.rows=int(valor_y)
        Tamanho_da_Matriz.atualiza_passo(self)

    def atualiza_passo(self):

#         if (self.verifica_medicao()):
#             return
        try:
            #Para o passo do eixo X
            self.var_step_x=abs(self.start_point_x-self.end_point_x)/(int(self.cols)-1)
            self.lbl_par_7.config(text=(("%.4f" % (self.var_step_x)).replace('.',',')))
            #Para o passo do eixo Y
            self.var_step_y=abs(self.start_point_y-self.end_point_y)/(int(self.rows)-1)
            self.lbl_par_8.config(text=(("%.4f" % (self.var_step_y)).replace('.',',')))
        except AttributeError:
            return
        
        #Função se string contem somente numero e maior que zero     
    def verifica_string(self, string, mensagem):
        """Função para verificar se a string contém somente números e se esses números são maior que zero."""
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
        
    #Verifica se string é um numero decimal     
    def verifica_numero(self, string, mensagem):
        """Função para verificar se a string é um número decimal."""
        #Caso número comece com sinal negativo substitui o sinal por '0'
        if(string[0]=='-'):
            string=string.replace('-','0',1)
        if not(string.isdigit()):#verifica se é somente digito
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal'))
            return True
        return False
    
    def abc(self):
        print("abc")


#---------------------------------------Fim da Classe Tamanho da Matriz---------------------------------------------------
        
class Pontos(Frame):
    
    def __init__(self):
        super().__init__()
    
    #Função de definição de ponto 1
    def start_point(self):

#         if (self.verifica_medicao()):
#             return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x, self.start_point_y)).replace('.',',')))
        Tamanho_da_Matriz.atualiza_passo(self)
        
     #Funções de definição de ponto 2
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end

#         if (self.verifica_medicao()):
#             return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x, self.end_point_y)).replace('.',',')))
        Tamanho_da_Matriz.atualiza_passo(self)
        
#---------------------------------------Fim da Classe Pontos---------------------------------------------------
        
class Medicao(Frame):
    
    def __init__(self):
        super().__init__()
        
    #Função para verificar se está medindo     
    def verifica_medicao(self):

        #Caso esteja medindo aparece mensagem de erro.
        if (self.flag_medindo):
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função\ndurante a medição")
            return True
        else:
            return False

    def stop_meas(self):

        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            self.flag_medindo=False

            
    def medicao(self):

        if (Medicao.verifica_medicao(self, )):
            return
        #Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        #de coordenada
        try:
            if(self.start_point_x<self.end_point_x): x = float(self.start_point_x)
            else: x = float(self.end_point_x)
            if(self.start_point_y>self.end_point_y): y = float(self.start_point_y)
            else: y = float(self.end_point_y)
            print("ponto inicial= "+str(x)+' '+str(y))
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Limites não definidos",
                                   message="Pontos não definidos    ")
            return
        
        self.flag_medindo=True
        
        self.var_pb.set(1)
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x= x-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            Movimento.meas_movimento_cnc(self,direcao, abs(x))
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste1")
                time.sleep(0.125)
            
        y= y-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y)) #ARRUMAR com ctrl f
            while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                print("teste2")
                time.sleep(0.125)
                
        self.matrix_meas = [[-80 for _ in range(self.cols)] for _ in range(self.rows)]
        
        var_progressbar=0
        self.max_medido, self.min_medido = -99, 0
        
        self.lbl_par_11['text'] = '-0.00'
        self.lbl_par_12['text'] = '-0.00'
        
        self.var_pb.set(var_progressbar)
        step_progressbar=100/((self.rows)*(self.cols))
        
        self.meas_time = datetime.now()
        flag_ordem=True #false=esquerda pra direita
        for i in range(0, self.rows):#linha
            if(self.flag_stop):
                self.flag_stop = False
                return
            if(flag_ordem):
                for j in range(0, self.cols):#coluna
                    if(self.flag_stop):
                        self.flag_stop = False
                        return
                    self.matrix_meas[i][j]=self.leitura_amplitude()                     
                    if(self.matrix_meas[i][j] > self.max_medido):
                        self.max_medido = self.matrix_meas[i][j]
                        self.lbl_par_11['text'] = str(self.max_medido)
                    if(self.matrix_meas[i][j] < self.min_medido):
                        self.min_medido = self.matrix_meas[i][j]
                        self.lbl_par_12['text'] = str(self.min_medido)
                    self.button_matriz[i][j].config(text="\n"+str(self.matrix_meas[i][j])+" dBm\n")
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    if (i > 0) or (j > 0): #define tempo entre dois pontos 
                        tempo_total = tempo_total - delta_t
                        tempo_total = timedelta(seconds=tempo_total.total_seconds())
                        horas, sobra = divmod(tempo_total.seconds, 3600)
                        minutos, segundos = divmod(sobra, 60)
                        self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))
                    self.master.update()
                    if(j+1<self.cols):
                        self.meas_movimento_cnc(self.dict_jog['right'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                            print("teste3")
                            time.sleep(0.125)
                        if (i == 0) and (j == 0): #define tempo entre dois pontos 
                            delta_t = datetime.now() - self.meas_time
                            tempo_total = (self.rows)*(self.cols)*delta_t
                            tempo_total = timedelta(seconds=tempo_total.total_seconds())
                            horas, sobra = divmod(tempo_total.seconds, 3600)
                            minutos, segundos = divmod(sobra, 60)
                            self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))

                flag_ordem=False
            else:
                for j in reversed(range(0,self.cols)):#coluna
                    if(self.flag_stop):
                        self.flag_stop = False
                        return
                    self.matrix_meas[i][j]=self.leitura_amplitude()
                    if(self.matrix_meas[i][j] > self.max_medido):
                        self.max_medido = self.matrix_meas[i][j]
                        self.lbl_par_11['text'] = str(self.max_medido)
                    elif(self.matrix_meas[i][j] < self.min_medido):
                        self.min_medido = self.matrix_meas[i][j]
                        self.lbl_par_12['text'] = str(self.min_medido)
                    self.button_matriz[i][j].config(text="\n"+str(self.matrix_meas[i][j])+" dBm\n")
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    if (i > 0) or (j > 0): #define tempo entre dois pontos 
                        tempo_total = tempo_total - delta_t
                        tempo_total = timedelta(seconds=tempo_total.total_seconds())
                        horas, sobra = divmod(tempo_total.seconds, 3600)
                        minutos, segundos = divmod(sobra, 60)
                        self.lbl_10.config(text='Tempo estimado de {:02d} : {:02d}: {:02d}'.format(horas, minutos, segundos))
                    self.master.update()
                    if(j!=0):
                        self.meas_movimento_cnc(self.dict_jog['left'], self.var_step_x)
                        while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                            print("teste4")
                            time.sleep(0.125)
                flag_ordem=True
            if(i+1<self.rows):
                self.meas_movimento_cnc(self.dict_jog['down'], self.var_step_y)
                while(controle_cnc.estado_atual(self.serial_cnc)!='Idle'):
                    print("teste5")
                    time.sleep(0.125)
       
        self.flag_medindo=False
    


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
    app = Main_Window()
    root.mainloop()

if __name__ == "__main__":
    main()