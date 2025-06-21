import pygame
import asyncio
import math

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)

# Setup layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aplikasi Menggambar 2D Professional")

# Variabel global
drawing_mode = "titik"
current_color = BLACK
is_drawing = False
start_pos = None
shapes = []
points = []
selected_shape = None
transform_mode = None  # move, rotate, scale, select
is_transforming = False
transform_start_pos = None
original_shape_data = None
thickness = 5
mouse_pos = (0, 0)
undo_stack = []

# Font untuk UI
font = pygame.font.Font(None, 20)
title_font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 16)

class Button:
    def __init__(self, x, y, width, height, text, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active = False
        self.hover = False
        
    def draw(self, screen):
        if self.active:
            color = (100, 150, 255)
        elif self.hover:
            color = (200, 200, 200)
        else:
            color = (150, 150, 150)
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class ShapeButton(Button):
    def __init__(self, x, y, width, height, shape_type):
        super().__init__(x, y, width, height, "")
        self.shape_type = shape_type
        
    def draw(self, screen):
        if self.active:
            color = (100, 150, 255)
        elif self.hover:
            color = (200, 200, 200)
        else:
            color = (150, 150, 150)
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        if self.shape_type == "titik":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 4)
        elif self.shape_type == "garis":
            pygame.draw.line(screen, BLACK, 
                           (center_x - 12, center_y + 8), 
                           (center_x + 12, center_y - 8), 3)
        elif self.shape_type == "persegi":
            pygame.draw.rect(screen, BLACK, 
                           (center_x - 10, center_y - 8, 20, 16), 2)
        elif self.shape_type == "lingkaran":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 10, 2)
        elif self.shape_type == "ellipse":
            pygame.draw.ellipse(screen, BLACK, 
                              (center_x - 12, center_y - 8, 24, 16), 2)
        elif self.shape_type == "titik_sambung":
            points = [(center_x - 10, center_y + 5), 
                     (center_x - 5, center_y - 8), 
                     (center_x + 5, center_y + 2), 
                     (center_x + 10, center_y - 5)]
            pygame.draw.lines(screen, BLACK, False, points, 2)

class ColorButton(Button):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, size, size, "", color)
        self.button_color = color
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.button_color, self.rect)
        
        if self.active:
            pygame.draw.rect(screen, WHITE, self.rect, 4)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
        else:
            pygame.draw.rect(screen, BLACK, self.rect, 1)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        
    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)
        
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 8, self.rect.y - 5, 16, 30)
        pygame.draw.rect(screen, DARK_GRAY, handle_rect)
        
        text = f"{self.label}: {self.val}"
        if self.label == "Thickness":
            text += "px"
            
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) or \
               pygame.Rect(self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width - 8, 
                          self.rect.y - 5, 16, 30).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            ratio = max(0, min(1, rel_x / self.rect.width))
            self.val = int(self.min_val + ratio * (self.max_val - self.min_val))

# UI Elements
drawing_tools = [
    ShapeButton(20, 50, 50, 40, "titik"),
    ShapeButton(80, 50, 50, 40, "garis"),
    ShapeButton(140, 50, 50, 40, "persegi"),
    ShapeButton(200, 50, 50, 40, "lingkaran"),
    ShapeButton(260, 50, 50, 40, "ellipse"),
    ShapeButton(320, 50, 60, 40, "titik_sambung")
]

transform_tools = [
    Button(20, 110, 50, 30, "Select"),
    Button(80, 110, 50, 30, "Move"),
    Button(140, 110, 50, 30, "Rotate"),
    Button(200, 110, 50, 30, "Scale")
]

