import Adafruit_BBIO.GPIO as GPIO
import time


'''
all pins from P9
up dn               car
12 24               11
          a
14 26     __        13
       f |g |b
16 23     --        15
       e |  |c
22 30     --        21
          d
'''

floors = 4
in_type = 3 # up, down and car


button_pins = [["P9_22","P9_16","P9_14","P9_12"], # up
               ["P9_30","P9_23","P9_26","P9_24"], # down
               ["P9_21","P9_15","P9_13","P9_11"]] # car


# dictionary convert segment name to pin name
seven_segment = {
        'a':'P8_11',
        'b':'P8_7',
        'c':'P8_9',
        'd':'P8_13',
        'e':'P8_17',
        'f':'P8_15',
        'g':'P8_19'
        }

numbers = [
        "abcdef", #0
        "bc",     #1
        "abdeg",  #2
        "abcdg",  #3
        "bcfg",   #4
        "acdfg",  #5
        "acdefg", #6
        "abc",    #7
        "abcdefg",#8
        "abcdfg"  #9
        ]

button_data = [[0 for row in range(floors)] for col in range(in_type)]

#a data structure for storing the destination in upward direction and in downward direction. Mix up car and out of car inputs :)
dest=[[0,0,0,0],[0,0,0,0]]
#motion is -1 for down and 1 for up
motion=0
curr_floor=0
but_halt=0

def button_init():
    for i in range(in_type):
        for j in range(floors):
            print button_pins[i][j]
            GPIO.setup(button_pins[i][j], GPIO.IN)

def button_read():
    for i in range(in_type):
        for j in range(floors):
            button_data[i][j] = GPIO.input(button_pins[i][j])
            #print button_pins[i][j], GPIO.input(button_pins[i][j])
    #print button_data



def sevseg_init():
    for s in seven_segment:
        #print s
        #print seven_segment[s]
        GPIO.setup(seven_segment[s], GPIO.OUT)

def sevseg_clr():
    for s in seven_segment:
        #print s
        GPIO.output(seven_segment[s], GPIO.LOW)

def sevseg_set(number_to_disp):
    sevseg_clr()
    if not (0 <= number_to_disp <= 9):
        print 'seven segment display number out of bound'
        return
    seg_to_turn_on = numbers[number_to_disp]
    for s in seg_to_turn_on:
        #print s, seven_segment[s]
        GPIO.output(seven_segment[s],GPIO.HIGH)
'''

button_init()
button_read()
sevseg_init()
sevseg_clr()
for i in range(10):
    print i,
    sevseg_set(i)
    time.sleep(1)
'''

'''
Three states: going up, comming down and stationary
The states define reading the button input,destination input and checking if it needs to halt on the comming floor.
Thus the state machine will according to the motiion of the lift call the state function and then the display funtion.
If button does not provide a halt and dest always is empty then it switches to stationary state else if only one dest in opp dir then hange the state.
'''
def stationary(): #rather the initial condition
	#print "in stationary"
	global button_data,motion,dest,curr_floor
	flag=0
	while True:
		button_read()
		for i in range(in_type):			
			for j in range(floors):
				if button_data[i][j]==0:
					if j>curr_floor:
						dest[0][j]=1	#save up status 
						motion=1
					elif j<curr_floor:
						dest[1][j]=1
						motion=-1
					flag=1
					break
			if flag==1:
				break
		if flag==1:
			break
	
def go_up():
	#print "in up stTE"
	global button_data,motion,dest,curr_floor,but_halt
	flag=0
	while True:
		button_read()
		for i in range(in_type):			
			for j in range(floors):
				if button_data[i][j]==0:
					if i==0: #if halt desired direction is up
						dest[0][j]=1	#set halt floor in the direction
					elif i==2 and j<curr_floor:
						dest[0][j]=1
					else:
						dest[1][j]=1
					flag=1
					break
			if flag==1:
				but_halt=1
				break
			else:
				but_halt=0				
		break

def go_down():
	#print "IN DOWN STATE"	
	global button_data,motion,dest,curr_floor,but_halt
	flag=0
	while True:
		button_read()
		for i in range(in_type):			
			for j in range(floors):
				if button_data[i][j]==0:
					if i==0: #if halt desired direction is up
						dest[0][j]=1	#set halt floor in the direction
					elif i==2 and j>curr_floor:
						dest[0][j]=1
					else:
						dest[1][j]=1
					flag=1
					break
			if flag==1:
				but_halt=1
				break
			else:
				but_halt=0				
		break
'''
This display function is used to display on led,screen and also change dest status.
The state changing done in state machine on basis of but_halt and dest status
'''
def display():
	global button_data,motion,dest,curr_floor,but_halt
	print dest
	if motion==1:
		if curr_floor in range(0,3):
			curr_floor=curr_floor+1
			sevseg_set(curr_floor)
			time.sleep(1)
			if dest[0][curr_floor]==1:
				print "Halted on "+str(curr_floor)
				dest[0][curr_floor]=0
			else:
				print "crossed " +str(curr_floor)
		else:
			sevseg_set(curr_floor)
			time.sleep(1)
	if motion==-1:
		if curr_floor in range(1,4):
			curr_floor=curr_floor-1
			sevseg_set(curr_floor)
			time.sleep(1)
			if dest[1][curr_floor]==1:			
				print "Halted on "+str(curr_floor)
				dest[1][curr_floor]=0
			else:
				print "crossed " +str(curr_floor)
		else:
			sevseg_set(curr_floor)
			time.sleep(1)
	else:
		sevseg_set(curr_floor)
		time.sleep(1)

	#print dest
	

def StateMachine():
	global button_data,motion,dest,curr_floor,but_halt
	if motion==-1:
		go_down()
		display()
		flag=0
		for j in range(0,curr_floor):
			if dest[1][j]==1 or dest[0][j]==1:
				motion=-1
				flag=1
		if flag==0:
			for j in range(curr_floor,floors):
				if dest[1][j]==1 or dest[0][j]==1:
					motion=1
					flag=1
		if flag==0:
			motion=0
	elif motion==1:
		go_up()
		display()
		flag=0
		for j in range(curr_floor,floors):
			if dest[1][j]==1 or dest[0][j]==1:
				motion=1
				flag=1
		if flag==0:
			for j in range(0,curr_floor):
				if dest[1][j]==1 or dest[0][j]==1:
					motion=-1
					flag=1
		if flag==0:
			motion=0
	else:
		stationary()
		display()
		flag=0
		for j in range(0,curr_floor):
			if dest[1][j]==1 or dest[0][j]==1:
				motion=-1
				flag=1
		for j in range(curr_floor,floors):
			if dest[1][j]==1 or dest[0][j]==1:
				motion=1
				flag=1
		if flag==0:
			motion=0

'''
Main execution
'''
button_init()
sevseg_init()
curr_floor=0
sevseg_set(curr_floor)
time.sleep(1)
while True:
	StateMachine()

