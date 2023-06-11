# -*- coding: utf-8 -*-
"""
@author: João Barbosa, Luis Doreste and Rebeca Martinez
"""

# BEFORE RUNNING CODE (done in MAC):
# 1. Download magpy folder (if haven't already)
# 2. Add to PYTHONPATH using... export PYTHONPATH=/Users/Becca/magpy-master/1.1
# 3. echo PYTHONPATH
# 4. pythonw single.py 

################################## Librerías:
from psychopy import gui,visual,event,core, parallel #import all libraries from PsychoPy
from math import cos,sin, atan2,radians,degrees
from random import shuffle, sample
from numpy.linalg import norm
from time import sleep,time
from scipy.stats import circstd
from numpy import *
from cmath import phase
# from matplotlib.pylab import amap
from pylab import *
import numpy as np
import random
import datetime
import random

import sys
import csv
import matplotlib.pyplot as plt
import tobii_research as tr #eyetracker
from psychopy import gui


#import magicpy as mp ############## Descomentar

##### Eye tracker

import tobii_research as tr #eyetracker
import time

found_eyetrackers = tr.find_all_eyetrackers()
my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)

# this function append all the new gaze data to this list since the last callback
global_gaze_data = [] 
def gaze_data_callback(gaze_data):
    global global_gaze_data
    global_gaze_data.append(gaze_data)

global_gaze_data = {}
global_gaze_data['left_pos'] = np.array([np.nan,np.nan])
global_gaze_data['right_pos'] = np.array([np.nan,np.nan])
global_gaze_data['left_pupil'] = np.nan
global_gaze_data['right_pupil'] = np.nan
global_gaze_data['left_pupil_validity'] = np.nan
global_gaze_data['right_pupil_validity'] = np.nan
global_gaze_data['device_time'] = np.nan
global_gaze_data['system_time'] = np.nan

# and then I update the values of the dictionary in the callback function

def gaze_data_callback(gaze_data): # this is a callback function that will return values
    global global_gaze_data
    global_gaze_data['left_pos'] = gaze_data['left_gaze_point_on_display_area']
    global_gaze_data['right_pos'] = gaze_data['right_gaze_point_on_display_area']
    global_gaze_data['left_pupil'] = gaze_data['left_pupil_diameter']
    global_gaze_data['right_pupil'] = gaze_data['right_pupil_diameter']
    global_gaze_data['left_pupil_validity'] = gaze_data['left_pupil_validity']
    global_gaze_data['right_pupil_validity'] = gaze_data['right_pupil_validity']
    global_gaze_data['device_time'] = gaze_data['device_time_stamp']
    global_gaze_data['system_time'] = gaze_data['system_time_stamp']

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

def get_combined_eyes(gdata):
        combined_eyes = {}
        LPos = np.array(gdata['left_pos'])
        RPos = np.array(gdata['right_pos'])
        combined_eyes['EyesPos'] = np.nanmean([LPos,RPos], axis = 0)

        LPup = np.array(gdata['left_pupil'])
        RPup = np.array(gdata['right_pupil'])
        combined_eyes['EyesPup'] = np.nanmean([LPup,RPup], axis = 0)  
        return combined_eyes

EyesPos = np.array([0.0,0.0]) # initialising eye position    
eye_lim = 0.65

tobii = True

################################## Poner los datos preeliminares previamente a través de pantalla:
myDlg = gui.Dlg(title="COMPTE experiment")
myDlg.addText('Subject information')
myDlg.addField('Subject Code:')
myDlg.addField('Starting block:', choices=[1,2,3,4,5,6,7,8])
myDlg.addField('First stimulation side:', choices=["left", "right"])
ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')

code_person = str(ok_data[0])
block_i = int(ok_data[1]-1)
side = str(ok_data[2])

################################## Constantes:
debug_mode = True ##### Cambiar a False antes del pilot
log_on = True
fullscr = False   ##### Cambiar a True antes del pilot

dim_x = 800
dim_y = 800
gaze_on = True
center = [dim_x/2,dim_y/2]
tracker_status = False

# TIMES
#Ambos trabajan a 60 Hz
FIXATION=60  # frames, if 1 frame = 16.7 ms. Equivalent to 1 s. (comprobar como son los frames)
PRESENTATION=15
BLINK_PERIOD=15
RESPONSE_MAX=600 # frames, if 1 frame = 16.7 ms. Equivalent to 10 s.
DELAY=70


