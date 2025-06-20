import pygame
import asyncio
import math

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Setup layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aplikasi Menggambar")

# Variabel global
drawing_mode = "titik"
current_color = BLACK
is_drawing = False
start_pos = None
shapes = []
points = []
temp_shape = None

# Font untuk UI
font = pygame.font.Font(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active = False
        
    def draw(self, screen):
        # Gambar tombol
        color = (200, 200, 200) if self.active else (150, 150, 150)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Gambar teks
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class ColorButton(Button):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size, "", color)
        self.button_color = color
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.button_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        if self.active:
            pygame.draw.rect(screen, WHITE, self.rect, 4)

# Membuat tombol-tombol
mode_buttons = [
    Button(10, 10, 80, 30, "Titik"),
    Button(100, 10, 80, 30, "Garis"),
    Button(190, 10, 80, 30, "Persegi"),
    Button(280, 10, 80, 30, "Lingkaran"),
    Button(370, 10, 100, 30, "Titik Sambung"),
    Button(480, 10, 80, 30, "Ellipse")
]

color_buttons = [
    ColorButton(10, 50, 30, BLACK),
    ColorButton(50, 50, 30, RED),
    ColorButton(90, 50, 30, GREEN),
    ColorButton(130, 50, 30, BLUE),
    ColorButton(170, 50, 30, YELLOW),
    ColorButton(210, 50, 30, PURPLE),
    ColorButton(250, 50, 30, CYAN)
]

clear_button = Button(700, 10, 80, 30, "Clear")

# Set default active buttons
mode_buttons[0].active = True
color_buttons[0].active = True

def draw_ui():
    # Gambar area UI
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, SCREEN_WIDTH, 90))
    pygame.draw.line(screen, BLACK, (0, 90), (SCREEN_WIDTH, 90), 2)
    
    # Gambar tombol mode
    for button in mode_buttons:
        button.draw(screen)
    
    # Gambar tombol warna
    for button in color_buttons:
        button.draw(screen)
    
    # Gambar tombol clear
    clear_button.draw(screen)

def handle_mode_click(pos):
    global drawing_mode
    for i, button in enumerate(mode_buttons):
        if button.is_clicked(pos):
            # Reset semua tombol
            for b in mode_buttons:
                b.active = False
            button.active = True
            
            # Set mode
            if i == 0:
                drawing_mode = "titik"
            elif i == 1:
                drawing_mode = "garis"
            elif i == 2:
                drawing_mode = "persegi"
            elif i == 3:
                drawing_mode = "lingkaran"
            elif i == 4:
                drawing_mode = "titik_sambung"
            elif i == 5:
                drawing_mode = "ellipse"
            break

def handle_color_click(pos):
    global current_color
    for button in color_buttons:
        if button.is_clicked(pos):
            # Reset semua tombol
            for b in color_buttons:
                b.active = False
            button.active = True
            current_color = button.button_color
            break

def draw_shapes():
    # Gambar semua bentuk yang tersimpan
    for shape in shapes:
        shape_type = shape['type']
        color = shape['color']
        
        if shape_type == 'titik':
            pygame.draw.circle(screen, color, shape['pos'], 3)
        elif shape_type == 'garis':
            pygame.draw.line(screen, color, shape['start'], shape['end'], 2)
        elif shape_type == 'persegi':
            x = min(shape['start'][0], shape['end'][0])
            y = min(shape['start'][1], shape['end'][1])
            width = abs(shape['end'][0] - shape['start'][0])
            height = abs(shape['end'][1] - shape['start'][1])
            pygame.draw.rect(screen, color, (x, y, width, height), 2)
        elif shape_type == 'lingkaran':
            radius = int(math.sqrt((shape['end'][0] - shape['start'][0])**2 + 
                                 (shape['end'][1] - shape['start'][1])**2))
            if radius > 0:
                pygame.draw.circle(screen, color, shape['start'], radius, 2)
        elif shape_type == 'ellipse':
            x = min(shape['start'][0], shape['end'][0])
            y = min(shape['start'][1], shape['end'][1])
            width = abs(shape['end'][0] - shape['start'][0])
            height = abs(shape['end'][1] - shape['start'][1])
            if width > 2 and height > 2:
                pygame.draw.ellipse(screen, color, (x, y, width, height), 2)
        elif shape_type == 'titik_sambung':
            if len(shape['points']) > 1:
                pygame.draw.lines(screen, color, False, shape['points'], 2)
            for point in shape['points']:
                pygame.draw.circle(screen, color, point, 3)

