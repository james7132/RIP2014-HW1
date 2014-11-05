from util import *
import pygame
import math


class BugAlgorithm:

    def __init__(self, startPosition, goalPosition, obstacles, angleChange):
        self.start = startPosition
        self.goal = goalPosition
        self.obstacles = obstacles
        self.path = []
        self.angleChange = angleChange

    def run(self, maxTimeSteps = 1000):
        raise NotImplementedError()

    def atGoal(self, pos):
        return pos == self.goal

    def collisionCheck(self, point):
        for obstacle in self.obstacles:
            if obstacle.collisionCheck(point):
                return obstacle
        return None

class Bug1(BugAlgorithm):

    def run(self):
        bugPos = self.start
        self.path = [bugPos]
        while not self.atGoal(bugPos):
            currentDirection = (self.goal - bugPos).norm()
            while self.collisionCheck(bugPos + currentDirection) is None and not self.atGoal(bugPos):
                if (self.goal - bugPos).magnitude() <= currentDirection.magnitude():
                    bugPos = self.goal
                    self.path += [bugPos]
                    print bugPos
                    break
                else:
                    bugPos += currentDirection
                    self.path += [bugPos]
                    print bugPos
                    currentDirection = (self.goal - bugPos).norm()
            if self.atGoal(bugPos):
                break
            obstacle = self.collisionCheck(bugPos + currentDirection)
            bugPos, additionalPoints = obstacle.collisionPointSet(bugPos + currentDirection, self.goal)
            self.path += additionalPoints



def main():


    # Define some colors
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    bug_x = [0,0  , 40, 40,5  ,5  ,35 ,35 ,5  ,5 ,35,35,5 ,5 ,35,35 ,5,5 ,35,35,5 ,5,75,75,20,20,75,75,20,20,75,75,20,20 ,75 ,75 ,20 ,20 ,80 ,80]
    bug_y = [0,147,147,140,140,119,119,112,112,91,91,84,84,63,63,56,56,35,35,28,28,7,7 ,42,42,49,49,70,70,77,77,98,98,105,105,126,126,133,133,0 ]
    bug_points = []
    for i in zip(bug_x, bug_y):
        bug_points += [Vector2(i[0], i[1])]


    #Initialize
    start_position = Vector2(25,157)
    goal_position = Vector2(25,17)
    obstacles = [ PolygonObstacle(bug_points) ]
    angle_change = 45

    bug1 = Bug1(start_position, goal_position, obstacles, angle_change)

    pygame.init()

    # Set the width and height of the screen [width, height]
    size = (640, 480)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Bug 1")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Run bug 1
    bug1.run()

    path_to_tuples = []

    for v in bug1.path:
        path_to_tuples.append(v.to_tuple())

    # -------- Main Program Loop -----------
    while not done:
        # --- Main event loop
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop

        # --- Game logic should go here


        # --- Drawing code should go here

        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(WHITE)

        # print bug1.bugPosition.to_tuple()
        # Drawing other objects

        # Draw obstacles if they exist

        # Draw path for bug
        for position in path_to_tuples:
            pygame.draw.circle(screen, GREEN, position, 1, 0)

        # Draw obstacles
        if obstacles:
            for obstacle in obstacles:
                if isinstance(obstacle, RectangleObstacle):
                    pygame.draw.rect(screen, BLACK, pygame.Rect(obstacle.get_position(), obstacle.get_dimensions()))
                elif isinstance(obstacle, CircleObstacle):
                    pygame.draw.circle(screen, BLACK, obstacle.get_position(), obstacle.get_radius(), 0)

        # pygame.draw.circle(screen, GREEN, bug1.bugPosition.to_tuple(), 10, 0)


        # Draw goal for bug
        # pygame.draw.circle(screen, RED, bug1.goalPosition.to_tuple(), 10, 0)

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(60)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()


if __name__ == "__main__":
    main()