# PARTAPORT: marcadores
def marcador(mark):
    parport.setData(0)          #Limpieza previa
    if(mark == 'izq'):          #TMS en la izquierda
        val = 2
    elif(mark == 'dcha'):       #TMS en la derecha
        val = 4
    elif(mark == 'non'):        #NO TMS
        val = 6
    elif(mark == 'cntr'):       #Cuando apretamos en el centro
        val = 8
    elif(mark == 'circun'):     #Cuando presionamos en la circunferencia
        val = 10
    elif(mark == 'est'):        #Aparicion del stimulo
        val = 12
    elif(mark == 'enter'):      #Al presionar para el comienzo de la tasca
        val = 14
    elif(mark == 'reaction'):   #Cuando se mueve el ratón
        val = 16
    #elif(mark == 'inicio'):     #Comienzo de bloque        -> Estos dos inecesarios ya que vemos cuando comienza con izq y dcha
    #    val = 18                                           |
    #elif(mark == 'fin'):        #Final de bloque        <- v
    #    val = 20
    elif(mark == 'comienzo_ensayo'):
        val = 22
    elif(mark == 'fin_ensayo'):
        val = 24
    elif(mark == 'pausa'):      #Si apretamos a la 'p' para poder pausar
        val = 26
    elif(mark == 'reanudar'):   #Cuando reanudamos al pausar de nuevo por 'p'
        val = 28
    elif(mark == 'cambio_bloque'): 
        val = 30
    parport.setData(val)


################################## Set Up:
# SETUP PARALLEL PORT
# adress should be hexadecimal
if not debug_mode:
    port_adress = 16124
    parport = parallel.ParallelPort(port_adress)
    parport.setData(0)

# SETUP DEVICE
# For Magventure
if not debug_mode:
    serial_port_adress = 'COM5'
    magpro = mp.MagVenture(serial_port_adress)     # Initialize the stimulator object
    magpro.connect()
    magpro.arm()     
    magpro.set_amplitude(30)


################################## Pequeñas funciones de utilidad que iremos llamando:

#Guardamos datos hasta dónde se haya llegado
def guardado_csv(filename, arguments_row):
    if log_on:
        with open(filename, 'a', newline='') as csvfile:   #Argumento 'a' es de 'append', por lo que abre fichero sólo para escribir (adjuntando)
            spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(arguments_row)

    
def exit_task(filename, arguments_row): #Termina la tarea
    nome = 'esc_' + filename
    print(nome)
    guardado_csv(nome, arguments_row)
    if not debug_mode:
        magpro.disarm()
        magpro.disconnect()
        parport.setData(0)    
    mywin.close() # Cierra la ventana 'mywin'                                      # eyetracker
    event.clearEvents()
    sys.exit(0) # Termina el programa con un estado de código = 0 (significa correcto)
    
def toCar(r,deg): #Pasamos coordenadas polares a cartesianas
    x=r*cos(radians(deg))  #factor of 1cm==37.795 pixel
    y=r*sin(radians(deg)) 
    return (x,y) #Devuelve la tupla de las coordenadas

def getAngle(v): #Calcula el ángulo (en grados) de un vector 'v' especificado en coordenadas cartesianas
    a=atan2(v[1],v[0])
    b=degrees(a)
    return b

#Function to say "x" message and report time
def say_msg(message,duration,win): #Ponemos 'message' mensaje durante 'duration' tiempo en 'win' ventana
    msgClock=core.Clock() #Crear reloj
    msgText=visual.TextStim(win=win, ori=0, #Win = window in which it will be be drawn
        text=message,
        pos=[0,0], height=30, #1.5,
        color='black',units="pix") #Caracteristicas del mensaje 

    t=0 #Crear variable temporal
    msgClock.reset() #Reiniciar el reloj
    while t<duration: #La accion durara lo que hayamos pasado como duration
        t=msgClock.getTime() #Ir viendo cuanto tiempo a pasado           
        msgText.draw()
        win.flip() #Asegura que salga (flip) el mensaje en la ventana (win) en la proxima recarga de pantalla que tarda muy poco

#Se utiliza para mostrar un mensaje en la pantalla y esperar a que el usuario haga clic con el espaciador antes de continuar
def instr_msg(message,win): 
    msgText=visual.TextStim(win=win, ori=0, #Por lo que muy parecido al anterior, pero sin duración y depende de nosotros
        text=message,
        pos=[0,0], height=30, #1.5,
        color='black',units="pix")

    mouse.clickReset()
    while (not event.getKeys("space")): #Mientras no este apretado el raton se va a enseñar el siguiente mensaje   
        msgText.draw()
        win.flip()
    if not debug_mode:
        marcador("enter") #Marcador de que hemos comenzado apretado el ratón o el espaciador 

# Al continuar decidimos por que bloque continuar
#def contin(ven):
#    cont = False
#    global block_i #Variables que queremos cambiar en el main
#    global trial   #No solo el bloque, sino a demás si empezar en el comienzo de él

#    texto = "Controlando desde la terminal, espere un momento"
#    msgText1=visual.TextStim(win=ven, ori=0, 
#        text=texto,
#        pos=[0,0], height=30, #1.5,
#        color='black',units="pix")
#    msgText1.draw()
#    ven.flip()

#    while(not cont):
#        seguir_igual = input("Desea continuar en el mismo punto en el que estaba? Escribir 'yes' o 'no': ")
#        if(seguir_igual == 'yes'):
#            cont = True
        #En caso de que no queramos continuar exáctamente en el punto donde estábamos:
#        elif(seguir_igual == 'no'):
#            cont2 = False

#            while(not cont2):
#                texto2 = input("Desea empezar por el comienzo de este bloque? Escribir 'yes' o 'no': ")

                #Para continuar justo al principio de el bloque en el cual estábamos:
