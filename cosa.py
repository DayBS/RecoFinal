import sys, threading
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot

class Piso:
	def __init__(self):
		self.aulas = []

	def nuevaAula(self, aula):
		self.aulas.append(aula)

	def getAulas(self):
		return self.aulas

class Aula:
	def __init__(self, nombre, x, y, d):
		self.nombre = nombre
		self.estado = "sucio"
		self.x = x
		self.y = y
		self.d = d

	def getDat(self):
		return self.x, self.y, self.d, self.estado, self.nombre

	def limpiar(self):
		self.estado = "limpio"

class Edificio(QMainWindow):

	work_requested = Signal(str)

	def __init__(self):
		super().__init__()


		self.piso = 0
		self.x = 490
		self.y = 560

		self.pisos = []
		piso1 = Piso()
		piso1.nuevaAula(Aula("0a", 0, 200, 200))
		piso1.nuevaAula(Aula("0b", 200, 0, 200))
		piso1.nuevaAula(Aula("0c", 600, 0, 200))
		piso1.nuevaAula(Aula("0d", 800, 200, 200))
		piso2 = Piso()
		piso2.nuevaAula(Aula("1a", 0, 200, 200))
		piso2.nuevaAula(Aula("1b", 200, 0, 200))
		piso2.nuevaAula(Aula("1c", 400, 0, 200))
		piso2.nuevaAula(Aula("1d", 600, 0, 200))
		piso2.nuevaAula(Aula("1e", 800, 200, 200))
		piso3 = Piso()
		piso3.nuevaAula(Aula("2a", 0, 200, 200))
		piso3.nuevaAula(Aula("2b", 400, 0, 200))
		piso3.nuevaAula(Aula("2c", 800, 200, 200))
		piso4 = Piso()
		piso4.nuevaAula(Aula("3a", 0, 200, 200))
		piso4.nuevaAula(Aula("3b", 200, 0, 200))
		piso4.nuevaAula(Aula("3c", 400, 0, 200))
		piso4.nuevaAula(Aula("3d", 600, 0, 200))
		piso4.nuevaAula(Aula("3e", 800, 200, 200))

		self.pisos.append(piso1)
		self.pisos.append(piso2)
		self.pisos.append(piso3)
		self.pisos.append(piso4)

		self.label = QtWidgets.QLabel()
		canvas = QtGui.QPixmap(1000, 600)
		self.label.setPixmap(canvas)
		self.setCentralWidget(self.label)

		self.dibujarPiso()

		self.worker = Lector()
		self.worker_thread = QThread()

		self.worker.accion.connect(self.actualizar)

		self.work_requested.connect(self.worker.leer)

		self.worker.moveToThread(self.worker_thread)

		self.worker_thread.start()

		self.work_requested.emit("")

	def dibujarPiso(self):
		painter = QtGui.QPainter(self.label.pixmap())
		pen = QtGui.QPen()
		pen.setWidth(40)
		pen.setColor(QtGui.QColor('white'))
		painter.setPen(pen)
		painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
		painter.drawRect(0, 0, 1000, 600)

		aulas = self.pisos[self.piso].getAulas()

		font = QtGui.QFont()
		font.setPointSize(45)
		painter.setFont(font)
		pen.setColor(QtGui.QColor('black'))
		painter.setPen(pen)
		painter.drawText(0, 350, 1000, 250, Qt.AlignHCenter, str(self.piso))

		

		painter.end()

		for aula in aulas:
			self.dibujarAula(aula)

		painter = QtGui.QPainter(self.label.pixmap())
		pen.setWidth(20)
		painter.setPen(pen)
		painter.drawRect(self.x, self.y, 20, 20)

	def dibujarAula(self, aula):
		self.update()
		x, y, d, estado, nombre = aula.getDat()
		painter = QtGui.QPainter(self.label.pixmap())
		pen = QtGui.QPen()
		pen.setColor(QtGui.QColor('black'))
		if estado == "sucio":
			painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
		else:
			painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
		pen.setWidth(3)
		painter.setPen(pen)
		painter.drawRect(x, y, d, d)
		font = QtGui.QFont()
		font.setPointSize(15)
		painter.setFont(font)
		painter.drawText(x, y+(d//2), d, d, Qt.AlignHCenter, nombre)
		painter.end()

	def existeEnPiso(self, nom):
		res = False
		for aula in self.pisos[self.piso].aulas:
			if aula.nombre == nom:
				res = True
		return res

	def limpiar(self, nom):
		res = None
		for aula in self.pisos[self.piso].aulas:
			if aula.nombre == nom:
				res = aula
		res.limpiar()
		x1, y1, d, estado, nombre = res.getDat()
		self.x = x1 + d//2 - 10
		self.y = y1 + d//2 - 10

	def resetRobot(self):
		self.x = 490
		self.y = 560

	def actualizar(self, action):
		if action == "subir":
			if self.piso < len(self.pisos) -1:
				self.piso = self.piso + 1
				self.resetRobot()
				self.dibujarPiso()
			else:
				print("mas arriba y te vas con diosito")
		elif action == "bajar":
			if self.piso >= 1:
				self.piso = self.piso - 1
				self.resetRobot()
				self.dibujarPiso()
			else:
				print("ya es toda wey, bajale para arriba")
		elif action[0:8] == "limpiar ":
			nom = action[8:-1]+action[-1]
			if self.existeEnPiso(nom):
				self.limpiar(nom)
				self.dibujarPiso()
			else:
				print("echale mas ganas, ese cuarto no existe en este piso")
		else:
			print("no se que dice pero miente")

class Lector(QObject):
	accion = Signal(str)

	@Slot()
	def leer(self):
		while True:
			x = input()
			self.accion.emit(x)

app = QtWidgets.QApplication(sys.argv)
window = Edificio()
window.show()
app.exec_()