from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog

import serial.tools.list_ports
import time
import csv
from datetime import datetime

from cnc_controle import controle_cnc

class main_window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13  # tamanho da tabela
    rows_disp = 10.5  # numero de linhas apresentado
    cols_disp = 7.75 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop = False, False
    tempo_entre_medidas=1 #em segundos
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
    
    def initUI(self):
        #---nome da janela---------------------
        self.master.title('Controle Auto Scan')
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
        #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
        frm_01 = Labelframe(self.frm_notebook1, text='Serial')
        frm_01.place(x=10,y=1,width=440,height=80)
        
        #---configuração da linha/coluna------
        frm_01.columnconfigure(0, pad=3)
        frm_01.columnconfigure(1, pad=3)
        frm_01.rowconfigure(0, pad=3)
        frm_01.rowconfigure(1, pad=3)
        frm_01.rowconfigure(2, pad=3)
        frm_01.rowconfigure(3, pad=3)
        
        #---configuração linha analisador-----
        lbl_01 = Label(frm_01, text='Analisador:')
        lbl_01.grid(row=0, column=0, padx= 3)
        
        self.cmb_analyzer = Combobox(frm_01, width=27)
        self.cmb_analyzer.grid(row=0, column=1, padx= 3)
        
        btn_open_analyzer = Button(frm_01, text='Abrir')
        btn_open_analyzer.grid(row=0, column=2, padx= 3)
        
        #---Atualização de ports-----------
        btn_refresh = Button(frm_01, text='Atualizar')
        btn_refresh.place(x=353,y=1,width=75,height=53)
        btn_refresh['command'] = self.lista_serial
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.grid(row=1, column=0, padx= 3)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.grid(row=1, column=1, padx= 3)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.grid(row=1, column=2, padx= 3)
        self.btn_open_cnc['command'] = self.abrir_serial_cnc
        
        #---nome do frame---------------------
        frm_ctrls = Labelframe(self.frm_notebook1, text='Controle')
        frm_ctrls.place(x=10,y=355,width=440,height=340)
        
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
        btn_home = btn_up = Button(frm_ctrls, text= 'Origem')
        btn_home.place(x=343,y=23,width=70,height=83)
        
        #---configuração linhas------------   
        # Primeira linha
        btn_dig_no = Button(frm_ctrls, text=u'\u25F8')
        btn_dig_no.grid(row=1, column=1)
        
        btn_up = Button(frm_ctrls, text= u'\u25B2')
        btn_up.grid(row=1, column=2)
        btn_up['command'] = lambda direcao=self.dict_jog['up'] : self.ctrl_movimento_cnc(direcao)      
        
        btn_dig_ne = Button(frm_ctrls, text=u'\u25F9')
        btn_dig_ne.grid(row=1, column=3)
        
        btn_z_up_btn = Button(frm_ctrls, text= u'\u25B2')
        btn_z_up_btn.grid(row=1, column=4)
        btn_z_up_btn['command'] = lambda direcao=self.dict_jog['z_up'] : self.ctrl_movimento_cnc(direcao)
        
        # Segunda linha
        btn_left_btn = Button(frm_ctrls, text=u'\u25C0')
        btn_left_btn.grid(row=2, column=1)
        btn_left_btn['command'] = lambda direcao=self.dict_jog['left'] : self.ctrl_movimento_cnc(direcao)
        
        btn_home_btn = Button(frm_ctrls, text=u'\u25EF')
        btn_home_btn.grid(row=2, column=2)
        
        btn_right_btn = Button(frm_ctrls, text=u'\u25B6')
        btn_right_btn.grid(row=2, column=3)
        btn_right_btn['command'] = lambda direcao=self.dict_jog['right'] : self.ctrl_movimento_cnc(direcao)
        
        # Terceira linha       
        btn_diag_so = Button(frm_ctrls, text=u'\u25FA')
        btn_diag_so.grid(row=3, column=1)
        
        btn_down = Button(frm_ctrls, text=u'\u25BC')
        btn_down.grid(row=3, column=2)
        btn_down['command'] = lambda direcao=self.dict_jog['down'] : self.ctrl_movimento_cnc(direcao)
        
        btn_diag_se = Button(frm_ctrls, text=u'\u25FF')
        btn_diag_se.grid(row=3, column=3)
                
        btn_z_down = Button(frm_ctrls, text=u'\u25BC')
        btn_z_down.grid(row=3, column=4)
        btn_z_down['command'] = lambda direcao=self.dict_jog['z_down'] : self.ctrl_movimento_cnc(direcao)

        self.cmb_step = Combobox(frm_ctrls, width=5)# Janela de seleção do tamanho de passo
        self.cmb_step.grid(row=2, column=4)
        self.cmb_step['values'] = ['2','1','0.5','0.1']
        self.cmb_step.current(1)       
        
        lbl_06 = Labelframe(frm_ctrls, text='Log:')
        lbl_06.place(x=10,y=120,width=415,height=170)
                
        self.txt_log = scrolledtext.ScrolledText(lbl_06, width=48, height=9)
        self.txt_log.place(x=1,y=1)
         
        lbl_07 = Label(frm_ctrls, text='Comando:')
        lbl_07.place(x=10,y=295,width=60,height=20)
         
        self.ent_cmd = Entry(frm_ctrls, width=25)
        self.ent_cmd.place(x=80,y=295,width=294,height=20)       
        self.ent_cmd.bind('<Return>', self.comp_s)
         
        self.btn_send_cmd = Button(frm_ctrls, text='Enviar')
        self.btn_send_cmd.place(x=376,y=294,width=50,height=22)  
        self.btn_send_cmd['command'] = self.envia_cmd_cnc
        
        #---nome do frame---------------------
        frm_inic = Labelframe(self.frm_notebook1, text='Tamanho Matriz')
        frm_inic.place(x=10,y=80,width=215,height=75)
        
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
        btn_matriz_refresh['command'] = self.att_matriz
        
        #---nome do frame---------------------
        frm_param = Labelframe(self.frm_notebook1, text='Parametros')
        frm_param.place(x=235,y=80,width=215,height=225)
        
        frm_param.columnconfigure(0, pad=3)
        frm_param.columnconfigure(1, pad=3)
        
        frm_param.rowconfigure(0, pad=3)
        frm_param.rowconfigure(1, pad=3)
        frm_param.rowconfigure(2, pad=3)
        frm_param.rowconfigure(3, pad=3)
        
        lbl_par_1 = Label(frm_param, text='Possição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Possição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (cm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (cm):')
        self.lbl_par_5 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_6 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        
        lbl_par_1.grid(row=0, column=0, sticky=W)
        lbl_par_2.grid(row=1, column=0, sticky=W)
        lbl_par_3.grid(row=2, column=0, sticky=W)
        lbl_par_4.grid(row=3, column=0, sticky=W)
        self.lbl_par_5.grid(row=0, column=1, sticky=E)
        self.lbl_par_6.grid(row=1, column=1, sticky=E)
        self.lbl_par_7.grid(row=2, column=1, sticky=E)
        self.lbl_par_8.grid(row=3, column=1, sticky=E)
        
        #---nome do frame---------------------
        frm_progress = Labelframe(self.frm_notebook1)
        frm_progress.place(x=460,y=650,width=608,height=45)
        
        #---tempo de progresso----------------
        lbl_10 = Label(frm_progress, text='Tempo estimado de '+'HH'+' : '+'MM'+' : '+'SS')
        lbl_10.place(x=10,y=0,width=300,height=20)
        
        #---barra de progresso----------------
        self.var_pb=DoubleVar()
        self.var_pb.set(1)
        
        pb=Progressbar(frm_progress,variable=self.var_pb,maximum=100)
        pb.place(x=200,y=0,width=397,height=20)
        
        #---nome do frame---------------------
        frm_04 = Labelframe(self.frm_notebook1, text='Arquivo')
        frm_04.place(x=460,y=1,width=608,height=47)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        
        lbl_11 = Label(frm_04, text='  Nome do Arquivo:  ')
        lbl_11.grid(row=0, column=0)
        
        self.str_save = Entry(frm_04, width=41)
        self.str_save.grid(row=0, column=1)
        
        lbl_12 = Label(frm_04, text=' _dd-mm-yyyy_HH-MM.xlsx ')
        lbl_12.grid(row=0, column=2)
        
        btn_save = Button(frm_04, text='Salvar')
        btn_save.grid(row=0,column=3)
        btn_save['command'] = self.save
        
        #---nome do frame---------------------
        frm_pont = Labelframe(self.frm_notebook1, text='Definição dos pontos')
        frm_pont.place(x=10,y=155,width=215,height=75)
        
        btn_pont_start = Button(frm_pont, text='Ponto 1')
        btn_pont_start.place(x=5,y=1,width=100,height=50)
        btn_pont_start['command'] = self.start_point
        
        btn_pont_end = Button(frm_pont, text='Ponto 2')
        btn_pont_end.place(x=110,y=1,width=95,height=50)
        btn_pont_end['command'] = self.end_point
        
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
        lbl_08.grid(row=0, column=0)
        
        self.var_freq=Entry(frm_freq, width=12)
        self.var_freq.insert(END, '%d' % 300)
        self.var_freq.grid(row=0, column=1)
        
        self.cmb_freq = Combobox(frm_freq, width=5)
        self.cmb_freq.grid(row=0, column=2)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.place(x=68,y=25,width=136,height=25)
        self.btn_freq_refresh['command'] = self.att_freq
        
        #---botão origem-----------------
        btn_stop = Button(self.frm_notebook1, text='Parar Medição')
        btn_stop.place(x=305,y=310,width=145,height=45)
        btn_stop['command'] = self.stop_meas
        
        self.btn_pause = Button(self.frm_notebook1, text='Pausar Medição')
        self.btn_pause.place(x=157,y=310,width=145,height=45)
        self.btn_pause['command'] = self.pause_meas
        
        btn_start = Button(self.frm_notebook1, text='Iniciar Medição')
        btn_start.place(x=10,y=310,width=145,height=45)
        btn_start['command'] = self.measurement
        
        #-Notebook ed plotagem
        self.frm_notebook2 = Frame(notebook)
        self.frm_notebook2.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook2, text='      Mapa de calor      ')
        
        
        #---constantes e inicializações-------
        self.lista_serial()
        self.att_matriz()
        self.att_freq()
        
    #Função para atualizar lista das portas COM
    def lista_serial(self):        
        portas=controle_cnc.list_serial()
        
        self.cmb_analyzer['values'] = portas
        self.cmb_analyzer.set('Escolha...')
        
        self.cmb_cnc['values'] = portas
        self.cmb_cnc.set('Escolha...')
    
    #Função para abrir porta serial da CNC
    def abrir_serial_cnc(self):
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_cnc.get()
        self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc)
        
        if(self.serial_cnc==None):
            self.btn_open_cnc['text'] = 'Abrir'
        else:
            #forçar conecção
            self.btn_open_cnc['text'] = 'Fechar'
    
    #Função de movimento através do botões de controle
    def ctrl_movimento_cnc(self, direcao):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', self.cmb_step.get())
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
            
    #Função de motivmento durante medição        
    def meas_movimento_cnc(self, direcao, step):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', str(step))
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de envio comandos para serial CNC
    def envia_cmd_cnc(self):
        if (self.serial_cnc != None):
            str_comando=self.ent_cmd.get()
            
            str_resposta=controle_cnc.send_cmd(str_comando, self.serial_cnc)
            
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de evento de "ENTER"       
    def comp_s(self, event):
        self.envia_cmd_cnc()
    
    #Função para verificar se está medindo     
    def verifica_medicao(self):
        #Caso esteja medindo acusa erro e retorna true para if de break
        if (self.flag_medindo):
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função\ndurante a medição")
            return True
        else:
            return False
        
    #Função de definição de ponto 1
    def start_point(self):
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x, self.start_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Funções de definição de ponto 2
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x, self.end_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Função para atualiza passo entre medidas
    def atualiza_passo(self):
        if (self.verifica_medicao()):
            return
        try:
            #Para o passo do eixo X
            self.var_step_x=abs(self.start_point_x-self.end_point_x)/(int(self.cols)-1)
            print("xlinha="+str(self.var_step_x))
            self.lbl_par_7.config(text=(("%.4f" % (self.var_step_x)).replace('.',',')))
            #Para o passo do eixo Y
            self.var_step_y=abs(self.start_point_y-self.end_point_y)/(int(self.rows)-1)
            print("ylinha="+str(self.var_step_y))
            self.lbl_par_8.config(text=(("%.4f" % (self.var_step_y)).replace('.',',')))
        except AttributeError:
            return
    
    #Função de ativação flag de parar medição
    def stop_meas(self):
        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            self.flag_medindo=False
    
    #Função de ativação flag de pausa medição
    def pause_meas(self):
        if(self.flag_medindo):
            if not (self.flag_stop):
                #envia para o arduino parar
                self.flag_stop=True
            else :
                self.btn_pause.config(text=('Continuar'))
                pass # AQUI ENTRA CONTINUAÇÃO DA MEDIÇÃO
    
    #Função para atualziar tamanho da matriz
    def att_matriz(self):
        if (self.flag_medindo):
            print("Botão pressionado y="+str(row)+" x="+str(col))
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função")
            return
        
        valor_x = self.var_matriz_x.get()
        valor_y = self.var_matriz_y.get()
        
        #tratamento do valor de entrada
        if not(valor_x.isdigit() and valor_y.isdigit()):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
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
        self.frm_tabela.place(x=460,y=55,width=608,height=595)
        
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
                self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.meas_ponto(var1,var2)
        
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
        self.atualiza_passo()
    
    #Função de re medição de ponto
    def meas_ponto(self,row,col):
        if (self.verifica_medicao()):
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
        print("Medir ponto x="+str(col)+" y="+str(row))            
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x=x+(self.var_step_x*col)-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            time.sleep(4) #colocar delay
            
        y=y+(self.var_step_y*row)-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            time.sleep(4) #colocar delay
        
        self.flag_medindo=False
    
    #Função comunicação com analisador para definição
    #frequencia de medição
    def att_freq(self):
        if (self.verifica_medicao()):
            return
        
        freq = self.var_freq.get()
        if not (freq.isdigit()):
            messagebox.showwarning(title="Erro nos valor de Frequência",
                                   message="Frequência deve ser um numero decimal maior que zero\n ")
            return
        if(int(freq)==0):
            messagebox.showwarning(title="Erro nos valor de Frequência",
                                   message="Frequência deve ser um numero decimal maior que zero\n ")
            return
        if(self.cmb_freq.get()=="KHz"):
            freq=int(freq)*pow(10, 3)
        elif(self.cmb_freq.get()=="MHz"):
            freq=int(freq)*pow(10, 6)
        else:
            freq=int(freq)*pow(10, 9)
        #AQUI entra Função que manda pro analisador
        print('SYST:MODE RMOD')#Ativa modo reciver
        print("RMOD:FREQ {}.format("+ str(freq) +")")#Define frequencia do modo reciver
        
    #função de medição
    def measurement(self):
        if (self.verifica_medicao()):
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
        
        self.meas_time = datetime.now()
        self.flag_medindo=True
        
        self.var_pb.set(1)
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x= x-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            time.sleep(4) #colocar delay
            
        y=y-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            time.sleep(4) #colocar delay
        
        self.matrix_meas = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        var_progressbar=0
        self.var_pb.set(var_progressbar)
        step_progressbar=100/((self.rows)*(self.cols))
        
        flag_ordem=True #false=esquerda pra direita
        for i in range(0, self.rows):#linha
            if(flag_ordem):
                for j in range(0, self.cols):#coluna
                    if(self.flag_stop):
                        return
                    self.matrix_meas[i][j]=99# entra valor medido
                    self.button_matriz[i][j].config(text="meas+\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print("Mede")
                    if(j+1<self.cols):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['right'], self.var_step_x)
                flag_ordem=False
            else:
                for j in reversed(range(0,self.cols)):#coluna
                    if(self.flag_stop):
                        return
                    self.matrix_meas[i][j]=98# entra valor medido
                    self.button_matriz[i][j].config(text="meas-\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print ("Mede")
                    if(j!=0):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['left'], self.var_step_x)
                flag_ordem=True
            if(i+1<self.rows):
                time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                self.meas_movimento_cnc(self.dict_jog['down'], self.var_step_y)
                
        self.flag_medindo=False
    
    #Função para salvar arquivo com extensão csv
    def save(self):
        try:
            self.meas_time.strftime
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+
                       self.meas_time.strftime("_%d-%m-%Y_%H-%M")+".csv")
            
            #Abrir arquivo csv mode "write"
            file = open(file_path, 'w', newline ='') 

            #Escreve resultado da medida no arquivo csv
            with file:	 
                write = csv.writer(file, delimiter=';') 
                write.writerows(self.matrix_meas) 
            
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Medida não realizada", message="Nenhuma informação para salvar ")
        
def main():
    #---Gera janela-----------------------
    root = Tk()
    root.geometry('1080x720')
    root.resizable(0, 0) 
    #---icone da janela-------------------
    #icone = PhotoImage(file = 'labcem_icone.png') 
    #root.iconphoto(False, icone) 
    #-------------------------------------
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()