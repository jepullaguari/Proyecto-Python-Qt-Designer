import sys
from PyQt5 import uic, QtWidgets
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

from datetime import datetime
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

qtArchivo = "gui/interfaz.ui" # Nombre del archivo aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtArchivo)

class Ui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.obtenerCsv()
        self.indiceCanton() 
        self.setWindowTitle("Dosis de Vacunación")
        self.cmbProvincias.activated.connect(self.cargarCantones) 
       
        self.radioB_dosisT.setChecked(True)
        self.radioB_datosA.setChecked(True)
        
        self.graficarCantonesDosisT()
        # Llamamos a los métodos
        self.radioB_dosisT.clicked.connect(self.selectGraficarDosisT)
        self.radioB_primeraD.clicked.connect(self.selectGraficarDosisT)
        self.radioB_segundaD.clicked.connect(self.selectGraficarDosisT)
        self.radioB_ambasD.clicked.connect(self.selectGraficarDosisT)
        self.radioB_datosA.clicked.connect(self.selectGraficarDosisT)
        self.radioB_datosD.clicked.connect(self.selectGraficarDosisT)
        # Graficar automaticamente
        self.cmbProvincias.activated.connect(self.estadoCmbProvincia)
        self.cmbCantones.activated.connect(self.estadoCmbCanton)
        
        self.sliderPromedio.valueChanged.connect(self.selectGraficarDosisT)

    # Obtenemos nuestra data csv
    def obtenerCsv(self):
        self.df = pd.read_csv('data/vacunasCantones.csv')
        self.data_aux = self.df
        self.grupoProvincias = self.data_aux.groupby(['provincia'])

        listaProvincias = []
        for item in self.grupoProvincias.groups.keys():
            listaProvincias.append(item)
        
        self.cmbProvincias.addItems(list(listaProvincias))
        self.cargarCantones()
    
    # Cargamos los cantones con respecto a cada provincia
    def cargarCantones(self):
        listaCantones = []
        self.cmbCantones.clear()
        provincia_data = self.cmbProvincias.currentText()
        canton = self.data_aux[self.data_aux['provincia'] == provincia_data].groupby('canton')

        for item in canton.groups.keys():
            listaCantones.append(item)
        self.cmbCantones.addItems(list(listaCantones))

    # Verificamos la opción seleccionada y llamamos a los métodos para graficar
    def selectGraficarDosisT(self):
        if self.cmbProvincias.activated and self.radioB_dosisT.isChecked(): 
            self.graficarCantonesDosisT()  
        elif self.cmbProvincias.activated and self.radioB_primeraD.isChecked():
                self.graficarCantonesPrimeraD()
        elif self.cmbProvincias.activated and self.radioB_segundaD.isChecked():
                self.graficarCantonesSegundaD()
        elif self.cmbProvincias.activated and self.radioB_ambasD.isChecked():
                self.graficarCantonesAmbasD()

        self.sliderPromedio.valueChanged.connect(self.actualizarLCD)

    # Graficamos Provincia y cantones por Dosis Total
    def graficarCantonesDosisT(self):
        canton = self.cmbCantones.currentText()
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes1.clear()
        listaDosisCanton = self.idxCanton.loc[[canton],['created_at','dosis_total']]
        x = listaDosisCanton.iloc[:, 0]
        y = listaDosisCanton.iloc[:, 1]

        listFecha = []
        listDosis = []

        for i in range(len(y)):
            listFecha.append(x[i])
            listDosis.append(y[i])
        fecha_dt = self.formatearlistFechas(listFecha)
        
        # Media móvil
        valorSlider = self.obtenerValorSlider()
        media_DTA = listaDosisCanton.iloc[:, 1].rolling(window=valorSlider).mean()
        
        if self.radioB_dosisT.isChecked() and self.radioB_datosA.isChecked():
            self.MplWidget.canvas.axes.plot(fecha_dt, listDosis, 'r', label="Casos")
            self.MplWidget.canvas.axes.set_title("Dosis totales del Cantón " + canton,  size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_DTA, 'r', label="Casos")
                self.MplWidget.canvas.axes.set_title("Dosis totales del Cantón " + canton,  size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        elif self.radioB_dosisT.isChecked() and self.radioB_datosD.isChecked():
            list_dosisD = np.zeros([len(listDosis), 1], dtype=int)
            list_aux = np.zeros([len(listDosis), 1], dtype=int)
        
            for i in range(len(listDosis)):
                if i == 0:
                    list_dosisD[0] = 0
                else:
                    list_aux[i] = (listDosis[i] - listDosis[i - 1])

                    if list_aux[i] < 0:
                        list_dosisD[i] = 0
                    else:
                        list_dosisD[i] = list_aux[i]

            self.MplWidget.canvas.axes.plot(fecha_dt, list_dosisD, 'r', label="Casos")
            self.MplWidget.canvas.axes.set_title("Dosis totales del Cantón " + canton,  size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            df_DosisDiarias = pd.DataFrame(list_dosisD, columns=['dosis_total'])
            media_DTD = df_DosisDiarias.rolling(window=valorSlider).mean()

            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_DTD, 'r', label="Casos")
                self.MplWidget.canvas.axes.set_title("Dosis totales del Cantón " + canton,  size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        self.MplWidget.canvas.draw()
    
    # Graficamos Provincia y cantones por Primera Dosis
    def graficarCantonesPrimeraD(self):
        canton = self.cmbCantones.currentText()          
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes1.clear()
        lista_1DosisCanton = self.idxCanton.loc[[canton],['created_at','primera_dosis']]
        x = lista_1DosisCanton.iloc[:, 0]
        y = lista_1DosisCanton.iloc[:, 1]

        listFecha = []
        listDosis1 = []

        for i in range(len(y)):
            listFecha.append(x[i])
            listDosis1.append(y[i])
        
        fecha_dt = self.formatearlistFechas(listFecha)
        # Media móvil
        valorSlider = self.obtenerValorSlider()
        media_PD = lista_1DosisCanton.iloc[:, 1].rolling(window=valorSlider).mean()

        if self.radioB_primeraD.isChecked() and self.radioB_datosA.isChecked():
            self.MplWidget.canvas.axes.plot(fecha_dt, listDosis1, 'r', label="Casos") # Graficas casos covid
            self.MplWidget.canvas.axes.set_title("Primeras dosis del Cantón " + canton, size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_PD, 'r', label="Casos") # Graficas casos covid
                self.MplWidget.canvas.axes.set_title("Primeras dosis del Cantón " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        elif self.radioB_primeraD.isChecked() and self.radioB_datosD.isChecked():
            list_Prim_Dosis_D = np.zeros([len(listDosis1), 1], dtype=int)
            list_aux = np.zeros([len(listDosis1), 1], dtype=int)

            for i in range(len(listDosis1)):
                if i == 0:
                    list_Prim_Dosis_D[0] = 0
                else:
                    list_aux[i] = (listDosis1[i] - listDosis1[i - 1])

                    if list_aux[i] < 0:
                        list_Prim_Dosis_D[i] = 0
                    else:
                        list_Prim_Dosis_D[i] = list_aux[i]
            
            self.MplWidget.canvas.axes.plot(fecha_dt, list_Prim_Dosis_D, 'r', label="Casos")
            self.MplWidget.canvas.axes.set_title("Primeras dosis del Cantón " + canton, size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            df_PrimeraDosisDiarias = pd.DataFrame(list_Prim_Dosis_D, columns=['primera_dosis'])
            media_PDD = df_PrimeraDosisDiarias.rolling(window=valorSlider).mean()

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_PDD, 'r', label="Casos")
                self.MplWidget.canvas.axes.set_title("Primeras dosis del Cantón " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        self.MplWidget.canvas.draw()

    # Graficamos Provincia y cantones por Segunda Dosis
    def graficarCantonesSegundaD(self):
        canton = self.cmbCantones.currentText()         
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes1.clear()
        lista_2DosisCanton = self.idxCanton.loc[[canton],['created_at','segunda_dosis']]
        x = lista_2DosisCanton.iloc[:, 0]
        y = lista_2DosisCanton.iloc[:, 1]

        listFecha = []
        listDosis2 = []

        for i in range(len(y)):
            listFecha.append(x[i])
            listDosis2.append(y[i])
        fecha_dt = self.formatearlistFechas(listFecha)
        # Media móvil
        valorSlider = self.obtenerValorSlider()
        media_SD = lista_2DosisCanton.iloc[:, 1].rolling(window=valorSlider).mean()
        
        if self.radioB_segundaD.isChecked() and self.radioB_datosA.isChecked():
            self.MplWidget.canvas.axes.plot(fecha_dt, listDosis2, 'r', label="Casos")
            self.MplWidget.canvas.axes.set_title("Segundas dosis del Cantón " + canton, size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))
            
            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_SD, 'r', label="Casos")
                self.MplWidget.canvas.axes.set_title("Segundas dosis del Cantón " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        elif self.radioB_segundaD.isChecked() and self.radioB_datosD.isChecked():
            list_Segun_Dosis_D = np.zeros([len(listDosis2), 1], dtype=int)
            list_aux = np.zeros([len(listDosis2), 1], dtype=int)

            for i in range(len(listDosis2)):
                if i == 0:
                    list_Segun_Dosis_D[0] = 0
                else:
                    list_aux[i] = (listDosis2[i] - listDosis2[i - 1])
                    if list_aux[i] < 0:
                        list_Segun_Dosis_D[i] = 0
                    else:
                        list_Segun_Dosis_D[i] = list_aux[i]

            self.MplWidget.canvas.axes.plot(fecha_dt, list_Segun_Dosis_D, 'r', label="Casos")
            self.MplWidget.canvas.axes.set_title("Segundas dosis del Cantón " + canton, size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            df_SegundaDosisDiarias = pd.DataFrame(list_Segun_Dosis_D, columns=['segunda_dosis'])
            media_SDD = df_SegundaDosisDiarias.rolling(window=valorSlider).mean()

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_SDD, 'r', label="Casos")
                self.MplWidget.canvas.axes.set_title("Segundas dosis del Cantón " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Cantidades", size=12,color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fechas (año/mes)", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        self.MplWidget.canvas.draw()

    # Graficamos Provincia y cantones ambas dosis
    def graficarCantonesAmbasD(self):
        canton = self.cmbCantones.currentText()          
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes1.clear()

        # Obtención de Primera dosis
        lista_1DosisCanton = self.idxCanton.loc[[canton],['created_at','primera_dosis']]
        x1 = lista_1DosisCanton.iloc[:, 0]
        y1 = lista_1DosisCanton.iloc[:, 1]

        # Obtención de Segunda dosis
        lista_2DosisCanton = self.idxCanton.loc[[canton],['created_at','segunda_dosis']]
        x2 = lista_2DosisCanton.iloc[:, 0]
        y2 = lista_2DosisCanton.iloc[:, 1]

        listCanton = []
        listDosis1 = []
        listDosis2 = []

        for i in range(len(y2)):
            listCanton.append(x2[i])
            listDosis2.append(y2[i])
            listDosis1.append(y1[i])

        fecha_dt = self.formatearlistFechas(listCanton)
        valorSlider = self.obtenerValorSlider()

        data_Diarios = pd.DataFrame(listDosis1, columns=['Primera Dosis'])
        data_Acumulados = pd.DataFrame(listDosis2, columns=['Segunda Dosis'])
        
        media_PD = data_Diarios.rolling(window=valorSlider).mean()
        media_SG = data_Acumulados.rolling(window=valorSlider).mean()

        if self.radioB_ambasD.isChecked() and self.radioB_datosA.isChecked():
            self.MplWidget.canvas.axes.plot(fecha_dt, listDosis1, 'r', label="Primera dosis")
            self.MplWidget.canvas.axes1.plot(fecha_dt, listDosis2, 'g' , label="Segunda dosis", linestyle='--',linewidth='2.5')
            self.MplWidget.canvas.axes.set_title("Primera y segunda dosis del cantón " + canton,  size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fecha (año/mes)", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Primera Dosis", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes1.set_ylabel("Segunda Dosis", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_PD, 'r', label="Primera dosis")
                self.MplWidget.canvas.axes1.plot(fecha_dt, media_SG, 'g' , label="Segunda dosis", linestyle='--',linewidth='1.5')
                self.MplWidget.canvas.axes.set_title("Primera y segunda dosis de la provincia " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fecha (año/mes)", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Primera Dosis", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes1.set_ylabel("Segunda Dosis", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        elif self.radioB_ambasD.isChecked() and self.radioB_datosD.isChecked():
            list_Prim_Dosis_D = np.zeros([len(listDosis1), 1], dtype=int)
            list_Segun_Dosis_D = np.zeros([len(listDosis1), 1], dtype=int)

            list_Prim_Dosis_aux = np.zeros([len(listDosis1), 1], dtype=int)
            list_Segun_Dosis_aux = np.zeros([len(listDosis1), 1], dtype=int)

            for i in range(len(listDosis1)):
                if i == 0:
                    list_Prim_Dosis_D[0] = 0
                    list_Segun_Dosis_D[0] = 0
                else:
                    list_Prim_Dosis_aux[i] = (listDosis1[i] - listDosis1[i - 1])
                    list_Segun_Dosis_aux[i] = (listDosis2[i] - listDosis2[i - 1])
                    if list_Prim_Dosis_aux[i] < 0:
                        list_Prim_Dosis_D[i] = 0
                    else:
                        list_Prim_Dosis_D[i] = list_Prim_Dosis_aux[i]
                    if list_Segun_Dosis_aux[i] < 0:
                        list_Segun_Dosis_D[i] = 0
                    else:
                        list_Segun_Dosis_D[i] = list_Segun_Dosis_aux[i]

            self.MplWidget.canvas.axes.plot(fecha_dt, list_Prim_Dosis_D, 'r', label="Primera dosis")
            self.MplWidget.canvas.axes1.plot(fecha_dt, list_Segun_Dosis_D, 'g' , label="Segunda dosis",linewidth='1.5')
            self.MplWidget.canvas.axes.set_title("Primera y segunda dosis del cantón " + canton,  size=14, color='#0B0B61')
            self.MplWidget.canvas.axes.set_xlabel("Fecha (año/mes)", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.set_ylabel("Primera Dosis", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes1.set_ylabel("Segunda Dosis", size=12, color='#0B0B61')
            self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))
            
            df_PrimeraDosisDiarias = pd.DataFrame(list_Prim_Dosis_D, columns=['primera_dosis'])
            df_SegundaDosisDiarias = pd.DataFrame(list_Segun_Dosis_D, columns=['segunda_dosis'])
            media_PDD = df_PrimeraDosisDiarias.rolling(window=valorSlider).mean()
            media_SDD = df_SegundaDosisDiarias.rolling(window=valorSlider).mean()

            # Graficamos media móvil
            if self.sliderPromedio.value() > 1:
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.axes1.clear()
                self.MplWidget.canvas.axes.plot(fecha_dt, media_PDD, 'r', label="Primera dosis")
                self.MplWidget.canvas.axes1.plot(fecha_dt, media_SDD, 'g' , label="Segunda dosis",linewidth='1.5')
                self.MplWidget.canvas.axes.set_title("Primera y segunda dosis de la provincia " + canton, size=14, color='#0B0B61')
                self.MplWidget.canvas.axes.set_xlabel("Fecha (año/mes)", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.set_ylabel("Primera Dosis", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes1.set_ylabel("Segunda Dosis", size=12, color='#0B0B61')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(DateFormatter("%y/%m"))

        self.MplWidget.canvas.draw()

    # Controlamos si existe un cambio en el cmb de provincias y radios Button
    def estadoCmbProvincia(self):
        if self.cmbProvincias.activated and self.radioB_dosisT.isChecked():
            self.graficarCantonesDosisT()
        elif self.cmbProvincias.activated and self.radioB_primeraD.isChecked():
            self.graficarCantonesPrimeraD()
        elif self.cmbProvincias.activated and self.radioB_segundaD.isChecked():
            self.graficarCantonesSegundaD()
        elif self.cmbProvincias.activated and self.radioB_ambasD.isChecked():
            self.graficarCantonesAmbasD()

    # Controlamos si existe un cambio en el cmb de cantones y radios Button
    def estadoCmbCanton(self):
        if self.cmbCantones.activated and self.radioB_dosisT.isChecked():
            self.graficarCantonesDosisT()
        elif self.cmbCantones.activated and self.radioB_primeraD.isChecked():
            self.graficarCantonesPrimeraD()
        elif self.cmbCantones.activated and self.radioB_segundaD.isChecked():
            self.graficarCantonesSegundaD()
        elif self.cmbCantones.activated and self.radioB_ambasD.isChecked():
            self.graficarCantonesAmbasD()
 
    # Limpiamos el combo box de los cantones
    def clearCantones(self):
        self.cmbCantones.clear()
    
    # Establecemos al canton como index
    def indiceCanton(self):
        self.idxCanton = self.data_aux
        self.idxCanton.set_index("canton", inplace=True)
    
    # Actualizamos el valor en el lcd
    def actualizarLCD(self, value):
        self.lcdNumero.display(value)

    # Obtenemos el valor que tenga el slider
    def obtenerValorSlider(self):
        valorActual = self.sliderPromedio.value()
        return valorActual
    
    # Establecemos el formato para las fechas
    def formatearlistFechas(self, listF):
        fecha_dt = [datetime.strptime(date, '%d/%m/%Y') for date in listF]
        return fecha_dt

if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())