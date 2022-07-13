import pyvisa
import serial

class controle_gerador:      
    
    def imp(imp_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('OUTPut1:IMPedance {}'.format(imp_gerador))
        gerador.write('OUTPut1:STATe On')

    def frequencia(freq_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('SOURce1:FREQuency:FIXed {}'.format(freq_gerador))
    
    def vamp(vamp_gerador):
        rm = pyvisa.ResourceManager()
        gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')
        gerador.write('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {}'.format(vamp_gerador))
    

        
        