import pygame

# Initialize pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# Movement settings for character
flightSpeed = 5
flightPositionX = 20
flightPositionY = 20
flightWidth = 50
flightHeight = 60

# Settings for rotating square
square_size = 100
square_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
square_surface.fill((0, 255, 0))  # Green square
angle = 0  # Initial rotation angle

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key states
    keys = pygame.key.get_pressed()

    # Move character
    if keys[pygame.K_UP]:
        flightPositionY -= flightSpeed
    if keys[pygame.K_DOWN]:
        flightPositionY += flightSpeed
    if keys[pygame.K_LEFT]:
        flightPositionX -= flightSpeed
    if keys[pygame.K_RIGHT]:
        flightPositionX += flightSpeed

    # Rotate square using keys
    if keys[pygame.K_a]:  # Rotate counterclockwise
        angle += 5
    if keys[pygame.K_d]:  # Rotate clockwise
        angle -= 5

    # Clear screen
    screen.fill("black")

    # Draw moving character
    character = pygame.draw.rect(
        screen, (255, 255, 255), (flightPositionX, flightPositionY, flightWidth, flightHeight)
    )

    # Rotate the square
    rotated_square = pygame.transform.rotate(square_surface, angle)
    rect = rotated_square.get_rect(center=(640, 360))  # Centered on screen

    # Draw rotated square
    screen.blit(rotated_square, rect.topleft)

    # Update display
    pygame.display.flip()
    clock.tick(60)  # Limit FPS

pygame.quit()
