import pygame

# Initialize Pygame for joystick handling
pygame.init()
pygame.joystick.init()

# Check for connected joysticks
num_joysticks = pygame.joystick.get_count()
if num_joysticks == 0:
    print("No joystick connected!")
    pygame.quit()
    exit()

# Initialize the first joystick (assumed to be the PS4 controller)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick initialized: {joystick.get_name()}")

def print_controller_mappings():
    """Print the state of all buttons and axes for the PS4 controller."""
    while True:
        pygame.event.pump()  # Update the state of the joystick
        
        # Print all axes
        for i in range(joystick.get_numaxes()):
            print(f"Axis {i}: {joystick.get_axis(i)}")
        
        # Print all buttons
        for i in range(joystick.get_numbuttons()):
            print(f"Button {i}: {joystick.get_button(i)}")
        
        # Print all hats (D-pad)
        for i in range(joystick.get_numhats()):
            print(f"Hat {i}: {joystick.get_hat(i)}")
        
        pygame.time.wait(500)  # Wait 500ms before the next reading

if __name__ == '__main__':
    print_controller_mappings()
