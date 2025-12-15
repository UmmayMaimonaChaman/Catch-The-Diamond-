from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Window dimensions
W_Width, W_Height = 800, 600

# Game state variables
game_state = "playing"  # "playing", "paused", "game_over"
score = 0
diamond_speed = 2.0
last_time = time.time()
new_diamond_timer = 0

# Catcher 
catcher_x = W_Width // 2
catcher_y = 50
catcher_width = 150
catcher_height = 30
catcher_color = [1.0, 1.0, 1.0]

# Diamond
diamond_x = random.randint(50, W_Width - 50)
diamond_y = W_Height - 50
diamond_size = 20
diamond_color = [random.random(), random.random(), random.random()]
diamond_active = True

# Button
button_size = 40
button_y = W_Height - 50

# Mouse state
mouse_x = 0
mouse_y = 0

def find_zone(x1, y1, x2, y2):
    """Find which zone the line is in based on the 8-way symmetry"""
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) >= abs(dy):
        if dx > 0 and dy > 0:
            return 0
        elif dx > 0 and dy < 0:
            return 7
        elif dx < 0 and dy > 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
    else:
        if dx > 0 and dy > 0:
            return 1
        elif dx > 0 and dy < 0:
            return 6
        elif dx < 0 and dy > 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
    
    return 0

def convert_to_zone0(x, y, zone):
    """Convert coordinates from any zone to zone 0"""
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y
    return x, y

def convert_from_zone0(x, y, zone):
    """Convert coordinates from zone 0 back to original zone"""
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y
    return x, y

def midpoint_line(x1, y1, x2, y2):
    """Draw a line using midpoint line drawing algorithm"""
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    
    # Find and convert to zone 0
    zone = find_zone(x1, y1, x2, y2)
    x1_zone0, y1_zone0 = convert_to_zone0(x1, y1, zone)
    x2_zone0, y2_zone0 = convert_to_zone0(x2, y2, zone)
    
    # check kora x1_zone0 < x2_zone0
    if x1_zone0 > x2_zone0:
        x1_zone0, x2_zone0 = x2_zone0, x1_zone0
        y1_zone0, y2_zone0 = y2_zone0, y1_zone0
    
    dx = x2_zone0 - x1_zone0
    dy = y2_zone0 - y1_zone0
    
    # Midpoint algorithm for zone 0
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    
    x = x1_zone0
    y = y1_zone0
    
    points = []
    
    while x <= x2_zone0:
        # Convert back to original zone
        orig_x, orig_y = convert_from_zone0(x, y, zone)
        points.append((orig_x, orig_y))
        
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        
        x += 1
    
    return points

def draw_line_points(x1, y1, x2, y2):
    """Draw a line using midpoint algorithm with GL_POINTS"""
    points = midpoint_line(x1, y1, x2, y2)
    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()

def draw_diamond_points(x, y, size, color):
    """Draw a diamond shape using midpoint lines with GL_POINTS"""
    glColor3f(*color)
    
    # Diamond points
    top = (x, y + size)
    right = (x + size, y)
    bottom = (x, y - size)
    left = (x - size, y)
    
    # diamond akar jonno  using 4 lines
    draw_line_points(top[0], top[1], right[0], right[1])
    draw_line_points(right[0], right[1], bottom[0], bottom[1])
    draw_line_points(bottom[0], bottom[1], left[0], left[1])
    draw_line_points(left[0], left[1], top[0], top[1])

