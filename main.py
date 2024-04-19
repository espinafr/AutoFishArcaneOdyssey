#!env\Scripts\python.exe
import win32gui
import win32ui
import win32api
import win32con
import numpy as np
import cv2
import mss
import math
from operator import add, sub
import keyboard
from time import sleep

######################

sizex = 300
sizey = 250
margemY = 130
corDesejada = (242, 242, 242)#234,135,195)
cps = 9 # clicks por segundo

#######################

appRunning = False
fisgado = False
screenshotData = None

m = [round(win32api.GetSystemMetrics(0)/2-sizex/2), round(win32api.GetSystemMetrics(1)/2-sizey/2-margemY)] # m de meio
notificPos = [930, 1750, 1, 1] # pros pexe

dc = win32gui.GetDC(0) # pega o monitor 0
dcObj = win32ui.CreateDCFromHandle(dc)  # Cria um "device context" do monitor selecionado
hwnd = win32gui.WindowFromPoint((m[0],m[1])) # Pega a janela (programa) que contem esses pixeis específicos
# ^ possivelmente fazer algum jeito de já selecionar o roblox logo aqui

red = win32api.RGB(255, 0, 0) # Red
monitor = (m[0], m[1], m[0]+sizex+1, m[1]+sizey+1)

def drawRectangle() -> None:
    for x in range(sizex):
        win32gui.SetPixel(dc, m[0]+x, m[1], red)
        win32gui.SetPixel(dc, m[0]+x, m[1]+sizey, red)
    for y in range(sizey):
        win32gui.SetPixel(dc, m[0], m[1]+y, red)
        win32gui.SetPixel(dc, m[0]+sizex, m[1]+y, red)
    #win32gui.InvalidateRect(hwnd, monitor, True)

def click(x:int, y:int) -> None:
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def getGameScreenshot(top = m[1]+1, left = m[0]+1, width = sizex-1, height = sizey-1):
    with mss.mss() as sct:
        screenshot = sct.grab({"top": top, "left": left, "width": width, "height": height})
        return screenshot

def checarCor(regiao: tuple, samplingPoints: int = 9) -> list:
    pegarCorDePixel = lambda x, y: screenshotData[y][x] # Função pra pegar a cor na matriz de cores da print
    dimensionalSamplingPoints = samplingPoints**0.5 #Divisão de cada seleção de pixel dentro das margens
    left, upper, right, lower = regiao # Divide as propriedades da regiao nas respectivas variáveis
    yDelta, xDelta = lower - upper, right - left # Pega a distância (variação (delta)) entre os pontos da screenshot (em teoria só precisava do "upper" e "right" na definição seguinte, mas fiz assim porque é mais ''entendivel'')
    yStep, xStep = math.ceil(yDelta / dimensionalSamplingPoints),\
        math.ceil(xDelta / dimensionalSamplingPoints) ## Delta da margem dividido pela quantidade de pontos a serem checados
    somaCoresComponentes = [ 0, 0, 0 ] # Lista com a soma de todas as cores dos pontos checados
    pontosChecados = 0 # Qntd de pontos checados

    for y in range(upper, lower, yStep):
        for x in range(left, right, xStep):
            corDoPixel = pegarCorDePixel(x, y) # chama 🔥
            somaCoresComponentes = list(map(add, somaCoresComponentes, corDoPixel)) # Adiciona à "somaCoresComponentes" a cor do pixel selecionado
            pontosChecados += 1

    return [ somaComponente / pontosChecados for somaComponente in somaCoresComponentes ] # Retorna cada componente dividido pela soma dos totais (uma ''média'')

def verificarMudanca(xQntd = 20, yQntd = 20):
    global fisgado, screenshotData

    margem = 10 # Distancia entre cada checagem de cor
    maximaVariacaoCor  = 35 # Diferença máxima de cor pra ser considerado uma fisgada

    screenshot = getGameScreenshot()
    screenshotData = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2RGB) # Converteu a matriz de cores de blue green red pra red green blue

    restricaoX = lambda x: min(max(x, 0), screenshot.size[0]) # Função para gerar uma margem em volta do pixel mas que sem ultrapasse os limites da imagem
    restricaoY = lambda y: min(max(y, 0), screenshot.size[1])

    left, upper, right, lower = 0, 0, screenshot.size[0], screenshot.size[1]
    yDelta, xDelta = lower - upper, right - left # Pega a distância (variação (delta)) entre os pontos da screenshot (em teoria só precisava do "upper" e "right" na definição seguinte, mas fiz assim porque é mais ''entendivel'')
    yStep, xStep = math.ceil(yDelta / xQntd), math.ceil(xDelta / yQntd) ## A distância de checar um pixel pro outro na screenshot

    for y in range(upper, lower, yStep):
        for x in range(left, right, xStep):
            regiao = [
                restricaoX(x - margem // 2), restricaoY(y - margem // 2), 
                restricaoX(x + margem // 2), restricaoY(y + margem // 2)
            ] # Cria uma região em volta do pixel selecionado
            corRegional = checarCor(regiao) # Lista de cores de pontos definidos dentro das margens do pixel que escolhemos

            DeltaCorObjeto = sum(list(map(abs, list(map(sub, corDesejada, corRegional))))) # Pega mais ou menos a média de o quão parecidas são as cores selecionas com a cor que desejamos
            
            if DeltaCorObjeto <= maximaVariacaoCor:
                fisgado = True

def fish():
    global fisgado, appRunning 
    if fisgado:
        for x in range(cps):
            sleep(1/cps)
            click(x+250, 100) # números aleatórios sla
        if win32gui.GetPixel(dc, 1815, 943) == 65535: # mano nn sei foi tudo a base de teste -- 797
            #sleep(.1)
            #keyboard.send('0')
            #keyboard.press('w')
            #sleep(.4)
            #keyboard.release('w')
            sleep(.1)
            #keyboard.send('0')
            #click(500,500)
            fisgado = False
    else:
        verificarMudanca()

def update():
    global appRunning, fisgado

    sleep(5)
    while True:
        if keyboard.is_pressed("ctrl"):
            appRunning = True if not appRunning else False
            fisgado = False
            print(appRunning)
        
        if appRunning:
            fish()
        else:
            drawRectangle()

def main():
    update()

if __name__ == "__main__":
    main()