#                if(texto2 == 'yes'):
#                    trial = 0         #Nos vale por reiniciar por donde íbamos
                    ########## Hay que hacer un guardado csv en este punto
#                    cont2 = True

                #Para continuar al principio de otro bloque distinto:
#                elif(texto2 == 'no'):
#                    cont3 = False

#                    while(not cont3):
#                        bc = int(input("Por qué bloque desea comenzar? Escribir un número del 1-8, siendo 1 el primer bloque y 8 el último: "))
            
#                        if((bc>0)and(bc<9)):
#                            trial = 0        #En este caso debemos de ir al primer trial de dicho bloque
#                            block_i = bc-1   #Y a su vez ir al bloque correspondiente
                            ########## Hay que hacer un guardado csv en este punto
#                            cont3 = True
                        
                        #Comprobación de error:
#                        else:
#                            print("Asegúrese de que el número está entre el 1 y el 8")
#                    cont2 = True
                
                #Comprobación de error:
#                else:
#                    print("Escribir bien 'yes' o 'no'")
#            cont = True

        #Comprobación de error:    
#        else:
#            print("Escribir bien 'yes' o 'no'")
   

#Pausar experimento en caso de algún inconveniente puntual, usar p de pausa para parar y continuar
def pausar(win):
    message = "Experimento pausado, apretar 'p' para continuar"
    msgText=visual.TextStim(win=win, ori=0, #Por lo que muy parecido al anterior, pero sin duración y depende de nosotros
        text=message,
        pos=[0,0], height=30, #1.5,
        color='black',units="pix")
    # Mostramos mensaje
    msgText.draw()
    win.flip()
    # Esperar hasta que apretemos la letra 'p'
    if not debug_mode:
        marcador("pausa")
    pausa = True
    while pausa:
        if 'p' in event.getKeys():
            pausa = False
        msgText.draw()
        time.sleep(0.1)
        win.flip()
    win.flip()
    if not debug_mode:
        marcador("reanudar")
    #Vamos a las distintas opciones que podemos hacer al continuar y para ello llamamos a la función:
    #contin(win)


def len2(x): #Comprobamos que x sea lista o array para ver la longuitud
    if type(x) is not type([]): #Si 'x' no es una lista
        if type(x) is not type(array([])): #Si 'x' no es un array (no se si esta gramatica esta bien)
            return -1
    return len(x)

def phase2(x): #NaN: Not a number. Funcion para calcular la fase de un numero complejo
    if not isnan(x): #Comprueba si no es NaN
        return phase(x)
    return nan

def quit_handler(ven, filename, arguments_row): #Forma para salir del programa con la tecla esc
    for key in event.getKeys():
        if key in ['escape']: 
            exit_task(filename, arguments_row)
        elif key in ['p']: 
            pausar(ven)


def is_fix(fixated): #No entiendo que realiza esta funcion de utilidad
    return 1

def routines(ven, filename, arguments_row):              # Básicamente se llama para conseguir una serie de acciones
    quit_handler(ven, filename, arguments_row)       # Llama a la funcion con la que se podría salir con el escape o pausar con 'p'
    fixation.draw()          # Fija en un punto
    mywin.update()           # 'Re'carga la pantalla
    x_m,y_m=mouse.getPos()   # Valores 'x' e 'y' del raton obtenidos
        

# tracker


################################### Crear csv file:

subject_name = datetime.datetime.now().strftime('%d%m%Y%H%M') + '_' + code_person #Concatenacion tiempo + código persona

filename = subject_name + '.csv' # Fichero .csv en el cual guardaremos los datos
tmsfilename = subject_name + 'tms.csv'

cnames = ['trial','block','condition','TMS_trial', # Guardaremos los datos columnas de datos
           'delay','fixated','R','T_Angle',
           'choice_x','choice_y','choiceAngle','choiceR',
           'RT','MT',
           'ts_b','ts_f','ts_p','ts_d','ts_r','ts_e',
           'm_pos_x','m_pos_y','m_clock','RMT',"TMS stat",'ts_tms']


