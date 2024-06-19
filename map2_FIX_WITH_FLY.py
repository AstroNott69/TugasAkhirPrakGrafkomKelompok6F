from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import subprocess

app = Ursina()
window.fullscreen = False
window.color = color.black
is_flying = False
jump_force = 35  # Increase this value to make the player jump higher
max_fall_height = -20

FONT = "gui_assets/font/PixelOperatorMono8-Bold.ttf"

player = FirstPersonController(collider='box', speed=470, jump_duration=5)
player.gravity = 0.8
player.cursor.visible = True
player.position = (0, 1, 0)
player.rotation_y = 180  # Make the player face the opposite direction

# ground = Entity(model='plane', texture='grass', collider='mesh', scale=(30, 0, 3))
island = Entity(model="gui_assets/level/floatingisland_only_NEW.obj", position=(135, -60, 300), collider='mesh', scale=1, texture="gui_assets/level/level.png", shader=basic_lighting_shader, double_sided=True)
background = Entity(model="gui_assets/level/eye_long_NEWwwwwwwwwww.obj", position=(0, -4350, -500), scale=10, double_sided=True, texture="gui_assets/level/eyenew_sharpened.jpeg" )
finish = Entity(model="Finish_Line.obj", position=(134.5, -60, 310), scale=1, double_sided=True, texture="gui_assets/level/finish.png" )
background.rotation_y = -90

# Create a list to store the jumppad entities
jumppads = [
    Entity(model='cube', color=color.red, position=(-11, -6.6, -73), scale=(3, 0.2, 3), collider='box', rotation=(0,40,0)),
    Entity(model='cube', color=color.red, position=(18, -6.20, -130), scale=(3, 0.2, 3), collider='box', rotation=(0, 45, 0)),
    Entity(model='cube', color=color.red, position=(-13, -12.5, -351), scale=(2, 0.2, 2), collider='box',rotation=(0, 50, 0)),  
    Entity(model='cube', color=color.red, position=(52, -12.5, -477.8), scale=(3, 0.2, 3), collider='box', rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(40, -6.7, -756.5), scale=(2, 0.2, 2), collider='box',rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(27, -11, -420), scale=(2, 0.2, 2), collider='box',rotation=(0, -25, 0)),
    Entity(model='cube', color=color.red, position=(35, -4, -630), scale=(2, 0.2, 2), collider='box',rotation=(0, 25, 0)),
    Entity(model='cube', color=color.red, position=(15, -5.5, -558), scale=(2, 0.2, 2), collider='box',rotation=(0, 62, 0)), 
    Entity(model='cube', color=color.red, position=(11, -6.2, -710), scale=(2, 0.2, 2), collider='box',rotation=(0, 40, 0)),       
]

# Finish line entity
finish_line = Entity(model='cube', color=color.clear, position=(-20, 10, -826), scale=(45, 45, 5), collider = 'mesh')

# Finish message
finish_message = Text(text='Congratulations! You finished the game!',font = FONT, origin=(0,0), scale=1, color=color.white)
finish_message.disable()  # Disable initially

# Timer variables
timer_text = Text(text="Time: 01:00", origin=(-2.5, -8.5), scale=2, color=color.white)
timer_seconds = 60  # 1 minute
timer_running = True  # Flag to control the timer

def restart_game():
    global timer_seconds, timer_running, is_flying
    timer_seconds = 60  # Reset timer
    timer_text.text = "Time: 01:00"  # Reset timer display
    finish_message.disable()  # Disable finish message on restart
    player.position = (0, 1, 0)
    player.rotation_y = 180  # Reset player rotation
    player.gravity = 0.8  # Reset gravity if it was changed during flight mode
    player.y_velocity = 0  # Reset any vertical velocity
    player.x_velocity = 0  # Reset any horizontal velocity
    is_flying = False  # Ensure flying mode is disabled
    timer_running = True  # Restart the timer

def load_map1():
    # Use subprocess to launch map1_FIX.py
    subprocess.Popen(["python", "map1_FIX.py"])
    application.quit()  # Close the current game window

def input(key):
    global is_flying
    if key == 't':
        quit()

    if key == 'r':
        restart_game()

    if key == 'f':
        is_flying = not is_flying
        player.gravity = 0 if is_flying else 0.8  # Disable gravity when flying

def update():
    global timer_seconds, timer_running, is_flying

    if timer_running:
        timer_seconds -= time.dt  # Decrement timer

        # Update timer display
        minutes = int(timer_seconds // 60)
        seconds = int(timer_seconds % 60)
        timer_text.text = f"Time: {minutes:01}:{seconds:02}"

        # Check if timer has reached 0
        if timer_seconds <= 0:
            timer_running = False  # Stop the timer
            load_map1()  # Load the next map

    if player.y < max_fall_height and not is_flying:
        restart_game()

    if held_keys['shift']:
        player.gravity = 5
    else:
        player.gravity = 0.8

    # Detect intersection with any of the jumppads
    for jumppad in jumppads:
        if player.intersects(jumppad).hit:
            player.y += jump_force  # Apply jump force
            break  # Ensure only one jump force is applied at a time

    # Detect intersection with the finish line
    if player.intersects(finish_line).hit:
        finish_message.enable()  # Show finish message
        timer_running = False  # Stop the timer
        invoke(lambda: finish_message.disable(), delay=2)  # Hide message after 2 seconds
        invoke(quit, delay=2.5)  # Restart the game after showing the finish message

    if is_flying:
        player.y_velocity = 0  # Ensure no vertical velocity is applied when flying
        player.gravity = 0  # Ensure gravity is disabled
        if held_keys['e']:
            player.position += Vec3(0, 1, 0) * time.dt * 50  # Move up
        if held_keys['q']:
            player.position -= Vec3(0, 1, 0) * time.dt * 50  # Move down

app.run()