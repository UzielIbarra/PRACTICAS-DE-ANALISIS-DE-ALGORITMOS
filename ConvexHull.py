
import csv
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.figure import Figure
import os
import tkinter as tk
from tkinter import filedialog, messagebox

Point = Tuple[float, float]


def leer_puntos_csv(ruta_csv: str) -> List[Point]:
    """Lee un CSV con encabezados x,y y regresa una lista de tuplas (x,y)."""
    puntos: List[Point] = []
    with open(ruta_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            x = float(row["x"])
            y = float(row["y"])
            puntos.append((x, y))
    return puntos


def punto_mas_izquierdo(puntos: List[Point]) -> int:
    """
    Regresa el índice del punto más a la izquierda.
    En empate de x, escoger el de menor y (para hacerlo determinista).
    """
    idx = 0
    for i in range(1, len(puntos)):
        if puntos[i][0] < puntos[idx][0] or (puntos[i][0] == puntos[idx][0] and puntos[i][1] < puntos[idx][1]):
            idx = i
    return idx


def orientacion(a: Point, b: Point, c: Point) -> float:
    """
    [TODO IMPLEMENTADO] Regresa el valor del producto cruz (cross product).

    Interpretación:
    - cross > 0  : giro antihorario (CCW)
    - cross < 0  : giro horario (CW)
    - cross == 0 : colineales
    """
    # Implementación del producto cruz
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return cross


def distancia2(a: Point, b: Point) -> float:
    """Distancia al cuadrado (evita usar sqrt, no hace falta para comparar)."""
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def convex_hull(puntos: List[Point]) -> List[Point]:
    """
    [TODO] Algoritmo de Jarvis March para calcular Convex Hull

    Idea general:
    1) Empieza en el punto más a la izquierda.
    2) En cada paso, elige el siguiente punto q tal que para cualquier otro punto r,
       el giro desde p hacia q sea el “más externo”.
    3) Repite hasta regresar al punto inicial.

    Nota:
    - Maneja colineales: si varios puntos quedan en la misma línea,
      quédate con el más lejano para que la envolvente quede “por fuera”.
    """
    if len(puntos) < 3:
        return puntos[:]  

    hull: List[Point] = []
    start_idx = punto_mas_izquierdo(puntos)
    p_idx = start_idx

    while True:
        hull.append(puntos[p_idx])
        q_idx = (p_idx + 1) % len(puntos)

        
        for r_idx in range(len(puntos)):
            if r_idx == p_idx:
                continue

            
            o = orientacion(puntos[p_idx], puntos[q_idx], puntos[r_idx])
            
            if o < 0:
                q_idx = r_idx

            elif o == 0:
                if distancia2(puntos[p_idx], puntos[r_idx]) > distancia2(puntos[p_idx], puntos[q_idx]):
                    q_idx = r_idx

        p_idx = q_idx
        if p_idx == start_idx:
            break

    return hull


def dibujar(puntos: List[Point], hull: List[Point], titulo: str = "Convex Hull"):
    """Crea una figura con puntos y el polígono del hull."""
    fig = Figure(figsize=(10, 8), dpi=100)
    ax = fig.add_subplot(111)
    
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]

    ax.scatter(xs, ys, alpha=0.6, s=20)

    if len(hull) >= 2:
        hx = [p[0] for p in hull] + [hull[0][0]]
        hy = [p[1] for p in hull] + [hull[0][1]]
        ax.plot(hx, hy, 'r-', linewidth=2, label='Convex Hull')
        ax.scatter([p[0] for p in hull], [p[1] for p in hull], color='red', s=50, zorder=5)

    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


class ConvexHullGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Convex Hull Visualizer")
        self.root.geometry("1200x800")
        
        self.puntos = None
        self.hull = None
        self.canvas_widget = None
        
        # Panel de controles
        control_frame = tk.Frame(root, bg="#f0f0f0", height=80)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Botón para seleccionar archivo
        self.btn_archivo = tk.Button(
            control_frame,
            text="📁 Seleccionar CSV",
            command=self.seleccionar_archivo,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.btn_archivo.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta de información
        self.info_label = tk.Label(
            control_frame,
            text="Selecciona un archivo CSV para comenzar...",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#333"
        )
        self.info_label.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        # Botón para limpiar
        self.btn_limpiar = tk.Button(
            control_frame,
            text="🗑️ Limpiar",
            command=self.limpiar,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10
        )
        self.btn_limpiar.pack(side=tk.RIGHT, padx=5)
        
        # Panel para el gráfico
        self.graph_frame = tk.Frame(root)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def seleccionar_archivo(self):
        """Abre diálogo para seleccionar archivo CSV."""
        archivo = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                self.puntos = leer_puntos_csv(archivo)
                if len(self.puntos) < 3:
                    messagebox.showerror("Error", "Se necesitan al menos 3 puntos")
                    return
                
                self.hull = convex_hull(self.puntos)
                
                # Actualizar información
                self.info_label.config(
                    text=f"✓ {len(self.puntos)} puntos | "
                         f"Hull: {len(self.hull)} vértices | "
                         f"Archivo: {os.path.basename(archivo)}"
                )
                
                # Mostrar gráfico
                self.mostrar_grafico()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer archivo:\n{str(e)}")
    
    def mostrar_grafico(self):
        """Muestra el gráfico del convex hull en la GUI."""
        # Limpiar canvas anterior
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Crear figura
        fig = dibujar(self.puntos, self.hull, "Convex Hull Visualizer")
        
        # Integrar en tkinter
        self.canvas_widget = tkagg.FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def limpiar(self):
        """Limpia el gráfico y reinicia."""
        self.puntos = None
        self.hull = None
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.info_label.config(text="Selecciona un archivo CSV para comenzar...")


def main():
    root = tk.Tk()
    gui = ConvexHullGUI(root)
    root.mainloop()



if __name__ == "__main__":
    main()