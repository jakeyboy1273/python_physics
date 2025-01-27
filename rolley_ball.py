import sys
import math
import pygame
import pymunk
import pymunk.pygame_util


# Create a parabolic bucket
def create_parabola(space, width, height, x_offset, y_offset):
    points = []
    for x in range(-width // 2, width // 2 + 1, 10):
        y = (x ** 2) / (4 * height)
        points.append((x + x_offset, -y + y_offset))

    for i in range(len(points) - 1):
        shape = pymunk.Segment(space.static_body, points[i], points[i + 1], 2)
        shape.elasticity = 0.8
        shape.friction = 0.6
        space.add(shape)


# Create a ball
def create_ball(space, radius, mass, pos):
    body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.8
    shape.friction = 0.6
    space.add(body, shape)
    return body


def __main__():

    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Parabolic Bucket Simulation")

    # Clocks for controlling frame rate
    clock = pygame.time.Clock()
    physics_clock = pygame.time.Clock()

    # Pymunk space for physics simulation
    space = pymunk.Space()
    space.gravity = (0, 980)  # Gravity pointing downward

    # Draw options for rendering
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    font = pygame.font.Font(None, 36)

    # Create the game bodies
    ball = create_ball(space, 20, 10, (WIDTH // 2 + 200, 100))
    create_parabola(space, 600, 100, WIDTH // 2, HEIGHT - 100)

    # Variables for dragging the ball
    selected_ball = None
    mouse_is_dragging = False

    # Main loop
    while True:

        # Handle screen boundary issues
        for body in space.bodies:
            # Check if the ball is outside the bottom boundary
            if body.position.y > HEIGHT:
                body.position = (body.position.x, 0)
                if body.velocity.y > 800:
                    body.velocity = (body.velocity.x, 800)

            # Check if the ball is outside the left boundary
            if body.position.x < 0:
                body.position = (WIDTH, body.position.y)

            # Check if the ball is outside the right boundary
            if body.position.x > WIDTH:
                body.position = (0, body.position.y)

        # Handle mouse drag with momentum
        if mouse_is_dragging and selected_ball:
            current_mouse_pos = pymunk.vec2d.Vec2d(
                pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            )

            # Apply a force proportional to the displacement
            # (this creates "dragging" with momentum)
            if not hasattr(selected_ball, "target_position"):
                selected_ball.target_position = pymunk.vec2d.Vec2d(0, 0)

            # Update target position based on mouse movement
            selected_ball.target_position = current_mouse_pos

            # Calculate the velocity to reach the target position smoothly
            delta = selected_ball.target_position - selected_ball.body.position
            selected_ball.body.velocity = delta * 10

        # Handle mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if mouse is inside the ball
                mouse_pos = pymunk.vec2d.Vec2d(
                    pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                )

                hits = space.point_query(mouse_pos, 10, pymunk.ShapeFilter())
                selected_ball = None

                for hit in reversed(hits):
                    if isinstance(hit.shape, pymunk.shapes.Circle):
                        selected_ball = hit.shape
                        break

                for hit in hits:
                    if hit.shape == selected_ball:
                        mouse_is_dragging = True
                        break  # Once we find the ball, break out of loop

                # If no ball is hit, unselect it (if needed)
                if not any(hit.shape == selected_ball for hit in hits):
                    selected_ball = None

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_is_dragging = False

        # Draw everything
        screen.fill((255, 255, 255))
        space.debug_draw(draw_options)

        # Display the messages
        ball.speed = math.sqrt(ball.velocity.x ** 2 + ball.velocity.y ** 2)
        speed_surface = font.render(
            f"Ball Speed: {ball.speed:.2f} m/s", True, (0, 0, 0)
            )
        fps_surface = font.render(
            f"FPS: {int(clock.get_fps())} Hz", True, (0, 0, 0)
            )
        physics_surface = font.render(
            f"Physics FPS: {int(physics_clock.get_fps())} Hz", True, (0, 0, 0)
            )
        screen.blit(speed_surface, (10, 10))
        screen.blit(fps_surface, (10, 50))
        screen.blit(physics_surface, (10, 90))

        # Update physics simulation
        clock.tick(fps)
        tick_rate = int(ticks/fps)
        for _ in range(tick_rate):
            physics_clock.tick(ticks)
            space.step(1/ticks)

        # Update the display
        pygame.display.flip()


if __name__ == "__main__":
    fps = 60
    ticks = 600
    __main__()
