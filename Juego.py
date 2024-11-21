import random
import sqlite3
import tkinter as tk
from tkinter import messagebox


# Crear base de datos y tablas
def crear_base_datos():
    conn = sqlite3.connect("ahorcado.db")
    cursor = conn.cursor()

    # Crear tabla palabras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palabras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            palabra TEXT NOT NULL
        )
    """)

    # Crear tabla partidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_jugador TEXT NOT NULL,
            partidas_jugadas INTEGER DEFAULT 0,
            partidas_ganadas INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Insertar palabras iniciales
def insertar_palabras_iniciales():
    palabras = {
        "frutas": [
            "manzana",
            "platano",
            "naranja",
            "uva",
            "fresa",
            "melocoton",
            "pera",
            "mango",
            "kiwi",
            "sandia",
            "melon",
            "cereza",
            "ciruela",
            "higo",
            "granada",
            "papaya",
            "guayaba",
            "piña",
            "limon",
            "lima",
            "frambuesa",
            "arándano",
            "durazno",
            "nectarina",
            "mandarina",
            "coco",
            "pomelo",
            "tamarindo",
            "chirimoya",
            "caqui",
            "lichi"
        ],
        "informatica": [
            "python", "java", "código", "teclado", "monitor", "inteligencia", "servidor", "cliente", "software",
            "internet"
        ],
        "personas": [
            "maaaaaaaaaartin",
            "ivan",
            "andrea",
            "rafa",
            "antonio",
            "jusep",
            "niko",
            "rodri",
            "alberto",
            "victor",
            "lucas",
            "miguel",
            "patricia",
            "josema",
            "raul",
            "pablo",
            "dani",
        ]
    }

    conn = sqlite3.connect("ahorcado.db")
    cursor = conn.cursor()
  #aqui se insertan las palabras en la base de datos
    for tema, lista_palabras in palabras.items():
        for palabra in lista_palabras:
            cursor.execute("""
                INSERT OR IGNORE INTO palabras (tema, palabra)
                VALUES (?, ?)
            """, (tema, palabra))

    conn.commit()
    conn.close()


# Cargar palabras desde SQLite
def cargar_palabras(tema):
    conn = sqlite3.connect("ahorcado.db")
    cursor = conn.cursor()

    cursor.execute("SELECT palabra FROM palabras WHERE tema = ?", (tema,))
    palabras = [row[0] for row in cursor.fetchall()]

    conn.close()
    return palabras


# Guardar partida en SQLite
def guardar_partida(nombre_jugador, gano):
    conn = sqlite3.connect("ahorcado.db")
    cursor = conn.cursor()

    # Consultar si el jugador ya existe
    cursor.execute("""
        SELECT id, partidas_jugadas, partidas_ganadas
        FROM partidas
        WHERE nombre_jugador = ?
    """, (nombre_jugador,))
    resultado = cursor.fetchone()

    if resultado:
        jugador_id, partidas_jugadas, partidas_ganadas = resultado
        partidas_jugadas += 1
        if gano:
            partidas_ganadas += 1
        cursor.execute("""
            UPDATE partidas
            SET partidas_jugadas = ?, partidas_ganadas = ?
            WHERE id = ?
        """, (partidas_jugadas, partidas_ganadas, jugador_id))
    else:
        cursor.execute("""
            INSERT INTO partidas (nombre_jugador, partidas_jugadas, partidas_ganadas)
            VALUES (?, ?, ?)
        """, (nombre_jugador, 1, 1 if gano else 0))

    conn.commit()
    conn.close()


class AhorcadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego del ahorcado")
        self.nombre_jugador = ""
        self.tema = ""
        self.palabra_secreta = ""
        self.letras_adivinadas = []
        self.letras_incorrectas = []
        self.errores = 0
        self.intentos_restantes = 6

        self.estilo_inicio()

    def estilo_inicio(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # configuracion colores y estilo
        fondo_principal = "#1e1e2f"
        fondo_secundario = "#2d2d44"
        color_texto = "#ffffff"
        color_resaltado = "#ff79c6"
        fuente_titulo = ("Helvetica", 20, "bold")
        fuente_texto = ("Helvetica", 12)

        self.root.configure(bg=fondo_principal)

        # Titulo
        tk.Label(self.root, text="Bienvenido al ahorcado", font=fuente_titulo, bg=fondo_principal,
                 fg=color_resaltado).pack(pady=20)

        # datos jugador
        frame = tk.Frame(self.root, bg=fondo_secundario, padx=20, pady=20, relief="flat")
        frame.pack(pady=20)
        # ingresar nombre
        tk.Label(frame, text="Ingresa tu nombre:", font=fuente_texto, bg=fondo_secundario,
                 fg=color_texto).pack(pady=5)
        self.nombre_entry = tk.Entry(frame, font=fuente_texto, relief="flat", justify="center",
                                     bg=fondo_principal, fg=color_texto, insertbackground=color_resaltado)
        self.nombre_entry.pack(pady=5)

        # elegir el tema
        tk.Label(frame, text="Selecciona un tema:", font=fuente_texto, bg=fondo_secundario,
                 fg=color_texto).pack(pady=10)
        self.tema_var = tk.StringVar(value="frutas")
        temas = [("Frutas", "frutas"), ("Informática", "informatica"), ("Nombres de personas", "personas")]
        for texto, valor in temas:
            tk.Radiobutton(frame, text=texto, variable=self.tema_var, value=valor, font=fuente_texto,
                           bg=fondo_secundario, fg=color_texto, selectcolor=fondo_principal,
                           activebackground=fondo_secundario,
                           activeforeground=color_resaltado).pack(anchor="w", padx=10, pady=2)

        # boton inicio
        tk.Button(frame, text="Iniciar Juego", command=self.iniciar_juego, font=("Helvetica", 14, "bold"),
                  bg=color_resaltado, fg=fondo_principal, bd=0, padx=15, pady=10, activebackground="#ff92d0",
                  activeforeground=fondo_principal).pack(pady=20)

    def iniciar_juego(self):
        self.nombre_jugador = self.nombre_entry.get().strip()
        self.tema = self.tema_var.get()
        if not self.nombre_jugador:
            messagebox.showerror("Error", "Por favor, ingrese su nombre.")
            return

        palabras = cargar_palabras(self.tema)
        if not palabras:
            messagebox.showerror("Error", "No hay palabras disponibles para este tema.")
            return

        self.palabra_secreta = random.choice(palabras).lower()
        self.letras_adivinadas = []
        self.letras_incorrectas = []
        self.errores = 0

        self.estilo_juego()

    def estilo_juego(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # configuracion colores y estilo
        fondo_principal = "#1e1e2f"
        fondo_secundario = "#2d2d44"
        color_texto = "#ffffff"
        color_resaltado = "#ff79c6"
        fuente_titulo = ("Helvetica", 16, "bold")
        fuente_texto = ("Helvetica", 12)
        fuente_resaltado = ("Courier New", 24, "bold")
        borde_redondeado = 10

        self.root.configure(bg=fondo_principal)

        # datos jugador y tema
        tk.Label(self.root, text=f"Nombre: {self.nombre_jugador}", font=fuente_titulo, bg=fondo_principal,
                 fg=color_texto).pack(pady=5)
        tk.Label(self.root, text=f"Tema: {self.tema.capitalize()}", font=fuente_titulo, bg=fondo_principal,
                 fg=color_resaltado).pack(pady=5)

        # palabra secreta
        self.palabra_label = tk.Label(self.root, text=self.get_palabra_mostrada(), font=fuente_resaltado,
                                      bg=fondo_principal, fg=color_texto)
        self.palabra_label.pack(pady=20)

        # dibujo
        self.dibujo_label = tk.Label(self.root, text=self.dibujar_ahorcado(), font=fuente_texto,
                                     bg=fondo_principal, fg=color_texto)
        self.dibujo_label.pack()

        # letras incorrectas
        tk.Label(self.root, text="Letras incorrectas:", font=fuente_texto, bg=fondo_principal, fg=color_texto).pack(pady=5)
        self.letras_incorrectas_label = tk.Label(self.root, text=", ".join(self.letras_incorrectas), font=fuente_texto,
                                         bg=fondo_principal, fg='red')  # Manteniendo el color rojo
        self.letras_incorrectas_label.pack(pady=5)


        # entrada de letra
        tk.Label(self.root, text="Introduce una letra:", font=fuente_texto, bg=fondo_principal, fg=color_texto).pack(
            pady=5)
        self.letra_entry = tk.Entry(self.root, font=fuente_texto, bg=fondo_principal, fg=color_texto)
        self.letra_entry.pack(pady=5)
        tk.Button(self.root, text="Comprobar", command=self.comprobar_letra, font=fuente_texto,
                  bg=color_resaltado, fg=fondo_principal, padx=15, pady=5, bd=0).pack(pady=5)

    def get_palabra_mostrada(self):
        return " ".join([letra if letra in self.letras_adivinadas else "_" for letra in self.palabra_secreta])

    def dibujar_ahorcado(self):
        ahorcado = [
            "  +---+\n      |\n      |\n      |\n     ===",
            "  +---+\n  O   |\n      |\n      |\n     ===",
            "  +---+\n  O   |\n  |   |\n      |\n     ===",
            "  +---+\n  O   |\n /|   |\n      |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n      |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n /    |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n / \\  |\n     ===",
        ]
        return ahorcado[self.errores]

    def comprobar_letra(self):
        letra = self.letra_entry.get().strip().lower()
        if len(letra) != 1 or not letra.isalpha():
            messagebox.showerror("Error", "Por favor, ingresa solo una letra.")
            return

        if letra in self.letras_adivinadas or letra in self.letras_incorrectas:
            messagebox.showinfo("Atención", "Ya has adivinado esta letra.")
            return

        if letra in self.palabra_secreta:
            self.letras_adivinadas.append(letra)
            if all(letra in self.letras_adivinadas for letra in self.palabra_secreta):
                messagebox.showinfo("¡OLEEEE OLEEEEE LOS CARACOLEEEEE!", f"¡Felicidades shurra, ganaste! La palabra era {self.palabra_secreta}.")
                guardar_partida(self.nombre_jugador, True)
                self.estilo_inicio()
        else:
            self.letras_incorrectas.append(letra)
            self.errores += 1
            if self.errores == 6:
                messagebox.showinfo("Perdiste", f"Perdiste. La palabra era {self.palabra_secreta}.")
                guardar_partida(self.nombre_jugador, False)
                self.estilo_inicio()

        self.estilo_juego()


if __name__ == "__main__":
    crear_base_datos()
    insertar_palabras_iniciales()

    root = tk.Tk()
    app = AhorcadoApp(root)
    root.mainloop()
