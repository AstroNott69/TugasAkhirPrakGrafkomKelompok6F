from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint
import subprocess

app = Ursina()
window.fullscreen = False
window.color = color.black
FONT = "gui_assets/font/PixelOperatorMono8-Bold.ttf"
FONT_death = "gui_assets/font/Garamond-Roman Light.ttf"

# Variables to control game and menu visibility
game_active = False
is_flying = False

# Maximum fall height from which the player is still considered alive
max_fall_height = -10

# Game elements
player = FirstPersonController(collider='box', jump_duration=0.35, speed=50)
player.cursor.visible = True

ground = Entity(model='plane', texture='brick', collider='mesh', scale=(30, 0, 3))
ground = Entity(model='quad', color=color.red, position=(1, 1, -1.5), scale=(40, 5, 3), collider='box')
cube1 = Entity(model="gui_assets/level/eye_fix.obj", texture='eyenew_sharpened.jpeg',scale =(11), position=(-1630,-1350,1540), double_sided=True)
cube1.disable()

pill1 = Entity(model='cube', color=color.red, scale=(0.4, 0.1, 53), z=28, x=-0.7)
pill2 = duplicate(pill1, x=-3.7)
pill3 = duplicate(pill1, x=0.6)
pill4 = duplicate(pill1, x=3.6)

# Function to create random blocks
def create_blocks():
    blocks = []
    for i in range(12):
        block = Entity(model='cube', collider='box', color=color.white33, position=(2, 0.1, 3 + i * 4), scale=(3, 0.1, 2.5))
        block2 = duplicate(block, x=-2.2)
        blocks.append((block, block2, randint(0, 10) > 7, randint(0, 10) > 7))
    return blocks

blocks = create_blocks()

goal = Entity(model='cube', texture='brick', z=55, scale=(10, 1, 10), collider='mesh')

# Create the finish cube and the message entity
finish_cube = Entity(model='cube', color=color.clear, position=(0, 1.5, 57), scale=(10, 1, 10), collider='box')
finish_message = Text(text='You are not Done yet!,it is just the beginning of all!', font=FONT, position=(0, 0), origin=(0, 0), scale=1, color=color.white)
finish_message.disable()  # Disable initially

# Menu elements
title_menu = Text(text='Wanna Play Something Fun?', font="gui_assets/font/PixelOperatorMono8-Bold.ttf", origin=(0, 0), scale=2, position=(0, 0.4))
start_button = Button(text='Ready To Die?', scale=(0.4, 0.1), position=(0, 0.1), on_click=lambda: start_game())
quit_button = Button(text='Wanna Quit Coward?', scale=(0.5, 0.1), position=(0, -0.1), on_click=lambda: quit_game())

start_button.text_entity.font = FONT
quit_button.text_entity.font = FONT

# Create a Panel behind the death message
death_message_background = Panel(scale=(0.5, 0.1), color=color.black66, position=(0, 0))
death_message_background.disable()

# Create a Text object to display the death message
death_message = Text(text='Foolish Player', font="gui_assets/font/Garamond-Roman Light.ttf", position=(0, 0), origin=(0, 0), scale=2, color=color.red)
death_message.disable()  # Disable initially

# Initialize the life count
life = 3

offset_x = 10 # utk membuat health bar jadi berbaris horizontal
# Create image entities for life indicators
life_images = []
for i in range(3):
    life_image = Entity(model='quad', texture='gui_assets/life_heart.png', scale=(10, 10), position=(offset_x + i * 5, 10, 60))
    life_images.append(life_image)

# Function to update life indicators
def update_life_indicators():
    for i, life_image in enumerate(life_images):
        if i < life:
            life_image.enable()
        else:
            life_image.disable()

def start_game():
    global game_active, life
    game_active = True
    life = 3  # Reset life when game starts
    death_message.text = ''  # Clear any previous death message
    death_message_background.disable()  # Disable the background for the death message initially
    death_message.disable()  # Disable death message initially
    cube1.enable()
    

    for e in [title_menu, start_button, quit_button]:
        e.disable()

    for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube]:
        entity.enable()

    for block1, block2, _, _ in blocks:
        block1.enable()
        block2.enable()

    player.position = (0, 1, 0)

    # Enable life indicators
    update_life_indicators()  # This function will enable the appropriate life indicators

def restart_game():
    global game_active
    game_active = False
    death_message.disable()  # Disable death message
    death_message_background.disable()  # Disable the background for the death message
    cube1.disable()
    

    for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube]:
        entity.disable()

    for block1, block2, _, _ in blocks:
        block1.disable()
        block2.disable()

    for life_image in life_images:
        life_image.disable()  # Disable life indicators on the main menu

    title_menu.enable()
    start_button.enable()
    quit_button.enable()
    finish_message.disable()  # Disable finish message on restart
    
def load_map2():
    # Use subprocess to launch map2.py
    subprocess.Popen(["python", "map2_FIX_WITH_FLY.py"])
    application.quit()  # Close the current game window

def player_died():
    global life
    life -= 1
    # Show death message and background
    death_message_background.enable()
    death_message.text = 'FOOLISH PLAYER'
    death_message.enable()
    invoke(lambda: (death_message_background.disable(), setattr(death_message, 'text', ''), death_message.disable()), delay=1.5)  # Clear the message and disable background after 1.5 seconds
   
    if life <= 0:
        invoke(restart_game)
    else:
        update_life_indicators()

def update():
    global game_active
    if game_active:
        # Check if player falls below the maximum fall height
        if player.y < max_fall_height and not is_flying:
            player_died()
            if life > 0:  # If the player still has lives left, reset player position
                player.position = (0, 1, 0)

        block_destroyed = False  # Flag to check if a block has been destroyed

        for block1, block2, k, n in blocks:
            if not block_destroyed:
                if block1.intersects() and k:
                    invoke(destroy, block1, delay=0.1)
                    block1.fade_out(duration=0.1)
                    block_destroyed = True
                elif block2.intersects() and n:
                    invoke(destroy, block2, delay=0.1)
                    block2.fade_out(duration=0.1)
                    block_destroyed = True

        # Check if player touches or lands on the finish cube
        
        if finish_cube.intersects(player):
            finish_message.enable()  # Show finish message
            invoke(finish_message.disable, delay=2)  # Hide message after 2 seconds
            game_active = False
            invoke(restart_game, delay=2.5)  # Restart game after 2.5 seconds
        
        if player.intersects(finish_cube).hit:
            finish_message.enable()
            invoke(load_map2, delay=1.5)  # Load map2 after a short delay

def input(key):
    global is_flying
    
    if key == 'q':
        quit()
    if key == 'f':
        is_flying = not is_flying
        player.gravity = 0 if is_flying else 1  # Disable gravity when flying

    if is_flying:
        if held_keys['e']:
            player.position += Vec3(0, 1, 0) * time.dt * 50  # Move up
        if held_keys['r']:
            player.position -= Vec3(0, 1, 0) * time.dt * 50  # Move down
        
    if key == 't':
        restart_game() 
   
def quit_game():
    application.quit()

# Disable game elements initially
for entity in [player, ground, pill1, pill2, pill3, pill4, goal, finish_cube, cube1]:
    entity.disable()

for block1, block2, _, _ in blocks:
    block1.disable()
    block2.disable()

for life_image in life_images:
    life_image.disable()  # Disable life indicators on the main menu

title_menu.enable()
start_button.enable()
quit_button.enable()

app.run()