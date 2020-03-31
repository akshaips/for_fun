import numpy as np
import matplotlib.pyplot as plt
import random
import copy
import math
from operator import itemgetter
import warnings
warnings.filterwarnings("ignore")

random.seed(0)
colony_count = 6
individual_count = 100
simulation_days = 50

##############################
#epidemic parameters
alpha = 0.5
beta = 1/7
contact_radius = 7
recovery_days = 15
travel_probability = 0.1
lockdown_count = 30
initial_infect_probability = 0.05
social_distance_count = 30
min_box = -100
max_box = 100
movement_step_size = 5

def init_colony(colony_count,individual_count):
    box = {"xmin": min_box, "xmax": max_box, "ymin": min_box, "ymax": max_box}
    colonies = []
    for colony in range(colony_count):
        colonies.append(init_coordinates(individual_count,box))
    return (colonies)

def init_coordinates(individual_count,box):
    coord_list = []
    for individual in range(individual_count):
        initial_infect = random.random()
        if initial_infect <= initial_infect_probability:
            coord_list.append({"person": str(individual), "x": random.uniform(box["xmin"], box["xmax"]),
                               "y": random.uniform(box["ymin"], box["ymax"]), "state": "I", "colour": "red","days":0})
        else:
            coord_list.append({"person":str(individual),"x":random.uniform(box["xmin"],box["xmax"]),"y":random.uniform(box["ymin"],box["ymax"]),"state":"S","colour":"blue","days":0,"travel_ban":0})
    return (coord_list)

def infect(alpha,individual,colony,contact_radius_square):
    for person in colony:
        if person["state"] == "I":
            distance = (person["x"] - individual["x"])**2 + (person["y"] - individual["y"])**2
            if distance <= contact_radius_square:
                infect_chance = random.random()
                if infect_chance <= alpha:
                    return True

def recovered(beta):
    recovered_chance = random.random()
    if recovered_chance <= beta:
        return True

def move_individual(individual,restriction = 1):
    movement_step = movement_step_size * restriction
    xmove = random.uniform(-movement_step,movement_step)
    ymove = random.uniform(-movement_step,movement_step)
    if individual["x"] + xmove >= max_box:
        xmove -= (abs(individual["x"] + xmove) - max_box)
    elif individual["x"] + xmove <= min_box:
        xmove += (abs(individual["x"] + xmove) - max_box)

    if individual["y"] + ymove >= max_box:
        ymove -= (abs(individual["y"] + ymove) - max_box)
    elif individual["y"] + ymove <= min_box:
        ymove += (abs(individual["y"] + ymove) - max_box)

    individual["x"] += xmove
    individual["y"] += ymove
    if individual["x"] > max_box or individual["x"] < min_box:
        print (individual["x"],1)
    return individual

def calc_cost(distance_list):
    return lambda coord_list: np.sum(1 / (np.sum((distance_list - coord_list) ** (2), axis=1) ** (0.5)))

def social_distance_move(individual,colony):

    distance_list = []
    for person in colony:
        distance = ((person["x"] - individual["x"])**2 + (person["x"] - individual["x"])**2)**(0.5)
        if distance < (contact_radius * 1.1) + movement_step_size and distance != 0:
            distance_list.append([person["x"],person["y"]])

    distance_list = np.array(distance_list)

    movement_step = movement_step_size * 0.3

    x_coordinates = individual["x"] + np.arange(-movement_step,movement_step,movement_step*0.1)
    x_coordinates = x_coordinates[(x_coordinates > min_box) & (x_coordinates < max_box)]

    y_coordinates = individual["y"] + np.arange(-movement_step,movement_step,movement_step*0.1)
    y_coordinates = y_coordinates[(y_coordinates > min_box) & (y_coordinates < max_box)]

    xy_coordinates = np.array(np.meshgrid(x_coordinates,y_coordinates)).T.reshape(-1,2)

    if len(distance_list) > 0:
        cost_lambda = calc_cost(distance_list)
        output_coor_list = list(map(cost_lambda,xy_coordinates))
        output_coor = min(enumerate(output_coor_list), key=itemgetter(1))[0]
        x,y = xy_coordinates[output_coor]
    else:
        x = individual["x"]
        y = individual["y"]

    individual["x"] = x
    individual["y"] = y
    return individual

def simulate_colonies(colonies,multiplying_factor,alpha,beta,contact_radius):
    contact_radius_square = contact_radius ** 2

    for colony in colonies:
        for individual in colony:
            infection_count_colony = sum([1 for individual in colony if individual["state"] == "I"])
            recovered_count_colony = sum([1 for individual in colony if individual["state"] == "R"])
            suceptible_count_colony = sum([1 for individual in colony if individual["state"] == "S"])

            if infection_count_colony + recovered_count_colony >= lockdown_count:
                individual["travel_ban"] = 1
            else:
                individual["travel_ban"] = 0

            if individual["state"] == "S":
                if infect(alpha,individual,colony,contact_radius_square):
                    individual["state"] = "I"
                    individual["colour"] = "red"

            elif individual["state"] == "I":
                individual["days"] += 1/multiplying_factor
                if individual["days"] > recovery_days:
                    if recovered(beta):
                        individual["state"] = "R"
                        individual["colour"] = "orange"

            if infection_count_colony + recovered_count_colony <= social_distance_count:
                if recovered_count_colony + suceptible_count_colony == individual_count:
                    individual["colour"] = "blue"
                    individual["state"] = "S"
                move_individual(individual)
            else:
                if recovered_count_colony + suceptible_count_colony == individual_count:
                    individual["colour"] = "blue"
                    individual["state"] = "S"
                    move_individual(individual)
                else:
                    social_distance_move(individual, colony)

        if random.random() < travel_probability:
            outgoing = random.randrange(0,len(colonies))
            incoming = random.randrange(0,len(colonies))
            if  outgoing != incoming:
                if colonies[outgoing][0]["travel_ban"] == 0 and colonies[incoming][0]["travel_ban"] == 0:
                    travel_person = random.randrange(0,len(colonies[outgoing]))
                    if colonies[outgoing][travel_person]["state"] == "I":
                        colonies[outgoing][travel_person]["colour"] = "pink"
                    if colonies[outgoing][travel_person]["state"] == "S":
                        colonies[outgoing][travel_person]["colour"] = "green"
                    person = colonies[outgoing].pop(travel_person)
                    colonies[incoming].append(person)

    return (colonies)