if log_on: 
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile: # Creamos fichero nuevo en el con el filename descrito anteriormente, modo escritura y dos argumentos que describen el formato
            spamwriter = csv.writer(csvfile, delimiter=';', # Escribimos, y de que forma, lo que acabamos de desclarar
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(cnames)  #Vamos escribiendo en el fichero filas y pasamos los argumentos de la lista descritos con anterioridad



################################### Tecnicismos de visualización
mywin = visual.Window([dim_x,dim_y],monitor="testMonitor", fullscr=fullscr, units="cm",color="white", screen=0) #Describimos nuestra ventana

fix_area=400
radius = 8
fixation_gauss = visual.PatchStim(win=mywin, mask='gauss', size=1, pos=[0,0], sf=0, color='black',units='cm') # El circulo que siempre esta al centro
fixation_square = visual.PatchStim(win=mywin, size=1, pos=[0,0], sf=0, color='black',units='cm') # Cuadrado central mientras esperamos
cursor = visual.PatchStim(win=mywin, size=1, pos=[0,0], sf=0, color='black',units='cm') # El cursor fijado en el cuadrado de la línea anterior
resp = visual.Circle(mywin,radius=0.7,pos=[0,0],fillColor='red',units='cm') # Rojo cuando vamos a buscar la respuesta visual

ex1=visual.Circle(mywin,radius=28.4,lineColor='black',fillColor='black',pos=toCar(10,340),units='pix') # Para representar los estímulos visuales circulares
ex2=visual.Circle(mywin,radius=15,lineColor='black',fillColor='black',pos=toCar(3,340),units='pix')

mywin.monitor.setSizePix((dim_x,dim_y)) # Crea las dimensaiones de la pantalla (x e y tienen 800 pixeles cada)
circ = visual.Circle(mywin, radius=radius, pos=[0,0], lineColor='black',units='cm', edges=128) # La circunferencia en la cual se mostraran los estimulos
circ.setFillColor(mywin.color)

mouse=event.Mouse(win=mywin,visible=False) # Que no se vea el raton


################################### Text strings :
### Instrucciones que leemos al paciente:
instr1="Bienvenido/a a nuestro experimento de memoria!"
instr2="En este experimento vamos a medir tu capacidad de recordar posiciones en el espacio. En la pantalla veras un circulo que aparecera brevemente. Tienes que recordar la ubicacion de circulo puesto que necesitaras esa informacion mas adelante."

instr3="En el centro de la pantalla habra un punto de fijacion negro. Es muy importante que siempre mires a este punto, incluso cuando aparece el circulo en la pantalla."
instr4="El circulo desaparecera y un otro circulo aparecera sobre el punto de fijacion. En ese momento debes empezar a mover el raton y marcar con un clic el punto donde recuerdas que se presento el circulo."
instr5="Por favor, empieza a mover el raton de inmediato tras el cambio del punto de fijacion, ya que tienes solo 3 segundos para responder."

instr6="Tienes alguna pregunta?"
instr7="Por favor, trata de marcar las posiciones recordadas con la mayor precision posible! Se te dara informacion sobre tu rendimiento en la tarea al cabo de 5 minutos."
instr8="Para pausar el experimento, apretar 'p'. Para salir de él, pulsar 'esc'."

instr9="Comenzaremos por una pequeña prueba inicial para entender como realizar el experimento"
instr10="Perfecto! Ahora ya comenzaremos con el experimento"


################################### Generación de estímulo:
# Localidades: Right Dorsolateral Prefrontal Cortex, Left Dorsolateral Prefrontal Cortex
RMT = 45 # Resting Motor Threshold

LOCS_R = ['R', 'R', 'R', 'R']   #P. R -> Right Dorsolateral Prefrontal Cortex. Cambio de 2 a 4
LOCS_L = ['L', 'L', 'L', 'L']   #V. L -> Left Dorsolateral Prefrontal Cortex

#Queremos 8 bloques, 4 por cada hemisferio
LOCS = LOCS_R + LOCS_L #['R','R','R','R','L','L','L','L']
n_locations = len(LOCS) #Mas facil hubiese sido poner 4 y ya


n_locations_R=len(LOCS_R) 
n_locations_L=len(LOCS_L) 

int_R = [0, 0.7] # Modificado ya que solo utilizamos dos intensidades: real y sin intensidad
int_L = [0, 0.7]

n_int_R = len(int_R)
n_int_L = len(int_L)

n_trials_block_R= 100 # 100 trials por bloque; 8 bloques (4 por hemisferio); 800 trials totales
n_trials_block_L= 100


angles_per_loc_R = array([np.random.rand(int(n_trials_block_R/n_int_R))*360 for _ in range(n_locations_R)]) #Crea un array de numeros [0, 360), total numeros por el int()
angles_per_loc_L = angles_per_loc_R.copy()

#Para la prueba inicial:
angles_per_prueba_inicial = angles_per_loc_R.copy()
random.shuffle(angles_per_prueba_inicial)
angles_per_prueba_inicial = angles_per_prueba_inicial[0][0:5]

angles_R = column_stack([angles_per_loc_R,angles_per_loc_R]) #Apilamos conjuntamente los angulos (2 veces para los de 0 y los de 0.7)
angles_L = column_stack([angles_per_loc_L,angles_per_loc_L])

tms_in_R = column_stack([zeros(shape(angles_per_loc_R)),int_R[1]*ones(shape(angles_per_loc_R))]) #shape()->dim. Tenemos la cantidad de 0 y de 1, los cuales dispararemos
tms_in_L = column_stack([zeros(shape(angles_per_loc_L)),int_L[1]*ones(shape(angles_per_loc_L))]) #Comprobar que los cambios estan bien, cambiado int_L por int_P, quitado un tercero en tms_in_R y quitado un exponencial

angles = list(angles_R)
angles_Left = list(angles_L)
[angles.append(l) for l in angles_Left] #Lista de angulos concatenando los de R y L

tms_in = list(tms_in_R)
tms_in_Left = list(tms_in_L)
[tms_in.append(l) for l in tms_in_Left] #Lista de los tms totales

prec_angle=[]

################################### Definiciones para poder ir guardando en cualquier momento:

#### Inicializamos las variables para poder guardar en cualquier momento:
n_trial = n_izquierda = n_derecha = LOC = tms_trial = r_T = angle_T = choice_ang = choice_r = rtime = mtime = ts_b = ts_f = ts_p = ts_d = ts_r = ts_e = tms_stat = ts_tms = 0
choice_pos = [0, 0]
m_pos_x=[]
m_pos_y=[]
m_clock=[]
fixx=1

arguments_row = [n_trial,block_i,LOC,tms_trial,DELAY,fixx,r_T,angle_T,choice_pos[0],choice_pos[1],choice_ang,choice_r,rtime,mtime,ts_b,ts_f,ts_p,ts_d,ts_r,ts_e,m_pos_x,m_pos_y,m_clock,RMT,tms_stat,ts_tms]


##################################### ################################### ################################### #################################
#                                                          Prueba de reconomimiento                                                           # 

# Realizaremos una prueba mostrando de forma aleatoria 5 ángulos previo al experimento, sin registrar ningún dato, para así poder darle a entender
# al paciente como se realiza el experimento.
# Quitamos los tiempos de espera máximos para que así el paciente se familiarice con el experimento y tenga tiempo de ver cómo funciona.

#### Mostramos las distintas instrucciones previas:
instr_msg(instr1, mywin)
instr_msg(instr2, mywin)
instr_msg(instr3, mywin)
instr_msg(instr4, mywin)
instr_msg(instr5, mywin)
instr_msg(instr6, mywin)
instr_msg(instr7, mywin)
instr_msg(instr8, mywin)

#### Pequeña prueba sin estimulación previa para que el paciente entienda como va el experimento:
instr_msg(instr9, mywin)
if not debug_mode:
    marcador("comienzo_ensayo")

# Los 5 ángulos los hemos creado en la sección anterior
for alfa in angles_per_prueba_inicial:
    angle,r = alfa,radius
    x,y=toCar(r,angle)
    
    # Define stimulus: definimos un circulo negro en la coordenada oportuna
    stim = visual.Circle(mywin,radius=1,lineColor="black",fillColor="black",pos=[x,y],units='cm')
    fixation = fixation_gauss
    routines(mywin, filename, arguments_row)
    mouse.clickReset() #Resetea el estado interno del raton

    while not ( abs(x) < 2 and abs(y) < 2): #Espera hasta que estemos en el centro
        quit_handler(mywin, filename, arguments_row)
        x,y=gpos=mouse.getPos()
        cursor.setPos(gpos, operation='', log=None)                                        
        cursor.draw() 
        routines(mywin, filename, arguments_row)
    
    # Ultimaos la preparacion del nuevo trial
    mouse.setPos([0,0]) #Establece la posición del cursor del ratón en el origen     
    fixation = fixation_square
    fixation.setColor('black')
    t=0		            
    routines(mywin, filename, arguments_row)

    for frameN in range(int(FIXATION/2)): #Fijamos durante int() tiempo (30 frames=500ms=0,5s)
        routines(mywin, filename, arguments_row)
    sleep(.1) # give 100ms for the subject to refixate

    for frameN in range(PRESENTATION): #Tiempo de presentacion del estimulo visual
        stim.draw()
        routines(mywin, filename, arguments_row)
    
    for frameN in range(DELAY): #Tiempo de delay (lo usamos?)
        routines(mywin, filename, arguments_row)

    #Dibujar o no el estímulo y reiniciar ciertos valores:         
    mouse.setPos((0,0)) #Establece la posición del cursor del raton en las coordenadas (0,0)
    pos = mouse.getPos() #Guardamos la posicion del raton
    resp.setFillColor("red") #Ponemos en rojo el objeto que se va moviendo en el cursor
    resp.setPos(pos) #Establece la posicion del elemento de respuesta en la posicion actual del cursor del raton
    fixation = fixation_gauss #Ponemos la forma gausiana en el centro
    event.clearEvents()
    fixation.setColor("black")

    if DELAY == 0: #Decidir si dibujar el estimulo o no
        stim.draw()
    else:
        pass
    routines(mywin, filename, arguments_row)

    #Si se mueve de cierta distancia del centro
    x,y = mouse.getPos()
    rad=0
    while ( abs(x) < 1 and abs(y) < 1): 
        circ.draw()
        if DELAY == 0:
            stim.draw()
        x,y=pos = mouse.getPos()
        resp.setPos(pos)
        resp.draw()
        routines(mywin, filename, arguments_row) #Se llama en cada iteración para actualizar la pantalla
        pass
    
    while (mouse.getPressed()[0]==0): 
        circ.draw()
        x,y=pos=mouse.getPos() #Recogida de datos de la posición x e y del cursor
        resp.setPos(pos)
        resp.draw()
        routines(mywin, filename, arguments_row) #Refrescamos pantalla
        pass

    resp.setPos(pos)
    resp.setFillColor('white')
    resp.draw()


mywin.flip()
if not debug_mode:
    marcador("fin_ensayo")
instr_msg(instr10, mywin)





##################################### ################################### ################################### ################################# 
#################################### ################################### ################################### ################################## 
################################### ################################### ################################### ################################### 
#                                                          COMENZAMOS EL EXPERIMENTO                                                          #                                                                                                                           


################################### Definiciones previas a comenzar:
#Creamos distintos relojes que nos servirán para poder seguir el tiempo de distintos eventos durante el experimento:
responseClock = core.Clock() #Tiempo entre la presentacion de un estimulo y lo que se tarda en responder
blockClock = core.Clock() #Tiempo de un block entero de trials
trialClock = core.Clock() #Tiempo en el trial, lo vamos actualizando para cada necesidad temporal
totalClock = core.Clock() #Tiempo de la duracion total del experimento
blink_counter = core.Clock() #La frecuencia de pestañeos durante el experimento. Necesario?


################################### Comenzamos el bloque:      

#This has to be set beforehand, reading from a file is best idea.
#shuffle(blocks)

all_trials_idx = [] #Vamos metiendo todos los trials que se van a hacer aquí

for i in range(n_locations_R):
    all_trials_idx+=[range(shape(tms_in_R)[1])]

for i in range(n_locations_L):
    all_trials_idx+=[range(shape(tms_in_L)[1])]


#Orden con el que se hace el experimento por lado:
if(side == 'left'):
    blocks=[4,0,5,1,6,2,7,3] # Session 2 LRLRLRLR
elif(side == 'right'):
    blocks=[0,4,1,5,2,6,3,7]
# Right -> 0-3; Left -> 4-7


#### Comenzamos el bloque propiamente dicho:
#Para poder elegir en que bloque estamos, debemos de cambiar el for por un while y crear una variable de routines para que devuelva valor
while(block_i<n_locations):
#for block_i in range(n_locations): #Al principio de cada bloque hacemos una serie de reajustes:
    block = blocks[block_i] #Pillamos el número de bloque que queremos
    block_i += 1 #Para la siguiente iteración
    #Hay que indicar si es lado izquierdo o derecho:
    if not debug_mode:
        if(block <= 3):
            marcador("dcha")
        else:
            marcador("izq")
    LOC=LOCS[block] #Vemos si este bloque está en izq o drcha
    trials_idx = list(all_trials_idx[block]) # I am turning the range into a list...
    n_trials_block = len(trials_idx) #Supongo que esto debería de ser cte ya que haremos el mismo numero de trials siempre
    totalClock.reset()
    blink_counter.reset()
    prec_angle=[]
    
    # shuffle TMS / NO TMS. Importante mezclar cuando disparamos y cuando no:
    shuffle(trials_idx)
    angles_block=angles[block][trials_idx]
    tms_block = tms_in[block][trials_idx]

################################### Comenzamos el trial:
    print(block_i)
    first_block= "Beginning of block: %i" % block_i
    instr_msg(first_block, mywin)

    for trial in range(n_trials_block): #El for itera por todos los trials del bloque
        tms_trial = tms_block[trial] #Vemos que intensidad se usa, si 0 o con la intensidad.
        if not debug_mode:
            magpro.set_amplitude(int(tms_trial*RMT)) #Ajustamos la intensidad

        if(block <= 3):
            n_derecha += 1
        else:
            n_izquierda += 1
        
        #Mera compruebación:
        print("Nº trials lado derecho:   ", n_derecha)
        print("Nº trials lado izquierdo: ", n_izquierda)
        print("Nº trials del bloque:     ", trial+1)
        print("Nº del bloque:            ", block_i)

        n_trial=n_trial+1 #Como la indexacion comienza en 0, le añadimos uno para guardar (se podria poner mas cerca de dicha localizacion)
       
        angle,r = angles_block[trial],radius
        x,y=toCar(r,angle) #Calculamos las coordinadas del trial a partir de los valores del angulo y 'r'

        # Define stimulus: definimos un circulo negro en la coordenada oportuna
        stim = visual.Circle(mywin,radius=1,lineColor="black",fillColor="black",pos=[x,y],units='cm')
        ts_b = time.time() #Guarda el tiempo actual
        #tracker.log("SYNC PERIOD")                                               # eyetracker
        fixation = fixation_gauss
        routines(mywin, filename, arguments_row)
        mouse.clickReset() #Resetea el estado interno del raton
        
        x,y=mouse.getPos()  
        while not ( abs(x) < 2 and abs(y) < 2): #Espera hasta que estemos en el centro
            quit_handler(mywin, filename, arguments_row)
            x,y=gpos=mouse.getPos()
            cursor.setPos(gpos, operation='', log=None)                                        
            cursor.draw() 
            routines(mywin, filename, arguments_row)
        
        # Ultimaos la preparacion del nuevo trial
        if not debug_mode:
            marcador("cntr")
        mouse.setPos([0,0]) #Establece la posición del cursor del ratón en el origen     
        fixation = fixation_square
        fixation.setColor('black')
        if not debug_mode:
            parport.setData(55) #Marcador de que comienza un nuevo trial
        t=0		            
        trialClock.reset() #Reseteamos el contador de trial
        routines(mywin, filename, arguments_row)

        #tracker.log("FIXATION PERIOD")                                         # eyetracker
        t=0
        trialClock.reset()
        ts_f = time.time() #Pillamos el tiempo en el que se fija

        for frameN in range(int(FIXATION/2)): #Fijamos durante int() tiempo (30 frames=500ms=0,5s)
            routines(mywin, filename, arguments_row)
            if tobii:
                eyepos = []
                Eyes =  get_combined_eyes(global_gaze_data)
                eyepos.append(Eyes['EyesPos']) #
                if len(eyepos) > 500:
                    lastpos = eyepos[-30:]
                    EyesPos = np.nanmean(lastpos, axis=0)
                    #print(EyesPos) # with this you can visualize the eye position
                    if np.isnan(EyesPos[0]):  EyesPos = np.array([0.0,0.0])
                if EyesPos[0] >  eye_lim or EyesPos[0] < 1-eye_lim or EyesPos[1] >  eye_lim or EyesPos[1] < 1-eye_lim:
                    print("NOT FIXATING!!")


        #myMagstim.poke(silent=False)
        sleep(.1) # give 100ms for the subject to refixate


################################### Impulso TMS: 
        ts_tms=time.time() #Pillamos el tiempo en el que se estimula

        tms_stat = 0 #Nos dira si hubo pulso o no (estado de TMS en este trial)
        if tms_trial > 0: #Recrodamos que en la indentacion 0 = no pulse, por lo que miramos si habra o no pulso TMS
           if not debug_mode:
              parport.setData(0) #Indica pulso de TMS (se pone en 0 ya que sobre escribe)
              out_put = magpro.fire() #Dispara pulso
              tms_stat = out_put[0] #Se actualiza dicho estado
        else:
            if not debug_mode:
                parport.setData(88) #Indica que no se envio pulso de TMS
        routines(mywin, filename, arguments_row)
        
              #tracker.log("PRESENTATION PERIOD")                                    # eyetracker
        

################################### Espera de tiempos correspondientes:  
        t=0
        trialClock.reset()
        ts_p = time.time() #Pillamos el tiempo en el que se estimula
        for frameN in range(PRESENTATION): #Tiempo de presentacion del estimulo visual
            stim.draw()
            routines(mywin, filename, arguments_row)
       
        #tracker.log("DELAY PERIOD")                                              # eyetracker
        t=0
        trialClock.reset()
        ts_d=time.time() #Pillamos el tiempo en el que hay delay
        for frameN in range(DELAY): #Tiempo de delay (lo usamos?)
            #sleep(frameN)
            routines(mywin, filename, arguments_row)
            if tobii:
                eyepos = []
                Eyes =  get_combined_eyes(global_gaze_data)
                eyepos.append(Eyes['EyesPos']) #
                if len(eyepos) > 500:
                    lastpos = eyepos[-30:]
                    EyesPos = np.nanmean(lastpos, axis=0)
                    #print(EyesPos) # with this you can visualize the eye position
                    if np.isnan(EyesPos[0]):  EyesPos = np.array([0.0,0.0])
                if EyesPos[0] >  eye_lim or EyesPos[0] < 1-eye_lim or EyesPos[1] >  eye_lim or EyesPos[1] < 1-eye_lim:
                    print("NOT FIXATING!!")
      
        #tracker.log("RESPONSE PERIOD")                                          # eyetracker
        
        
################################### Dibujar o no el estímulo y reiniciar ciertos valores:         
        mouse.setPos((0,0)) #Establece la posición del cursor del raton en las coordenadas (0,0)
        pos = mouse.getPos() #Guardamos la posicion del raton
        resp.setFillColor("red") #Ponemos en rojo el objeto que se va moviendo en el cursor
        resp.setPos(pos) #Establece la posicion del elemento de respuesta en la posicion actual del cursor del raton
        fixation = fixation_gauss #Ponemos la forma gausiana en el centro
        choice_trial=0
        event.clearEvents()
        fixation.setColor("black")

        if DELAY == 0: #Decidir si dibujar el estimulo o no
            stim.draw()
            if not debug_mode:
                marcador("est")
        else:
            pass
        routines(mywin, filename, arguments_row)
        
        #Iremos poniendo en la lista los valores de las coordenadas y del reloj
        m_pos_x=[]
        m_pos_y=[]
        m_clock=[]
        
        responseClock.reset()
        trialClock.reset() #Reseteamos para ver los distintos tiempos mas adelante
        ts_r = time.time() #Pillamos el tiempo en el que hay response

        print("DELAY = %.2f s" % (ts_d - ts_r)) #Delay - Response


        ### REACTION TIME
        #Medimos el tiempo que tardamos en reaccionar. O pasamos del tiempo máximo permitido, o se mueve de cierta distancia del centro
        x,y = mouse.getPos()
        rad=0
        while ( abs(x) < 1 and abs(y) < 1 and frameN in range(RESPONSE_MAX)): 
            circ.draw()
            if DELAY == 0:
                stim.draw()
                if not debug_mode:
                    marcador("est")
            else:
                pass
            x,y=pos = mouse.getPos()
            resp.setPos(pos)
            resp.draw()
            routines(mywin, filename, arguments_row) #Se llama en cada iteración para actualizar la pantalla
            pass
        #Marcador de que hubo respuesta:
        if not debug_mode:
            if(abs(x) > 1 or abs(y) > 1):
                marcador("reaction")
        #Guardamos el tiempo de reacción:
        rtime = trialClock.getTime()
        
        ### MOVEMENTE TIME
        #Vemos el tiempo que estamos moviendo el cursor: hasta que pasa el tiempo máximo o se aprieta el cursor.
        trialClock.reset()
        #keep waiting for the release
        #Vamos cogiendo informacion de la w, y y del tiempo desde que sale del centro hasta que pulsamos
        while (mouse.getPressed()[0]==0 and frameN in range(RESPONSE_MAX)): 
            circ.draw()
            x,y=pos=mouse.getPos() #Recogida de datos de la posición x e y del cursor
            resp.setPos(pos)
            t=trialClock.getTime() #Recogida de datos del tiempo
            resp.draw()
            m_pos_x.append(x) #Guardamos datos recogidos en listas
            m_pos_y.append(y)
            m_clock.append(t)
            routines(mywin, filename, arguments_row) #Refrescamos pantalla
            pass
        
        rep_pos=pos #Aquí guardamos la posición final del cursor
        #Lo que hacemos es calcular el ángulo y el rado con respecto al centro:
        angle_T,r_T =  angle,r 
        ts_e = time.time()                 #END TIME: tiempo total (reaction+movement)                  
        mtime = trialClock.getTime()       #MOVEMENT TIME: tiempo de movimiento 
        

        #Comprobamos si el ratón está pulsado (y que no sea que se pasó el tiempo máximo).
        if mouse.getPressed()[0]==1:                       #En caso de que lo esté:
            if not debug_mode:
                marcador("circun")                                  #Marcador
            choice_pos=rep_pos                             #Guardamos la posición del ratón donde esté pulsado
            choice_ang= float("%.2f" % getAngle(rep_pos))  #El ángulo de la posición con respecto al origen (redondeado a los 2 decimales)
            choice_r=float("%.2f" % (norm(rep_pos)))       #La distancia con respecto al origen (redondeado a los 2 decimales)
            err_ang= angle_T- choice_ang                   #El error con respecto al ángulo, y debajo con respecto a la distancia
            err_r=float("%.2f" % (r-(choice_r)))# -*- coding: utf-8 -*-
        else: #Si no está apretado es que se pasó el tiempo máximo y rellenamos todo con NaN
            choice_pos=array([np.nan,np.nan])
            choice_ang=np.nan  
            choice_r=np.nan
            err_ang=np.nan
            err_r=np.nan

        if err_ang>180:  #Formalidad para trabajar con lo ángulos y tener resultados útiles:
            err_ang=err_ang-360
    
        prec_angle.append(err_ang)   

        #Guardamos todo en fichero csv
        arguments_row = [n_trial,block_i,LOC,tms_trial,DELAY,fixx,r_T,angle_T,choice_pos[0],choice_pos[1],choice_ang,choice_r,rtime,mtime,ts_b,ts_f,ts_p,ts_d,ts_r,ts_e,m_pos_x,m_pos_y,m_clock,RMT,tms_stat,ts_tms]
        guardado_csv(filename, arguments_row)

        #Dibujamos en blanco el cursor en donde hemos apretado la respuesta:
        resp.setPos(pos)
        resp.setFillColor('white')
        resp.draw()


################################### Finaliza el trial
    #Convertimos los ángulos a numpy array y quitamos los NaN                 
    prec_angle=np.array(prec_angle)                           
    prec_angle= prec_angle[~np.isnan(prec_angle)]                           
    abs_err = np.mean(abs(prec_angle)) #Calculamos el error absoluto

    mywin.flip()

    if abs_err <4: #Comentamos como les ha ido en funcion a este error:
        say_msg('Muy bien! Tu precisión en este bloque ha sido muy alta',5,mywin)
    if abs_err>=4 and abs_err<10:
        say_msg('Muy bien! Tu precisión en este bloque ha sido alta',5,mywin)
    if abs_err>=10 and abs_err<20:
        say_msg('Muchas gracias, tu precisión en este bloque ha sido media',5,mywin)
    if abs_err>20:
        say_msg('Muchas gracias. Por favor, intenta de contestar con mayor precisión.',5,mywin)
   

# myMagstim.disarm(receipt=False)
# myMagstim.disconnect()


my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)


################################### Cuando no estamos en 'debug' hay que poner los parámetros necesarios en el equipamiento: 
if not debug_mode:
    magpro.disarm()
    magpro.disconnect()
    parport.setData(0)

################################### Clean up para finalizar: 
event.clearEvents()
exit_task(filename, arguments_row)