def draw_catcher_points(x, y, width, height, color):
    """Draw the catcher bowl using midpoint lines with GL_POINTS"""
    glColor3f(*color)
    
    # Catcher(shape)
    left = (x - width//2, y)
    right = (x + width//2, y)
    top_left = (x - width//3, y + height//2)
    top_right = (x + width//3, y + height//2)
    
    # Draw catcher using 4 lines
    draw_line_points(left[0], left[1], top_left[0], top_left[1])
    draw_line_points(top_left[0], top_left[1], top_right[0], top_right[1])
    draw_line_points(top_right[0], top_right[1], right[0], right[1])
    draw_line_points(right[0], right[1], left[0], left[1])

def draw_button_points(x, y, size, color, shape="square"):
    """Draw a button with specified shape using GL_POINTS"""
    glColor3f(*color)
    
    if shape == "left_arrow":
        # Left arrow shape
        center = (x, y)
        left = (x - size//2, y)
        top = (x - size//4, y + size//3)
        bottom = (x - size//4, y - size//3)
        
        draw_line_points(center[0], center[1], left[0], left[1])
        draw_line_points(left[0], left[1], top[0], top[1])
        draw_line_points(left[0], left[1], bottom[0], bottom[1])
    
    elif shape == "play_pause":
        # Play/Pause icon
        if game_state == "playing":
            # Pause icon (two straight vertical lines)
            left_x = x - size//4
            right_x = x + size//4
            top_y = y + size//2
            bottom_y = y - size//2
            
            glColor3f(1.0, 1.0, 1.0)
            
            #vertical lines (   hoina :(    )
            draw_line_points(left_x, top_y, left_x, bottom_y)
            draw_line_points(right_x, top_y, right_x, bottom_y)
        else:
            # Play icon (triangle pointing right)
            left = (x - size//3, y - size//3)
            right = (x - size//3, y + size//3)
            top = (x + size//3, y)
            
            # Draw triangle
            draw_line_points(left[0], left[1], top[0], top[1])
            draw_line_points(top[0], top[1], right[0], right[1])
            draw_line_points(right[0], right[1], left[0], left[1])
    
    elif shape == "cross":
        # Cross/X shape
        size_half = size//3
        draw_line_points(x - size_half, y - size_half, x + size_half, y + size_half)
        draw_line_points(x - size_half, y + size_half, x + size_half, y - size_half)

def check_collision(diamond_x, diamond_y, diamond_size, catcher_x, catcher_y, catcher_width, catcher_height):
    """Check collision between diamond and catcher using AABB"""
    diamond_left = diamond_x - diamond_size
    diamond_right = diamond_x + diamond_size
    diamond_top = diamond_y + diamond_size
    diamond_bottom = diamond_y - diamond_size
    
    catcher_left = catcher_x - catcher_width//2
    catcher_right = catcher_x + catcher_width//2
    catcher_top = catcher_y + catcher_height//2
    catcher_bottom = catcher_y - catcher_height//2
    
    return (diamond_left < catcher_right and
            diamond_right > catcher_left and
            diamond_bottom < catcher_top and
            diamond_top > catcher_bottom)

def check_button_click(mouse_x, mouse_y, button_x, button_y, button_size):
    """Check if mouse click is within button bounds"""
    return (abs(mouse_x - button_x) <= button_size//2 and
            abs(mouse_y - button_y) <= button_size//2)

def reset_game():
    """Reset the game state"""
    global score, diamond_speed, diamond_x, diamond_y, diamond_color, diamond_active, game_state, catcher_color, new_diamond_timer
    score = 0
    diamond_speed = 2.0
    diamond_x = random.randint(50, W_Width - 50)
    diamond_y = W_Height - 50
    diamond_color = [random.random(), random.random(), random.random()]
    diamond_active = True
    game_state = "playing"
    catcher_color = [1.0, 1.0, 1.0]  # White
    new_diamond_timer = 0
    print("Starting Over")

def mouse_listener(button, state, x, y):
    """Handle mouse clicks"""
    global mouse_x, mouse_y, game_state, score
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mouse_x = x
        mouse_y = W_Height - y  # Convert to OpenGL coordinates
        
        # Check restart button (left)
        if check_button_click(mouse_x, mouse_y, 50, button_y, button_size):
            reset_game()
        
        # Check play/pause button (middle)
        elif check_button_click(mouse_x, mouse_y, W_Width//2, button_y, button_size):
            if game_state == "playing":
                game_state = "paused"
            elif game_state == "paused":
                game_state = "playing"
        
        # Check exit button (right)
        elif check_button_click(mouse_x, mouse_y, W_Width - 50, button_y, button_size):
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop()

def special_key_listener(key, x, y):
    """Handle special key presses"""
    global catcher_x
    
    if game_state == "playing":
        if key == GLUT_KEY_LEFT:
            catcher_x = max(catcher_width//2, catcher_x - 20)
        elif key == GLUT_KEY_RIGHT:
            catcher_x = min(W_Width - catcher_width//2, catcher_x + 20)

def display():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up orthographic projection
    glViewport(0, 0, W_Width, W_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W_Width, 0, W_Height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw background
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    # Draw buttons
    draw_button_points(50, button_y, button_size, [0.0, 0.8, 0.8], "left_arrow")  # Teal restart
    draw_button_points(W_Width//2, button_y, button_size, [1.0, 0.75, 0.0], "play_pause")  # Amber play/pause
    draw_button_points(W_Width - 50, button_y, button_size, [1.0, 0.0, 0.0], "cross")  # Red exit
    
    # Draw catcher
    draw_catcher_points(catcher_x, catcher_y, catcher_width, catcher_height, catcher_color)
    
    # Draw diamond if active
    if diamond_active:
        draw_diamond_points(diamond_x, diamond_y, diamond_size, diamond_color)
    
    glutSwapBuffers()

def animate():
    """Animation function"""
    global diamond_y, diamond_x, diamond_color, diamond_active, score, diamond_speed, last_time, game_state, catcher_color, new_diamond_timer
    
    current_time = time.time()
    delta_time = current_time - last_time
    
    if game_state == "playing":
        # Update diamond position
        if diamond_active:
            diamond_y -= diamond_speed * delta_time * 60  # Adjust speed based on frame rate
            
            # Check if diamond hits the ground
            if diamond_y - diamond_size <= 0:
                game_state = "game_over"
                diamond_active = False
                catcher_color = [1.0, 0.0, 0.0]  # Red
                print(f"Game Over! Final Score: {score}")
            
            # Check collision with catcher
            elif check_collision(diamond_x, diamond_y, diamond_size, catcher_x, catcher_y, catcher_width, catcher_height):
                score += 1
                print(f"Score: {score}")
                diamond_active = False
                new_diamond_timer = 0.5  # Start timer for new diamond
        
        # Handle new diamond creation timer
        if not diamond_active and new_diamond_timer > 0:
            new_diamond_timer -= delta_time
            if new_diamond_timer <= 0:
                diamond_x = random.randint(50, W_Width - 50)
                diamond_y = W_Height - 50
                diamond_color = [random.random(), random.random(), random.random()]
                diamond_active = True
                diamond_speed += 0.8  # Increase difficulty
    
    last_time = current_time
    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(2.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    wind = glutCreateWindow(b"Catch the Diamonds!")
    
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    
    init()
    glutMainLoop()

main() 
