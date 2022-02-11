import os
import re
import sys

def convert(fileNumbers, fileLines):
	result = [None] * len(fileNumbers)

	for i in range(0, len(fileNumbers)):
		if fileNumbers[i] is not None:
			result[fileNumbers[i] - 1] = fileLines[i]

	with open('./out.c', 'w') as f:
		for line in result:
			if line is not None:
				print(line, file = f)

def ascii_to_c(path):
	dir = os.listdir(path)
	fileNumbers = []
	fileLines = []

	if path[-1] != '/':
		path = path + '/'

	for file in dir:
		filePath = "{}{}".format(path, file)

		with open(filePath, 'r') as f:
			fileNumber = None
			syntax = ""
			line = f.readline()

			while line:
				if line.startswith('//'):
					useless = re.search(r'\d+', line)
					if useless:
						fileNumber = int(useless.group())
				else:
					syntax += line
				line = f.readline()
			if fileNumber:
				fileNumbers.append(fileNumber)
				fileLines.append(syntax)

	convert(fileNumbers, fileLines)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: python3 ascii_to_c.py  <FOLDER-PATH>")
	else:
		path = sys.argv[1]
		ascii_to_c(path)
