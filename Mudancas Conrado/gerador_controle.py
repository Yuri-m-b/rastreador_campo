import pyvisa
import serial

class gerador_controle:
    def open_visa_gerador(com_port, visa_gerador):
        if (visa_gerador == None):
            #retirar numero da COM 
            for i in range (len(com_port)):
                if com_port[i].isnumeric():
                    break
        com_port = com_port[i:int(com_port.find(' -'))]
        #Inicialização da COM
        rm = pyvisa.ResourceManager()
        #Se não tiver uma porta COM compativel instrumento retorna False
        #para apresentação de erro,  falta de drive
        if not any(str(com_port) in i for i in rm.list_resources()):
            return False
        else:
            try:
                my_instrument = rm.open_resource('ASRL'+str(com_port)+'::INSTR')
            except Exception as e:
                print(e)
                my_instrument.close()
                return None
            
    def gerador_frequencia(visa_analisador,freq):
        gerador.write('SOURce1:FREQuency:FIXed 25MHz')
    
    def gerador_impedancia(visa_gerador):
        gerador.write('OUTPut1:IMPedance 470')
        
        
