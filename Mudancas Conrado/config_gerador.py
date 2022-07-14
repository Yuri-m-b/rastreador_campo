import pyvisa
import time

rm = pyvisa.ResourceManager()
gerador = rm.open_resource('USB::0x0699::0x0346::C037753::INSTR')

gerador.write('OUTPut1:IMPedance 470')
gerador.write('OUTPut1:STATe on')
gerador.write('SOURce1:FREQuency:FIXed 10MHz')
gerador.write('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 10')
print(float(gerador.query('OUTP:IMP?')))
print(gerador.query('*IDN?'))