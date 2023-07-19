import pygame
import sys

# Initialize Pygame
pygame.init()
image_folder = './static/repair/'
# Set up some constants
WIDTH, HEIGHT = 1024, 768
FPS = 60

# Set up some colors
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load background image
bg_image = pygame.image.load(image_folder+'factory.png')  # Background image

# Load car image
car_image = pygame.image.load(image_folder+'car.png')  # Car image

# Load component images
component_images = [
    pygame.transform.scale(pygame.image.load(image_folder+'battery.png'), (100, 100)),       # Battery component
    pygame.transform.scale(pygame.image.load(image_folder+'motor.png'), (100, 100)),         # Motor component
    pygame.transform.scale(pygame.image.load(image_folder+'chair.png'), (100, 100)),        # Charging port component
    pygame.transform.scale(pygame.image.load(image_folder+'tire.png'), (100, 100)),         # Chair component
    pygame.transform.scale(pygame.image.load(image_folder+'headlight.png'), (100, 100))     # Wiring system component
]

# Define the titles of the components
component_titles = [
    "Battery",
    "Motor",
    "Charging Port",
    "Tire",
    "Wiring System"
]

# Initialize car status
car_status = 100

# Initialize dragging status
dragging = None

# Game loop
while True:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, component_image in enumerate(component_images):
                if pygame.Rect(10, 10 + i * 110, component_image.get_width(), component_image.get_height()).collidepoint(event.pos):
                    dragging = i
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging is not None and car_rect.collidepoint(event.pos):
                if dragging == 1:  # Adjust the index to match the correct component
                    print("Correct component dragged!")  # Replace with your desired action
            dragging = None

    # Draw the background
    screen.blit(bg_image, (0, 0))

    # Draw the car
    car_rect = car_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(car_image, car_rect)

    # Draw the components with titles
    for i, component_image in enumerate(component_images):
        if dragging == i:
            pos = pygame.mouse.get_pos()
        else:
            pos = (10, 10 + i * 110)  # Adjust the vertical spacing to accommodate the larger component size
        screen.blit(component_image, pos)

        # Draw component title
        font = pygame.font.Font(None, 30)
        text = font.render(component_titles[i], True, RED)
        screen.blit(text, (pos[0] + component_image.get_width() + 10, pos[1]))

    # Draw the status bar
    pygame.draw.rect(screen, RED, (WIDTH - 110, 10, car_status, 20))

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)
