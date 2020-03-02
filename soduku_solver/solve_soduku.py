import sys
import time

start_time = time.time()
input_file = sys.argv[1]


def read_input(filename): #read the input file and check the size of sudoku
	open_file = open(filename,"r").readlines()
	puzzle = []
	for count,lines in enumerate(open_file,1):
		lines_split = lines.split(",")
		puzzle_row = []
		for field in lines_split:
			field = field.replace("\n","")
			if field == "":
				field = 0
			puzzle_row.append(int(field))
		assert len(puzzle_row) == 9, "Row " + str(count) + " has only " + str(len(puzzle_row)) + " entries (9 required)"
		puzzle.append(puzzle_row)
	assert len(puzzle) == 9, "There is only " + str(len(puzzle)) + " rows in the puzzle"
	return (puzzle)


def exit_code(): #exit the code during invalid soduku
	print ("Not a valid soduku")
	print("--- %s seconds ---" % (time.time() - start_time))
	exit()

	
def sanity_check(puzzle): #checks for multiple entries of values in the input puzzle
	for r_count,row in enumerate(puzzle):
		for f_count,field in enumerate(row):
			if field != 0:
			
				count = 0
				for entry in box_value(puzzle,r_count,f_count):
					if field == entry:
						count += 1
				if count == 2:
					exit_code()
				
				count = 0
				for entry in row:
					if field == entry:
						count += 1
				if count == 2:
					exit_code()
					
				count = 0
				for entry in [row[f_count] for row in puzzle]:
					if field == entry:
						count += 1
				if count == 2:
					exit_code()


def box_value(puzzle,r_count,f_count): #the 3X3 box values for a given index to see neighbouring values
	r_block = r_count // 3
	c_block = f_count // 3
	block_dict = {0:[0,1,2],1:[3,4,5],2:[6,7,8]}
	
	block_values = []
	for dict_r_value in block_dict[r_block]:
		for dict_c_value in block_dict[c_block]:
			block_values.append(puzzle[dict_r_value][dict_c_value])
	return block_values
	
	
def get_field_value(puzzle,r_count,f_count,entry_value): #Check a value between 1-9 is valid or not in the field
	for value in range(entry_value,10):
		if value not in puzzle[r_count]:
			row_value = [row[f_count] for row in puzzle]
			if value not in row_value:
				if value not in box_value(puzzle,r_count,f_count):
					return value
	return False


def get_0_index(puzzle): #to get the field with zeros in the puzzle and return the index in a dict format
	position_dict = {}
	for row_count,rows in enumerate(puzzle):
		for field_count,field in enumerate(rows):
			if field == 0:
				position_dict[str(row_count) + ", " + str(field_count)] = 0
	return position_dict


def get_back_track_index(puzzle,position_dict,current_position): #Backtracking the code for changing the entry of previous entry
	x,y = list(position_dict)[current_position].split(",")
	x = int(x)
	y = int(y)
	
	if current_position - 1 == -1:
		exit_code()
		
	if position_dict[list(position_dict)[current_position - 1]] < 9:
		position_dict[list(position_dict)[current_position]] = 0
		puzzle[x][y] = 0
		return (puzzle,current_position - 1,position_dict)
	else:
		position_dict[list(position_dict)[current_position]] = 0
		puzzle[x][y] = 0
		return get_back_track_index(puzzle,position_dict,current_position - 1)


def solve_puzzle(puzzle,position_dict,start_position): #The main solver
	n = 0
	while n < (len(position_dict)):
		x,y = list(position_dict)[n+start_position].split(",")
		x = int(x)
		y = int(y)
		start_value = position_dict[list(position_dict)[n+start_position]]
		current_puzzle_value = get_field_value(puzzle,x,y,start_value)
		if current_puzzle_value != False:
			puzzle[x][y] = current_puzzle_value
			position_dict[list(position_dict)[n+start_position]] = current_puzzle_value
		else:
			return  get_back_track_index(puzzle,position_dict,n+start_position)
		count = 0
		
		#output
		recursion.append(1)
		for rows in puzzle:
			if 0 not in rows:
				count += 1
		if count == 9:
			print ("Total number of steps = " + str(len(recursion)))
			for row in puzzle:
				print (row)
			print("--- %s seconds ---" % (time.time() - start_time))
			exit()
		n += 1

recursion = [] #to calculate number of steps
puzzle = read_input(input_file)
sanity_check(puzzle) #check the input sudoku is correct or not
position_dict = get_0_index(puzzle) #get index where zeros are present and make it into a dict
back_prop_position = 0	 #index to start the program from

while True:
	puzzle,back_prop_position,position_dict = solve_puzzle(puzzle,position_dict,back_prop_position)