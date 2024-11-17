import random
import json
import tkinter as tk
from tkinter import messagebox


# cargara las palabras desde el json que se llama "palabras.json"
def cargar_palabras(tema):
    with open('palabras.json', 'r') as f:
        palabras = json.load(f)
    return palabras[tema]


# Guardara las partidas jugadas y ganadas en el json partidas.json
def guardar_partida(nombre_jugador, gano):
    try:
        with open('partidas.json', 'r') as f:
            partidas = json.load(f)
    except FileNotFoundError:
        partidas = {}
    # por cada partida jugada y ganada aumentara +1
    if nombre_jugador in partidas:
        partidas[nombre_jugador]['partidas_jugadas'] += 1
        if gano:
            partidas[nombre_jugador]['partidas_ganadas'] += 1
    else:
        partidas[nombre_jugador] = {'partidas_jugadas': 1, 'partidas_ganadas': 1 if gano else 0}

    with open('partidas.json', 'w') as f:
        json.dump(partidas, f, indent=4)


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
        borde_redondeado = 10

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

        try:
            palabras = cargar_palabras(self.tema)  # comprueba si el archivo existe
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo de palabras.")
            return

        self.palabra_secreta = random.choice(palabras).lower()  # genera la palabra aleatoria del tema seleccionado
        self.letras_adivinadas = []
        self.letras_incorrectas = []
        self.errores = 0

        self.estilo_juego()

    def estilo_juego(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # colores y estilos
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
        tk.Label(self.root, text=f"Jugador: {self.nombre_jugador}", font=fuente_titulo, bg=fondo_principal,
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
        tk.Label(self.root, text="Letras incorrectas:", font=fuente_texto, bg=fondo_principal, fg=color_texto).pack(
            pady=5)
        self.letras_incorrectas_label = tk.Label(self.root, text=", ".join(self.letras_incorrectas), font=fuente_texto,
                                                 bg=fondo_principal, fg=color_resaltado)
        self.letras_incorrectas_label.pack()

        # campo de texto
        entrada_frame = tk.Frame(self.root, bg=fondo_secundario, bd=0, highlightthickness=0)
        entrada_frame.pack(pady=20)

        tk.Label(entrada_frame, text="Ingresa una letra:", font=fuente_texto, bg=fondo_secundario,
                 fg=color_texto).pack(side=tk.LEFT, padx=5)

        self.letra_entry = tk.Entry(entrada_frame, font=fuente_texto, width=5, relief="flat", justify="center",
                                    bg=fondo_principal, fg=color_texto, insertbackground=color_resaltado)
        self.letra_entry.pack(side=tk.LEFT, padx=5)
        self.letra_entry.bind("<Return>", lambda event: self.intentar_letra())

        tk.Button(entrada_frame, text="Intentar", command=self.intentar_letra, font=fuente_titulo,
                  bg=color_resaltado, fg=fondo_principal, bd=0, padx=10, pady=5, activebackground="#ff92d0",
                  activeforeground=fondo_principal).pack(side=tk.LEFT, padx=5)

    def get_palabra_mostrada(self):
        return " ".join([letra if letra in self.letras_adivinadas else "_" for letra in self.palabra_secreta])

    def dibujar_ahorcado(self):
        estados = [
            "  +---+\n      |\n      |\n      |\n     ===",
            "  +---+\n  O   |\n      |\n      |\n     ===",
            "  +---+\n  O   |\n  |   |\n      |\n     ===",
            "  +---+\n  O   |\n /|   |\n      |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n      |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n /    |\n     ===",
            "  +---+\n  O   |\n /|\\  |\n / \\  |\n     ===",
        ]
        return estados[self.errores]

    def intentar_letra(self):
        letra = self.letra_entry.get().lower().strip()  # esta es la letra ingresada
        self.letra_entry.delete(0, tk.END)  # borra la letra ingresada

        if len(letra) != 1 or not letra.isalpha():
            messagebox.showerror("Estas cuajao", "Por favor, ingresa una letra válida.")
            return

        if letra in self.letras_adivinadas or letra in self.letras_incorrectas:
            messagebox.showwarning("Espabila", "Ya has ingresado esa letra.")
            return

        if letra in self.palabra_secreta:
            self.letras_adivinadas.append(letra)
            if set(self.letras_adivinadas) >= set(self.palabra_secreta):
                messagebox.showinfo("¡Oleeee los caracoleee!", f"¡Ganaste! La palabra era: {self.palabra_secreta}")
                guardar_partida(self.nombre_jugador, True)
                self.estilo_inicio()
                return
        else:
            self.letras_incorrectas.append(letra)
            self.errores += 1
            if self.errores >= self.intentos_restantes:
                messagebox.showinfo("Fin del Juego", f"Has perdido. La palabra era: {self.palabra_secreta}")
                guardar_partida(self.nombre_jugador, False)
                self.estilo_inicio()
                return

        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        self.palabra_label.config(
            text=self.get_palabra_mostrada())  # esto hace que se muestre la palabra con las letras adivinadas
        self.dibujo_label.config(text=self.dibujar_ahorcado())  # esto hace que se muestre el dibujo del ahorcado
        self.letras_incorrectas_label.config(
            text=", ".join(self.letras_incorrectas))  # esto hace que se muestre las letras incorrectas


if __name__ == "__main__":
    root = tk.Tk()
    app = AhorcadoApp(root)
    root.mainloop()
