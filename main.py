import pygame
import random
from fractions import Fraction
import asyncio
import sys
import sys

# Detectar si estamos en un entorno web (pygbag)
IS_WEB = "pygame_web" in sys.modules
# Inicializar Pygame y el mixer
pygame.init()
pygame.mixer.init()

# Cargar sonidos
try:
    laser_sound = pygame.mixer.Sound("laser.wav")  # Sonido de disparo
    explosion_sound = pygame.mixer.Sound("explosion.wav")  # Sonido de impacto correcto
    fallido_sound = pygame.mixer.Sound("fallido.wav")  # Sonido de impacto incorrecto
    game_over_sound = pygame.mixer.Sound("GameOver.wav")  # Sonido de game over
    print("Sonidos cargados correctamente")
except pygame.error as e:
    print(f"Error al cargar sonidos: {e}")

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FracShooter")

# Cargar la imagen de fondo
background = pygame.image.load("fracshooter.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_YELLOW = (255, 255, 102)

# Fuentes
font = pygame.font.Font(None, 50)  # Fuente grande (para títulos, etc.)
small_font = pygame.font.Font(None, 36)  # Fuente mediana (ya existente)
tiny_font = pygame.font.Font(None, 24)  # Nueva fuente más pequeña

# Variables globales para almacenar datos (en lugar de localStorage)
rapidez_global = 1
highscore_global = 0

def guardar_rapidez(rapidez):
    global rapidez_global
    rapidez_global = rapidez

def cargar_rapidez():
    global rapidez_global
    return rapidez_global

def save_highscore(score):
    global highscore_global
    highscore_global = score

def load_highscore():
    global highscore_global
    return highscore_global

def guardar_puntaje(nombre, puntaje):
    if IS_WEB:
        # Usar localStorage en la web
        puntajes_guardados = localStorage.getItem("puntajes")
        if puntajes_guardados:
            puntajes = eval(puntajes_guardados)  # Convertir de string a lista
        else:
            puntajes = []
        puntajes.append((nombre, puntaje))
        localStorage.setItem("puntajes", str(puntajes))
    else:
        # Usar un archivo de texto en la terminal
        with open("puntajes.txt", "a") as archivo:
            archivo.write(f"{nombre}: {puntaje}\n")

def cargar_puntajes():
    if IS_WEB:
        # Cargar desde localStorage en la web
        puntajes_guardados = localStorage.getItem("puntajes")
        if puntajes_guardados:
            return eval(puntajes_guardados)  # Convertir de string a lista
        else:
            return []
    else:
        # Cargar desde un archivo de texto en la terminal
        try:
            with open("puntajes.txt", "r") as archivo:
                puntajes = []
                for linea in archivo:
                    nombre, puntaje = linea.strip().split(": ")
                    puntajes.append((nombre, int(puntaje)))
                return puntajes
        except FileNotFoundError:
            return []
async def mostrar_puntajes():
    puntajes = cargar_puntajes()
    desplazamiento = 0  # Controla el desplazamiento vertical
    waiting = True
    while waiting:
        screen.fill(WHITE)  # Fondo blanco

        # Título
        texto_titulo = font.render("Puntajes Guardados", True, BLUE)
        screen.blit(texto_titulo, (WIDTH // 2 - 150, 20))

        # Mostrar los puntajes
        for i, (nombre, puntaje) in enumerate(puntajes):
            y_pos = 100 + i * 40 - desplazamiento  # Ajustar la posición vertical
            if 100 <= y_pos < HEIGHT - 100:  # Solo mostrar los puntajes dentro de la pantalla
                texto_puntaje = small_font.render(f"{nombre}: {puntaje}", True, BLACK)
                screen.blit(texto_puntaje, (WIDTH // 2 - 100, y_pos))

        # Instrucciones para desplazarse
        texto_instrucciones = tiny_font.render("Usa las flechas ARRIBA/ABAJO para desplazarte", True, BLACK)
        screen.blit(texto_instrucciones, (WIDTH // 2 - 200, HEIGHT - 80))
        texto_volver = tiny_font.render("Presiona ENTER para volver al menú", True, BLACK)
        screen.blit(texto_volver, (WIDTH // 2 - 150, HEIGHT - 50))
        texto_exportar = tiny_font.render("Presiona E para exportar los puntajes", True, BLACK)
        screen.blit(texto_exportar, (WIDTH // 2 - 150, HEIGHT - 20))

        pygame.display.flip()

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Volver al menú
                    waiting = False
                elif event.key == pygame.K_UP:  # Desplazarse hacia arriba
                    desplazamiento = max(0, desplazamiento - 20)
                elif event.key == pygame.K_DOWN:  # Desplazarse hacia abajo
                    desplazamiento = min(len(puntajes) * 40 - (HEIGHT - 200), desplazamiento + 20)
                elif event.key == pygame.K_e:  # Exportar puntajes
                    if await solicitar_contraseña():  # Solicitar contraseña
                        await exportar_puntajes(puntajes)  # Exportar si la contraseña es correcta

        await asyncio.sleep(0)  # Evitar bloqueo
async def solicitar_contraseña():
    contraseña_correcta = "123"
    contraseña_ingresada = ""
    input_activo = True

    while input_activo:
        screen.blit(background, (0, 0))
        texto_instruccion = font.render("Ingresa la contraseña:", True, BLUE)
        texto_contraseña = font.render("*" * len(contraseña_ingresada), True, BLACK)
        screen.blit(texto_instruccion, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        screen.blit(texto_contraseña, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_activo = False
                elif event.key == pygame.K_BACKSPACE:
                    contraseña_ingresada = contraseña_ingresada[:-1]
                else:
                    contraseña_ingresada += event.unicode

        await asyncio.sleep(0)  # Ceder el control

    # Verificar la contraseña
    if contraseña_ingresada == contraseña_correcta:
        return True
    else:
        # Mostrar mensaje de error
        screen.blit(background, (0, 0))
        texto_error = font.render("Contraseña incorrecta", True, RED)
        screen.blit(texto_error, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        await asyncio.sleep(2)  # Mostrar el mensaje por 2 segundos
        return False
async def exportar_puntajes(puntajes):
    if IS_WEB:
        # Crear un archivo de texto con los puntajes
        contenido = "\n".join([f"{nombre}: {puntaje}" for nombre, puntaje in puntajes])
        
        # Usar JavaScript para crear un archivo descargable
        js_code = f"""
        const contenido = `{contenido}`;
        const blob = new Blob([contenido], {{ type: 'text/plain' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'puntajes.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        """
        # Ejecutar el código JavaScript en el navegador
        import js
        js.eval(js_code)
        
        # Mostrar un mensaje en la pantalla
        screen.blit(background, (0, 0))
        texto_exportado = font.render("Puntajes exportados como puntajes.txt", True, BLACK)
        screen.blit(texto_exportado, (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.flip()
        await asyncio.sleep(2)  # Mostrar el mensaje por 2 segundos
    else:
        # En un entorno no web, simplemente guardar en un archivo
        with open("puntajes_exportados.txt", "w") as archivo:
            for nombre, puntaje in puntajes:
                archivo.write(f"{nombre}: {puntaje}\n")
        
        # Mostrar un mensaje en la pantalla
        screen.blit(background, (0, 0))
        texto_exportado = font.render("Puntajes exportados como puntajes_exportados.txt", True, BLACK)
        screen.blit(texto_exportado, (WIDTH // 2 - 250, HEIGHT // 2))
        pygame.display.flip()
        await asyncio.sleep(2)  # Mostrar el mensaje por 2 segundos
async def show_instructions():
    instructions = [
        "INSTRUCCIONES DEL JUEGO",
        "",
        "1. Mueve el jugador con las flechas izquierda/derecha.",
        "2. Dispara con ESPACIO.",
        "3. Apunta a la fracción correcta.",
        "4. Cada acierto suma puntos, según el nivel.",
        "5. Si fallas 3 veces, el juego termina.",
        "",
        "Presiona ENTER para volver al menú."
    ]
    waiting = True
    while waiting:
        screen.blit(background, (0, 0))
        instruction_rect = pygame.Rect(50, 80, WIDTH - 100, HEIGHT - 120)
        pygame.draw.rect(screen, WHITE, instruction_rect)
        pygame.draw.rect(screen, BLUE, instruction_rect, 3)
        for i, line in enumerate(instructions):
            text = small_font.render(line, True, BLUE)
            screen.blit(text, (70, 100 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
        await asyncio.sleep(0)  # Evitar bloqueo

async def select_level():
    levels = ["Principiante", "Intermedio", "Experto"]
    selected_level = 0
    selecting = True
    while selecting:
        screen.blit(background, (0, 0))
        for i, level in enumerate(levels):
            rect_x, rect_y = WIDTH // 2 - 120, 300 + i * 70
            pygame.draw.rect(screen, LIGHT_YELLOW, (rect_x, rect_y, 240, 50))
            pygame.draw.rect(screen, BLACK, (rect_x, rect_y, 240, 50), 3)
            color = RED if i == selected_level else BLACK
            text = font.render(level, True, color)
            screen.blit(text, text.get_rect(center=(rect_x + 120, rect_y + 25)))
        
        # Agregar la opción de regresar al menú principal
        texto_volver = small_font.render("Presiona ESC para volver al menú", True, BLACK)
        screen.blit(texto_volver, (WIDTH // 2 - 150, HEIGHT - 50))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % len(levels)
                elif event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % len(levels)
                elif event.key == pygame.K_RETURN:
                    guardar_rapidez([1, 3, 4][selected_level])
                    selecting = False
                    print(f"Nivel seleccionado: {levels[selected_level]}")  # Mensaje de depuración
                    await start_game()  # Llamar a la función del juego
                elif event.key == pygame.K_ESCAPE:  # Regresar al menú principal
                    selecting = False
                    await main_menu()
        await asyncio.sleep(0)  # Evitar bloqueo

async def main_menu():
    options = ["Jugar", "Instrucciones", "Puntajes"]  # Opción "Puntajes"
    selected_option = 0
    running = True
    while running:
        screen.blit(background, (0, 0))
        for i, option in enumerate(options):
            rect_x, rect_y = WIDTH // 2 - 120, 200 + i * 70
            pygame.draw.rect(screen, LIGHT_BLUE, (rect_x, rect_y, 240, 50))
            pygame.draw.rect(screen, BLUE, (rect_x, rect_y, 240, 50), 3)
            color = RED if i == selected_option else BLACK
            text = font.render(option, True, color)
            screen.blit(text, text.get_rect(center=(rect_x + 120, rect_y + 25)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_option] == "Jugar":
                        await select_level()
                    elif options[selected_option] == "Instrucciones":
                        await show_instructions()
                    elif options[selected_option] == "Puntajes":
                        await mostrar_puntajes()
        await asyncio.sleep(0)  # Evitar bloqueo

    # Cerrar Pygame y salir del programa
    pygame.quit()
    sys.exit()

async def input_nombre(score):
    # Primero, preguntar si desea guardar el puntaje
    confirmacion = True
    guardar = False
    while confirmacion:
        screen.blit(background, (0, 0))
        texto_confirmacion = font.render("¿ Deseas guardar tu puntaje?", True, BLACK)
        texto_si = font.render("Sí (S)", True, BLACK)
        texto_no = font.render("No (N)", True, BLACK)
        screen.blit(texto_confirmacion, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        screen.blit(texto_si, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(texto_no, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Si el jugador presiona 'S' (Sí)
                    guardar = True
                    confirmacion = False
                elif event.key == pygame.K_n:  # Si el jugador presiona 'N' (No)
                    guardar = False
                    confirmacion = False
        await asyncio.sleep(0)  # Ceder el control

    # Si el jugador no quiere guardar el puntaje, regresar al menú principal
    if not guardar:
        await main_menu()
        return

    # Si el jugador quiere guardar el puntaje, pedir su nombre
    nombre = ""
    input_activo = True
    while input_activo:
        screen.blit(background, (0, 0))
        texto_instruccion = font.render("Nombre:", True, BLUE)
        texto_nombre = font.render(nombre, True, BLACK)
        screen.blit(texto_instruccion, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        screen.blit(texto_nombre, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_activo = False
                elif event.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    nombre += event.unicode
        await asyncio.sleep(0)  # Ceder el control

    # Guardar el puntaje
    guardar_puntaje(nombre, score)

    # Mostrar mensaje de "Puntaje guardado"
    screen.blit(background, (0, 0))
    texto_guardado = font.render("Puntaje guardado", True, BLACK)
    screen.blit(texto_guardado, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    await asyncio.sleep(2)  # Mostrar el mensaje por 2 segundos

    # Regresar al menú principal
    await main_menu()
async def start_game():
    print("Iniciando juego...")  # Mensaje de depuración
    # Configuración de la pantalla
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dispara a la Operación Correcta")

    # Cargar imágenes
    player_image = pygame.image.load("Imagen/Cohete.png")
    player_image = pygame.transform.scale(player_image, (50, 50))
    bullet_image = pygame.image.load("Imagen/bala.png")
    bullet_image = pygame.transform.scale(bullet_image, (10, 20))

    # Cargar imagen de fondo
    background = pygame.image.load("Imagen/fondo.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Jugador
    player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 50)

    # Balas
    bullets = []

    # Fracciones y operaciones
    fractions = []
    num_fractions = 5
    frac1 = frac2 = target_result = None
    operation = ""

    # Usar la rapidez cargada
    rapidez = cargar_rapidez()
    fall_speed = rapidez / 2
    fall_accumulator = 0
    message = ""
    message_timer = 0

    # Movimiento del jugador
    move_left = False
    move_right = False
    player_speed = 5

    # Cargar y guardar el puntaje más alto
    highscore = load_highscore()

    def generate_fractions():
        nonlocal frac1, frac2, target_result, operation, message
        fractions.clear()

        # Generar fracciones aleatorias
        frac1 = Fraction(random.randint(1, 5), random.randint(2, 9))
        frac2 = Fraction(random.randint(1, 5), random.randint(2, 9))

        # Elegir una operación aleatoria
        operation = random.choice(["+", "-", "x", "÷"])

        # Calcular el resultado correcto
        if operation == "+":
            target_result = frac1 + frac2
        elif operation == "-":
            target_result = frac1 - frac2
        elif operation == "x":
            target_result = frac1 * frac2
        elif operation == "÷":
            target_result = frac1 / frac2 if frac2 != 0 else frac1

        # Evitar resultados negativos o demasiado grandes
        if target_result < 0 or target_result > 10:
            generate_fractions()
            return

        # Generar fracciones incorrectas como distractores
        positions = []
        for _ in range(num_fractions - 1):
            while True:
                num = random.randint(1, 9)
                den = random.randint(2, 9)
                frac = Fraction(num, den)
                if frac == target_result:
                    continue
                x = random.randint(50, WIDTH - 100)
                y = random.randint(50, HEIGHT // 2)
                rect = pygame.Rect(x, y, 50, 50)

                if not any(r.colliderect(rect) for _, r in fractions):
                    fractions.append((frac, rect))
                    positions.append(rect)
                    break

        # Agregar la fracción correcta en una posición aleatoria
        while True:
            x = random.randint(50, WIDTH - 100)
            y = random.randint(50, HEIGHT // 2)
            rect = pygame.Rect(x, y, 50, 50)
            if not any(r.colliderect(rect) for _, r in fractions):
                fractions.append((target_result, rect))
                break

    generate_fractions()

    def draw_text_box(text, x, y, w, h, font=tiny_font):  # Usar tiny_font por defecto
        pygame.draw.rect(screen, WHITE, (x, y, w, h))  # Fondo blanco
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)  # Borde negro
        text_surface = font.render(text, True, BLACK)  # Usar la fuente proporcionada
        screen.blit(text_surface, (x + 10, y + 5))

    def draw_text_box1(text, x, y, w, h, font=tiny_font):  # Usar tiny_font por defecto
        pygame.draw.rect(screen, (0, 255, 0), (x, y, w, h))  # Fondo verde
        pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)  # Borde blanco
        text_surface = font.render(text, True, BLACK)  # Usar la fuente proporcionada
        screen.blit(text_surface, (x + 10, y + 7))

    # Variables del juego
    running = True
    score = 0
    lives = 10

    while running:
        screen.fill(WHITE)

        # Dibujar fondo
        screen.blit(background, (0, 0))

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_left = True
                elif event.key == pygame.K_RIGHT:
                    move_right = True
                elif event.key == pygame.K_SPACE:
                    bullets.append(pygame.Rect(player.centerx - 5, player.top, 10, 20))
                    laser_sound.play()  # Reproducir sonido de disparo
                elif event.key == pygame.K_ESCAPE:  # Regresar al menú principal
                    running = False
                    await main_menu()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False

        # Movimiento del jugador
        if move_left and player.left > 0:
            player.move_ip(-player_speed, 0)
        if move_right and player.right < WIDTH:
            player.move_ip(player_speed, 0)

        # Movimiento de balas
        for bullet in bullets[:]:
            bullet.move_ip(0, -10)
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Mover fracciones hacia abajo
        fall_accumulator += fall_speed
        if fall_accumulator >= 1:
            move_pixels = int(fall_accumulator)
            for frac, rect in fractions[:]:
                rect.move_ip(0, move_pixels)
                if rect.top > HEIGHT:
                    fractions.remove((frac, rect))
                    lives -= 1
                    message = "Fallaste una fracción!"
                    message_timer = 60
                    generate_fractions()
            fall_accumulator -= move_pixels

        # Dibujar jugador
        screen.blit(player_image, player.topleft)

        # Dibujar fracciones
        font_small = pygame.font.Font(None, 24)  # Fuente más pequeña
        for frac, rect in fractions:
            pygame.draw.rect(screen, RED, rect)  # Dibuja el rectángulo rojo
            text = font_small.render(str(frac), True, BLACK)  # Renderiza el texto con la fuente pequeña
            screen.blit(text, (rect.x + 10, rect.y + 15))  # Dibuja el texto dentro del rectángulo

        # Dibujar balas
        for bullet in bullets:
            screen.blit(bullet_image, bullet.topleft)

        # Verificar colisiones
        for bullet in bullets[:]:
            for frac, rect in fractions[:]:
                if bullet.colliderect(rect):
                    bullets.remove(bullet)
                    fractions.remove((frac, rect))
                    if frac == target_result:
                        score += 10 * rapidez
                        message = "¡Acertaste!"
                        explosion_sound.play()  # Reproducir sonido de impacto correcto
                        generate_fractions()
                    else:
                        lives -= 1
                        message = "Fallaste!"
                        fallido_sound.play()  # Reproducir sonido de impacto incorrecto
                    message_timer = 60
                    break

        # Verificar si el puntaje es el más alto
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        # Mostrar información
        draw_text_box(f"Puntaje: {score}", 10, 10, 150, 30)  # Reducir el ancho y alto del cuadro
        draw_text_box1(f"{frac1} {operation} {frac2}", WIDTH // 2 - 70, 10, 180, 30)  # Ajustar posición y tamaño
        draw_text_box(f"Vidas: {lives}", WIDTH - 150, 10, 100, 30)  # Reducir el ancho y alto del cuadro
        draw_text_box(f"Récord: {highscore}", WIDTH - 200, 50, 180, 30)  # Reducir el ancho y alto del cuadro

        # Si las vidas llegan a 0, termina el juego
        if lives <= 0:
            game_over_text = font.render("¡Juego Terminado!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            game_over_sound.play()  # Reproducir sonido de game over
            await asyncio.sleep(2)  # Mostrar el mensaje por 2 segundos

            # Llamar a la función para preguntar si desea guardar el puntaje
            await input_nombre(score)
            running = False

        pygame.display.flip()
        await asyncio.sleep(0)  # Evitar bloqueo

    # No cerrar Pygame aquí, solo salir de la función
    return
# Ejecutar el menú principal
async def main():
    await main_menu()

if __name__ == "__main__":
    asyncio.run(main())