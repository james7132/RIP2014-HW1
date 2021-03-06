from quad_tree import *
import tkinter as tk
from util import *
import math

class RRT:
	def __init__(self, space, limit, arm, obstacles, start, goal, constrain,  precision): 
		self.space = space
		self.start = start #VectorN(RobotArm.inverseKinematics(start.to_tuple(), arm.l))
		self.goal = goal #VectorN(RobotArm.inverseKinematics(goal.to_tuple(), arm.l))
		self.obstacles = obstacles
		self.qt = QuadTree(space, limit, obstacles, self.start, self.goal)
		self.arm = arm
		self.worldGoal = arm.setQ(goal).getEnd()
		arm.setQ(start)
		self.worldTree = Tree(arm.getEnd(), precision)
		self.configTree = Tree(self.start, precision)
		self.goalApproximation = (1, 1, 0.1)
		self.constrain = constrain

	def grow_baseline(self, step, goalDirected):
		p, c = self.qt.samplePoint(step, goalDirected)
		x = Vector2(p[0], p[1])
		if p and c:
			p = self.adjust(p)
			if p and not self.arm.ArmCollisionCheck(p.components, self.obstacles): 
				# print(p)
				self.qt.addPoint(p)
				new = self.arm.getEnd()
				old = self.arm.setQ(c.components).getEnd()
				self.worldTree.add(new, old)
				self.configTree.add(p, c)
				self.arm.setQ(p)
				return self.worldTree.V[-1], self.worldTree.E[-1], x
		return None, None, None

	def adjust(self, p):
		wp = self.arm.setQ(p.components).getEnd()
		wp = Vector2(wp[0], wp[1])
		circle = CircleObstacle(0,0,wp.magnitude())
		points = circle.raycast(self.constrain.start, self.constrain.move) + circle.raycast(self.constrain.start, self.constrain.move * -1)
		# print(wp, points)
		if points: 
			distances = [ (wp - c).magnitude() for c in points]
			minim = distances.index(min(distances))
			# print(distances, )
			closest = points[minim]
			offset = closest.angle() - wp.angle()
			newp = VectorN( (p.components[0]+offset, ) + tuple(p[1:]) )
			# print( points, offset, self.arm.setQ(newp.components).getEnd(), newp)	
			return newp
		return None

	def goalNear(self, p): 
		if not any(abs(d) > t for d, t in zip(p - self.worldGoal, self.goalApproximation)):
			return True
		return False

	def getPath(self):
		path = [self.goal]
		cur = self.configTree.V[-1]
		while cur: 
			path = [cur.value] + path
			cur = cur.parent
		return path

obstacles = [CircleObstacle(200,225,100)]#, CircleObstacle(150,600,120)]
# obstacles = [RectangleObstacle(200, 220, 1.57, 100, 100)]
obstacles = []
space = ((-2*math.pi,)*3, (4*math.pi,)*3)
rrt = RRT(space, 0.00001, RobotArm((200, 200, 100)), obstacles, VectorN((1.5707, -1.2308, 0)), VectorN((1.5707, 1.2308, 0)), Line(Vector2(0,300), Vector2(1, 300) ), 8 )

xOffset = 500
yOffset = 300
yMax = 700

class App:
	def __init__(self, master, rrt, w, h):
		self.w = w
		self.h = h
		self.master = master
		frame = tk.Frame(master)
		frame.pack()
		self.canvas = tk.Canvas(master, width=w, height=h)
		self.canvas.pack()
		self.master.after(3000, self.animate_search)
		self.draw_world()
		print(rrt.goal)

	def draw_world(self):
		self.canvas.create_line(xOffset, 0, xOffset, self.w)
		self.canvas.create_line(0, yOffset, 1000, yOffset)
		for obstacle in obstacles: 
			self.draw_obstacle(obstacle)
		self.draw_arm(rrt.arm.setQ(rrt.start), "red")
		self.draw_arm(rrt.arm.setQ(rrt.goal), "green")
		self.draw_arm(rrt.arm.setQ(rrt.goal), "green")

	def draw_dot(self, x, y, r): 
		self.canvas.create_oval(x-r + xOffset, y-r + yOffset, x+r + xOffset, y + r + yOffset)

	def draw_line(self, p1, p2):
		self.canvas.create_line(p1[0] + xOffset, p1[1] + yOffset, p2[0] + xOffset, p2[1] + yOffset)

	def draw_obstacle(self, obstacle): 
		if isinstance(obstacle, CircleObstacle):
			r = obstacle.r
			self.canvas.create_oval(obstacle.x-r + xOffset, obstacle.y-r + yOffset , obstacle.x+r + xOffset, obstacle.y+r + yOffset)
		elif isinstance(obstacle, PolygonObstacle):
			points = [VectorN( (xOffset + x.x, yOffset + x.y) ).to_tuple() for x in obstacle.points]
			self.canvas.create_polygon(points);
		elif isinstance(obstacle, RectangleObstacle):
			self.draw_obstacle(obstacle.wrapped)

	def draw_arm(self, arm, color): 
		x = arm.a1[0] + xOffset, arm.a2[0] + xOffset, arm.a3[0] + xOffset
		y = arm.a1[1] + yOffset, arm.a2[1] + yOffset, arm.a3[1] + yOffset
		arm.armLines[0] = self.canvas.create_line(xOffset, yOffset, x[0], y[0], fill=color)
		arm.armLines[1] = self.canvas.create_line(x[0], y[0], x[1], y[1], fill=color)
		arm.armLines[2] = self.canvas.create_line(x[1], y[1], x[2], y[2], fill=color)

	def deleteArm(self, arm): 
		for line in arm.armLines:
			self.canvas.delete(line) 

	def animate_search(self): 
		p, e, x = rrt.grow_baseline(0.05, True)
		# print(p)
		if p:
			self.draw_dot(p.value[0], p.value[1], 1)
			self.draw_line(e.l.value, e.r.value)
			self.deleteArm(rrt.arm)
			self.draw_arm(rrt.arm, "blue")

		if len(rrt.worldTree.V) < 3000 and (not p or not rrt.goalNear(p.value)): 
			self.master.after(10, self.animate_search)
		else: 
			self.path = rrt.getPath()
			self.pos = 0
			self.canvas.delete("all")
			self.draw_world()
			self.master.after(1000, self.animate_movement)

	def animate_movement(self):
		self.deleteArm(rrt.arm)
		self.draw_arm(rrt.arm.setQ(self.path[self.pos]), "blue")
		self.pos+=1
		if self.pos < len(self.path):
			self.master.after(10, self.animate_movement)

	def draw_tree(self, tree): 
		for p in tree.V: 
			self.draw_dot(p.x,p.y,1) 
		for e in tree.E: 
			self.canvas.create_line(e.l.x + xOffset, yMax - (e.l.y + yOffset), e.r.x + xOffset, yMax - (e.r.y + yOffset))

root = tk.Tk()
app = App(root, rrt, 1024, 768)
root.mainloop()