def simulate(colony_count,individual_count,simulation_days,alpha,beta,contact_radius):
    multiplying_factor = 24.0
    number_of_frames = int(simulation_days * multiplying_factor)

    frames_list = []
    colonies = init_colony(colony_count,individual_count)
    frames_list.append(copy.deepcopy(colonies))

    for frames in range(number_of_frames):
        if (frames%multiplying_factor) == 0:
            print (frames/multiplying_factor)
        colonies = simulate_colonies(colonies, multiplying_factor, alpha, beta, contact_radius)
        output = copy.deepcopy(colonies)
        frames_list.append(output)
    return (frames_list,multiplying_factor)

def plot():
    simulation,multiplying_factor = simulate(colony_count,individual_count,simulation_days,alpha,beta,contact_radius)

    axis_list = []
    num_rows = math.ceil(colony_count / 3)
    if colony_count == 1:
        fig, ax = plt.subplots()
    else:
        fig, ax = plt.subplots(nrows =num_rows, ncols =3,sharex=True, sharey = True)

    for row in range(num_rows):
        for column in range(3):
            if len(axis_list) < colony_count:
                axis_list.append([int(row), int(column)])

    frames_dict = {}
    for frame_number,frames in enumerate(simulation):
        colony_x = []
        colony_y = []
        colony_colour = []
        SIR_count = []
        for colonies in frames:
            infection_count_colony = sum([1 for individual in colonies if individual["state"] == "I"])
            recovered_count_colony = sum([1 for individual in colonies if individual["state"] == "R"])
            suceptible_count_colony = sum([1 for individual in colonies if individual["state"] == "S"])
            x = []
            y = []
            colour = []
            for individual in colonies:
                x.append(individual["x"])
                y.append(individual["y"])
                colour.append(individual["colour"])
            colony_x.append(x)
            colony_y.append(y)
            colony_colour.append(colour)
            SIR_count.append([suceptible_count_colony,infection_count_colony,recovered_count_colony])
        frames_dict[frame_number] = [colony_x,colony_y,colony_colour,SIR_count]

    for frames in frames_dict:
        dots_list = []
        day = frames // multiplying_factor
        fig.suptitle('Day ' + str(int(day)) + "/" + str(simulation_days))

        for n, axis in enumerate(axis_list):
            colours = ["blue","red","orange"]
            labels = ["Susceptible" ,"Infected","Recovered"]

            if colony_count == 1:
                SIR_count_list = frames_dict[frames][3][0]
                dots = ax.scatter(frames_dict[frames][0][0], frames_dict[frames][1][0], c=frames_dict[frames][2][0])
                ax.axes.xaxis.set_visible(False)
                ax.axes.yaxis.set_visible(False)
                ax.legend([""],[""],loc="upper right",
                                   title="Population " + str(sum(SIR_count_list)) + " \nSusceptible " + str(
                                       SIR_count_list[0]) + "\nInfected " + str(
                                       SIR_count_list[1]) + "\nRecovered " + str(
                                       SIR_count_list[2]))
            elif num_rows == 1:
                SIR_count_list = frames_dict[frames][3][n]
                dots = ax[axis[1]].scatter(frames_dict[frames][0][n], frames_dict[frames][1][n], c=frames_dict[frames][2][n])
                ax[axis[1]].axes.xaxis.set_visible(False)
                ax[axis[1]].axes.yaxis.set_visible(False)
                ax[axis[1]].legend([""],[""],loc="upper right",
                          title="Population " + str(sum(SIR_count_list)) + " \nSusceptible " + str(
                              SIR_count_list[0]) + "\nInfected " + str(SIR_count_list[1]) + "\nRecovered " + str(
                              SIR_count_list[2]))
            else:
                SIR_count_list = frames_dict[frames][3][n]
                dots = ax[axis[0]][axis[1]].scatter(frames_dict[frames][0][n], frames_dict[frames][1][n], c=frames_dict[frames][2][n])
                ax[axis[0]][axis[1]].axes.xaxis.set_visible(False)
                ax[axis[0]][axis[1]].axes.yaxis.set_visible(False)
                ax[axis[0]][axis[1]].legend([""],[""],loc="upper right",
                                   title="Population " + str(sum(SIR_count_list)) + " \nSusceptible " + str(
                                       SIR_count_list[0]) + "\nInfected " + str(
                                       SIR_count_list[1]) + "\nRecovered " + str(
                                       SIR_count_list[2]))

            dots_list.append(dots)
        plt.pause(0.001)
        for entry in dots_list:
            entry.remove()
    plt.show()

    #return frames_dict

plot()