colors_list = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, PINK, WHITE]
color_buttons = []
for i, color in enumerate(colors_list):
    x = 400 + (i % 5) * 40
    y = 50 + (i // 5) * 40
    color_buttons.append(ColorButton(x, y, 35, color))

thickness_slider = Slider(700, 80, 150, 1, 20, 5, "Thickness")

clear_button = Button(900, 50, 80, 30, "Clear All")
undo_button = Button(900, 90, 80, 30, "Undo")

# Set defaults
drawing_tools[0].active = True
color_buttons[0].active = True

def save_state():
    """Save current state to undo stack"""
    global undo_stack
    undo_stack.append([shape.copy() for shape in shapes])
    if len(undo_stack) > 50:  # Limit undo history
        undo_stack.pop(0)

def get_shape_center(shape):
    """Get center point of a shape"""
    if shape['type'] == 'titik':
        return shape['pos']
    elif shape['type'] == 'garis':
        return ((shape['start'][0] + shape['end'][0]) // 2,
                (shape['start'][1] + shape['end'][1]) // 2)
    elif shape['type'] in ['persegi', 'ellipse']:
        return ((shape['start'][0] + shape['end'][0]) // 2,
                (shape['start'][1] + shape['end'][1]) // 2)
    elif shape['type'] == 'lingkaran':
        return shape['start']
    elif shape['type'] == 'titik_sambung':
        if shape['points']:
            x = sum(p[0] for p in shape['points']) // len(shape['points'])
            y = sum(p[1] for p in shape['points']) // len(shape['points'])
            return (x, y)
    return (0, 0)

def rotate_point_around_center(point, center, angle_degrees):
    """Rotate point around center"""
    angle_rad = math.radians(angle_degrees)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    
    x = point[0] - center[0]
    y = point[1] - center[1]
    
    new_x = x * cos_angle - y * sin_angle
    new_y = x * sin_angle + y * cos_angle
    
    return (int(new_x + center[0]), int(new_y + center[1]))

def move_shape(shape, dx, dy):
    """Move shape by dx, dy"""
    if shape['type'] == 'titik':
        shape['pos'] = (shape['pos'][0] + dx, shape['pos'][1] + dy)
    elif shape['type'] == 'garis':
        shape['start'] = (shape['start'][0] + dx, shape['start'][1] + dy)
        shape['end'] = (shape['end'][0] + dx, shape['end'][1] + dy)
    elif shape['type'] in ['persegi', 'ellipse', 'lingkaran']:
        shape['start'] = (shape['start'][0] + dx, shape['start'][1] + dy)
        shape['end'] = (shape['end'][0] + dx, shape['end'][1] + dy)
    elif shape['type'] == 'titik_sambung':
        shape['points'] = [(p[0] + dx, p[1] + dy) for p in shape['points']]

def rotate_shape_to_mouse(shape, mouse_pos):
    """Rotate shape to follow mouse position"""
    center = get_shape_center(shape)
    
    # Calculate angle from center to mouse
    dx = mouse_pos[0] - center[0]
    dy = mouse_pos[1] - center[1]
    angle = math.degrees(math.atan2(dy, dx))
    
    # Restore original shape first
    if original_shape_data:
        for key, value in original_shape_data.items():
            shape[key] = value.copy() if isinstance(value, list) else value
    
    # Apply rotation
    if shape['type'] == 'garis':
        shape['start'] = rotate_point_around_center(shape['start'], center, angle)
        shape['end'] = rotate_point_around_center(shape['end'], center, angle)
    elif shape['type'] in ['persegi', 'ellipse']:
        shape['start'] = rotate_point_around_center(shape['start'], center, angle)
        shape['end'] = rotate_point_around_center(shape['end'], center, angle)
    elif shape['type'] == 'lingkaran':
        shape['end'] = rotate_point_around_center(shape['end'], center, angle)
    elif shape['type'] == 'titik_sambung':
        shape['points'] = [rotate_point_around_center(p, center, angle) for p in shape['points']]

def scale_shape_to_mouse(shape, mouse_pos):
    """Scale shape based on mouse distance from center"""
    center = get_shape_center(shape)
    
    # Calculate scale factor based on mouse distance
    current_dist = math.sqrt((mouse_pos[0] - center[0])**2 + (mouse_pos[1] - center[1])**2)
    original_dist = math.sqrt((transform_start_pos[0] - center[0])**2 + (transform_start_pos[1] - center[1])**2)
    
    if original_dist > 0:
        scale_factor = current_dist / original_dist
        scale_factor = max(0.1, min(5.0, scale_factor))  # Limit scale
        
        # Restore original shape first
        if original_shape_data:
            for key, value in original_shape_data.items():
                shape[key] = value.copy() if isinstance(value, list) else value
        
        # Apply scaling
        if shape['type'] == 'garis':
            start_offset = (shape['start'][0] - center[0], shape['start'][1] - center[1])
            end_offset = (shape['end'][0] - center[0], shape['end'][1] - center[1])
            
            shape['start'] = (int(center[0] + start_offset[0] * scale_factor),
                            int(center[1] + start_offset[1] * scale_factor))
            shape['end'] = (int(center[0] + end_offset[0] * scale_factor),
                          int(center[1] + end_offset[1] * scale_factor))
                          
        elif shape['type'] in ['persegi', 'ellipse', 'lingkaran']:
            start_offset = (shape['start'][0] - center[0], shape['start'][1] - center[1])
            end_offset = (shape['end'][0] - center[0], shape['end'][1] - center[1])
            
            shape['start'] = (int(center[0] + start_offset[0] * scale_factor),
                            int(center[1] + start_offset[1] * scale_factor))
            shape['end'] = (int(center[0] + end_offset[0] * scale_factor),
                          int(center[1] + end_offset[1] * scale_factor))
                          
        elif shape['type'] == 'titik_sambung':
            new_points = []
            for point in shape['points']:
                offset = (point[0] - center[0], point[1] - center[1])
                new_point = (int(center[0] + offset[0] * scale_factor),
                           int(center[1] + offset[1] * scale_factor))
                new_points.append(new_point)
            shape['points'] = new_points

def find_shape_at_pos(pos):
    """Find shape at position"""
    for i, shape in enumerate(reversed(shapes)):
        actual_index = len(shapes) - 1 - i
        
        if shape['type'] == 'titik':
            if math.sqrt((pos[0] - shape['pos'][0])**2 + (pos[1] - shape['pos'][1])**2) <= 15:
                return actual_index
                
        elif shape['type'] == 'garis':
            start, end = shape['start'], shape['end']
            if point_line_distance(pos, start, end) <= 15:
                return actual_index
                
        elif shape['type'] in ['persegi', 'ellipse']:
            x = min(shape['start'][0], shape['end'][0])
            y = min(shape['start'][1], shape['end'][1])
            w = abs(shape['end'][0] - shape['start'][0])
            h = abs(shape['end'][1] - shape['start'][1])
            if x - 10 <= pos[0] <= x + w + 10 and y - 10 <= pos[1] <= y + h + 10:
                return actual_index
                
        elif shape['type'] == 'lingkaran':
            center = shape['start']
            radius = int(math.sqrt((shape['end'][0] - center[0])**2 + (shape['end'][1] - center[1])**2))
            distance = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            if abs(distance - radius) <= 15 or distance <= radius:
                return actual_index
                
        elif shape['type'] == 'titik_sambung':
            for point in shape['points']:
                if math.sqrt((pos[0] - point[0])**2 + (pos[1] - point[1])**2) <= 15:
                    return actual_index
                    
    return None

def point_line_distance(point, line_start, line_end):
    """Calculate distance from point to line"""
    A = point[1] - line_start[1]
    B = line_start[0] - point[0]
    C = point[0] * line_start[1] - line_start[0] * point[1]
    return abs(A * line_end[0] + B * line_end[1] + C) / math.sqrt(A**2 + B**2 + 1e-10)

def copy_shape_data(shape):
    """Create deep copy of shape data"""
    copied = {}
    for key, value in shape.items():
        if isinstance(value, list):
            copied[key] = value.copy()
        else:
            copied[key] = value
    return copied

def draw_ui():
    # Header background
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 180)
    pygame.draw.rect(screen, (240, 240, 240), header_rect)
    pygame.draw.line(screen, BLACK, (0, 180), (SCREEN_WIDTH, 180), 2)
    
    # Title
    title_text = title_font.render("Aplikasi Menggambar 2D Professional", True, BLACK)
    screen.blit(title_text, (20, 15))
    
    # Labels
    tools_label = font.render("Drawing Tools", True, BLACK)
    screen.blit(tools_label, (20, 30))
    
    transform_label = font.render("Transform Tools", True, BLACK)
    screen.blit(transform_label, (20, 95))
    
    colors_label = font.render("Colors", True, BLACK)
    screen.blit(colors_label, (400, 30))
    
    # Draw buttons
    for button in drawing_tools + transform_tools + color_buttons:
        button.draw(screen)
    
    thickness_slider.draw(screen)
    clear_button.draw(screen)
    undo_button.draw(screen)
    
    # Current mode info
    mode_text = f"Mode: {drawing_mode.title()}"
    if transform_mode:
        mode_text += f" | Transform: {transform_mode.title()}"
    if selected_shape is not None:
        mode_text += f" | Selected: Shape {selected_shape + 1}"
        
    info_surface = font.render(mode_text, True, BLACK)
    screen.blit(info_surface, (20, 150))
    
    # Mouse coordinates - always visible
    coord_text = f"Mouse: ({mouse_pos[0]}, {mouse_pos[1]})"
    coord_surface = small_font.render(coord_text, True, BLACK)
    screen.blit(coord_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25))
    
    # Instructions
    if selected_shape is not None and transform_mode:
        if transform_mode == "move":
            instruction = "Klik dan drag untuk memindahkan objek"
        elif transform_mode == "rotate":
            instruction = "Klik dan gerakkan mouse untuk merotasi objek"
        elif transform_mode == "scale":
            instruction = "Klik dan gerakkan mouse untuk mengubah ukuran objek"
        else:
            instruction = "Objek terpilih - pilih tool transform"
            
        inst_surface = small_font.render(instruction, True, DARK_GRAY)
        screen.blit(inst_surface, (20, SCREEN_HEIGHT - 45))

def draw_shapes():
    for i, shape in enumerate(shapes):
        shape_type = shape['type']
        color = shape['color']
        thickness_val = shape.get('thickness', 2)
        
        # Highlight selected shape
        is_selected = (i == selected_shape)
        
        if shape_type == 'titik':
            pygame.draw.circle(screen, color, shape['pos'], max(3, thickness_val))
            if is_selected:
                pygame.draw.circle(screen, RED, shape['pos'], max(3, thickness_val) + 5, 2)
                
        elif shape_type == 'garis':
            pygame.draw.line(screen, color, shape['start'], shape['end'], thickness_val)
            if is_selected:
                pygame.draw.line(screen, RED, shape['start'], shape['end'], thickness_val + 4)
                pygame.draw.circle(screen, RED, shape['start'], 5)
                pygame.draw.circle(screen, RED, shape['end'], 5)
                
        elif shape_type == 'persegi':
            x = min(shape['start'][0], shape['end'][0])
            y = min(shape['start'][1], shape['end'][1])
            width = abs(shape['end'][0] - shape['start'][0])
            height = abs(shape['end'][1] - shape['start'][1])
            pygame.draw.rect(screen, color, (x, y, width, height), thickness_val)
            if is_selected:
                pygame.draw.rect(screen, RED, (x-3, y-3, width+6, height+6), 2)
                
        elif shape_type == 'lingkaran':
            radius = int(math.sqrt((shape['end'][0] - shape['start'][0])**2 + 
                                 (shape['end'][1] - shape['start'][1])**2))
            if radius > 0:
                pygame.draw.circle(screen, color, shape['start'], radius, thickness_val)
                if is_selected:
                    pygame.draw.circle(screen, RED, shape['start'], radius + 3, 2)
                    pygame.draw.circle(screen, RED, shape['start'], 5)
                    
        elif shape_type == 'ellipse':
            x = min(shape['start'][0], shape['end'][0])
            y = min(shape['start'][1], shape['end'][1])
            width = abs(shape['end'][0] - shape['start'][0])
            height = abs(shape['end'][1] - shape['start'][1])
            if width > 2 and height > 2:
                pygame.draw.ellipse(screen, color, (x, y, width, height), thickness_val)
                if is_selected:
                    pygame.draw.ellipse(screen, RED, (x-3, y-3, width+6, height+6), 2)
                    
        elif shape_type == 'titik_sambung':
            if len(shape['points']) > 1:
                pygame.draw.lines(screen, color, False, shape['points'], thickness_val)
            for point in shape['points']:
                pygame.draw.circle(screen, color, point, max(2, thickness_val//2))
            if is_selected:
                for point in shape['points']:
                    pygame.draw.circle(screen, RED, point, max(2, thickness_val//2) + 3, 2)

def draw_temp_shape(mouse_pos):
    if not is_drawing or not start_pos:
        return
        
    if drawing_mode == "garis":
        pygame.draw.line(screen, current_color, start_pos, mouse_pos, thickness)
    elif drawing_mode == "persegi":
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        width = abs(mouse_pos[0] - start_pos[0])
        height = abs(mouse_pos[1] - start_pos[1])
        pygame.draw.rect(screen, current_color, (x, y, width, height), thickness)
    elif drawing_mode == "lingkaran":
        radius = int(math.sqrt((mouse_pos[0] - start_pos[0])**2 + 
                             (mouse_pos[1] - start_pos[1])**2))
        if radius > 0:
            pygame.draw.circle(screen, current_color, start_pos, radius, thickness)
    elif drawing_mode == "ellipse":
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        width = abs(mouse_pos[0] - start_pos[0])
        height = abs(mouse_pos[1] - start_pos[1])
        if width > 2 and height > 2:
            pygame.draw.ellipse(screen, current_color, (x, y, width, height), thickness)

async def main():
    global is_drawing, start_pos, shapes, points, selected_shape, transform_mode
    global is_transforming, transform_start_pos, original_shape_data, thickness
    global drawing_mode, current_color, mouse_pos, undo_stack
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover states
        for button in drawing_tools + transform_tools:
            button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle slider
                thickness_slider.handle_event(event)
                thickness = thickness_slider.val
                
                # UI area clicks
                if mouse_pos[1] < 180:
                    # Drawing tools
                    for i, button in enumerate(drawing_tools):
                        if button.is_clicked(mouse_pos):
                            for b in drawing_tools:
                                b.active = False
                            button.active = True
                            modes = ["titik", "garis", "persegi", "lingkaran", "ellipse", "titik_sambung"]
                            drawing_mode = modes[i]
                            transform_mode = None
                            selected_shape = None
                            break
                    
                    # Transform tools
                    for i, button in enumerate(transform_tools):
                        if button.is_clicked(mouse_pos):
                            for b in transform_tools:
                                b.active = False
                            button.active = True
                            modes = ["select", "move", "rotate", "scale"]
                            transform_mode = modes[i]
                            break
                    
                    # Colors
                    for button in color_buttons:
                        if button.is_clicked(mouse_pos):
                            for b in color_buttons:
                                b.active = False
                            button.active = True
                            current_color = button.button_color
                            break
                    
                    # Other buttons
                    if clear_button.is_clicked(mouse_pos):
                        save_state()
                        shapes = []
                        points = []
                        selected_shape = None
                        is_transforming = False
                    elif undo_button.is_clicked(mouse_pos) and undo_stack:
                        shapes = undo_stack.pop()
                        selected_shape = None
                        is_transforming = False
                        
                else:
                    # Canvas area
                    if transform_mode in ["select", "move", "rotate", "scale"]:
                        clicked_shape = find_shape_at_pos(mouse_pos)
                        
                        if clicked_shape is not None:
                            selected_shape = clicked_shape
                            
                            if transform_mode in ["move", "rotate", "scale"]:
                                is_transforming = True
                                transform_start_pos = mouse_pos
                                original_shape_data = copy_shape_data(shapes[selected_shape])
                        else:
                            selected_shape = None
                            is_transforming = False
                            
                    else:
                        # Drawing mode
                        save_state()
                        if drawing_mode == "titik":
                            shapes.append({
                                'type': 'titik',
                                'pos': mouse_pos,
                                'color': current_color,
                                'thickness': thickness
                            })
                        elif drawing_mode == "titik_sambung":
                            points.append(mouse_pos)
                        else:
                            is_drawing = True
                            start_pos = mouse_pos
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                thickness_slider.handle_event(event)
                
                if is_drawing and start_pos and mouse_pos[1] >= 180:
                    shape_data = {
                        'color': current_color,
                        'thickness': thickness
                    }
                    
                    if drawing_mode == "garis":
                        shape_data.update({
                            'type': 'garis',
                            'start': start_pos,
                            'end': mouse_pos
                        })
                    elif drawing_mode == "persegi":
                        shape_data.update({
                            'type': 'persegi',
                            'start': start_pos,
                            'end': mouse_pos
                        })
                    elif drawing_mode == "lingkaran":
                        shape_data.update({
                            'type': 'lingkaran',
                            'start': start_pos,
                            'end': mouse_pos
                        })
                    elif drawing_mode == "ellipse":
                        shape_data.update({
                            'type': 'ellipse',
                            'start': start_pos,
                            'end': mouse_pos
                        })
                        
                    shapes.append(shape_data)
                    
                is_drawing = False
                is_transforming = False
                start_pos = None
                transform_start_pos = None
                original_shape_data = None
                    
            elif event.type == pygame.MOUSEMOTION:
                thickness_slider.handle_event(event)
                
                # Real-time transformations
                if is_transforming and selected_shape is not None and mouse_pos[1] >= 180:
                    if transform_mode == "move":
                        if transform_start_pos:
                            dx = mouse_pos[0] - transform_start_pos[0]
                            dy = mouse_pos[1] - transform_start_pos[1]
                            
                            # Restore original position
                            if original_shape_data:
                                for key, value in original_shape_data.items():
                                    shapes[selected_shape][key] = value.copy() if isinstance(value, list) else value
                            
                            # Apply movement
                            move_shape(shapes[selected_shape], dx, dy)
                            
                    elif transform_mode == "rotate":
                        rotate_shape_to_mouse(shapes[selected_shape], mouse_pos)
                        
                    elif transform_mode == "scale":
                        scale_shape_to_mouse(shapes[selected_shape], mouse_pos)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and drawing_mode == "titik_sambung" and points:
                    save_state()
                    shapes.append({
                        'type': 'titik_sambung',
                        'points': points.copy(),
                        'color': current_color,
                        'thickness': thickness
                    })
                    points = []
                elif event.key == pygame.K_ESCAPE:
                    points = []
                    is_drawing = False
                    is_transforming = False
                    start_pos = None
                    selected_shape = None
                    transform_mode = None
                elif event.key == pygame.K_d:  # D key to deselect
                    selected_shape = None
                    is_transforming = False
        
        # Clear screen
        screen.fill(WHITE)
        
        # Draw shapes
        draw_shapes()
        
        # Draw temporary polyline
        if drawing_mode == "titik_sambung" and points:
            if len(points) > 1:
                pygame.draw.lines(screen, current_color, False, points, thickness)
            for point in points:
                pygame.draw.circle(screen, current_color, point, max(2, thickness//2))
                
            # Show preview line to mouse
            if points:
                pygame.draw.line(screen, (128, 128, 128), points[-1], mouse_pos, 1)
        
        # Draw temporary shape while drawing
        if is_drawing and mouse_pos[1] >= 180:
            draw_temp_shape(mouse_pos)
        
        # Draw UI
        draw_ui()
        
        pygame.display.flip()
        clock.tick(60)
        
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())