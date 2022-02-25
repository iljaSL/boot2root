import turtle
import sys

def draw(file):
    skk = turtle.Turtle()
    fileR = open(file, 'r')
    lines = fileR.readlines()

    for line in lines:
        if "Tourne gauche de 90 degrees" in line:
            skk.left(90)
        elif "Avance 50 spaces" in line:
            skk.forward(50)
        elif "Avance 1 spaces" in line:
            skk.forward(1)
        elif "Tourne gauche de 1 degrees" in line:
            skk.left(1)
        elif "Tourne droite de 1 degrees" in line:
            skk.right(1)
        elif "Avance 210 spaces" in line:
            skk.forward(210)
        elif "Recule 210 spaces" in line:
            skk.bk(210)
        elif "Tourne droite de 90 degrees" in line:
            skk.right(90)
        elif "Avance 120 spaces" in line:
            skk.forward(120)
        elif "Tourne droite de 10 degrees" in line:
            skk.right(10)
        elif "Avance 200 spaces" in line:
            skk.forward(200)
        elif "Tourne droite de 150 degrees" in line:
            skk.right(150)
        elif "Recule 100 spaces" in line:
            skk.back(100)
        elif "Tourne droite de 120 degrees" in line:
            skk.right(120)
        elif "Avance 100 spaces" in line:
            skk.forward(100)
        elif "Recule 200 spaces" in line:
            skk.bk(200)
    turtle.done()

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: python3 turtle_draw.py  <PATH-TO-FILE>")
	else:
		file = sys.argv[1]
		draw(file)