def draw_temp_shape(mouse_pos):
    if not is_drawing or not start_pos:
        return
        
    if drawing_mode == "garis":
        pygame.draw.line(screen, current_color, start_pos, mouse_pos, 2)
    elif drawing_mode == "persegi":
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        width = abs(mouse_pos[0] - start_pos[0])
        height = abs(mouse_pos[1] - start_pos[1])
        pygame.draw.rect(screen, current_color, (x, y, width, height), 2)
    elif drawing_mode == "lingkaran":
        radius = int(math.sqrt((mouse_pos[0] - start_pos[0])**2 + 
                             (mouse_pos[1] - start_pos[1])**2))
        if radius > 0:
            pygame.draw.circle(screen, current_color, start_pos, radius, 2)
    elif drawing_mode == "ellipse":
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        width = abs(mouse_pos[0] - start_pos[0])
        height = abs(mouse_pos[1] - start_pos[1])
        if width > 2 and height > 2:
            pygame.draw.ellipse(screen, current_color, (x, y, width, height), 2)

async def main():
    global is_drawing, start_pos, shapes, points
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Cek klik di area UI
                if mouse_pos[1] < 90:
                    handle_mode_click(mouse_pos)
                    handle_color_click(mouse_pos)
                    
                    if clear_button.is_clicked(mouse_pos):
                        shapes = []
                        points = []
                else:
                    # Area menggambar
                    if drawing_mode == "titik":
                        shapes.append({
                            'type': 'titik',
                            'pos': mouse_pos,
                            'color': current_color
                        })
                    elif drawing_mode == "titik_sambung":
                        points.append(mouse_pos)
                    else:
                        is_drawing = True
                        start_pos = mouse_pos
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if is_drawing and start_pos:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] >= 90:  # Pastikan di area gambar
                        if drawing_mode == "garis":
                            shapes.append({
                                'type': 'garis',
                                'start': start_pos,
                                'end': mouse_pos,
                                'color': current_color
                            })
                        elif drawing_mode == "persegi":
                            shapes.append({
                                'type': 'persegi',
                                'start': start_pos,
                                'end': mouse_pos,
                                'color': current_color
                            })
                        elif drawing_mode == "lingkaran":
                            shapes.append({
                                'type': 'lingkaran',
                                'start': start_pos,
                                'end': mouse_pos,
                                'color': current_color
                            })
                        elif drawing_mode == "ellipse":
                            shapes.append({
                                'type': 'ellipse',
                                'start': start_pos,
                                'end': mouse_pos,
                                'color': current_color
                            })
                    is_drawing = False
                    start_pos = None
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and drawing_mode == "titik_sambung" and points:
                    # Simpan titik sambung
                    shapes.append({
                        'type': 'titik_sambung',
                        'points': points.copy(),
                        'color': current_color
                    })
                    points = []
        
        # Clear screen
        screen.fill(WHITE)
        
        # Gambar shapes
        draw_shapes()
        
        # Gambar titik sambung sementara
        if drawing_mode == "titik_sambung" and points:
            if len(points) > 1:
                pygame.draw.lines(screen, current_color, False, points, 2)
            for point in points:
                pygame.draw.circle(screen, current_color, point, 3)
        
        # Gambar shape sementara saat mouse drag
        if is_drawing:
            mouse_pos = pygame.mouse.get_pos()
            draw_temp_shape(mouse_pos)
        
        # Gambar UI
        draw_ui()
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
        # Yield untuk web
        await asyncio.sleep(0)
    
    pygame.quit()

# Jalankan aplikasi
asyncio.run(main())