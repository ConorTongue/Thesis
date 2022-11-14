import pandas as pd
import numpy as np

#data = pd.read_csv (r'grid_rug_riv_pop.csv')
data = pd.read_csv (r'grid_language_religions.csv')
#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity','national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','temp_min','temp_max'])
#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','uniform_productivity','uniform_national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','temp_min','temp_max'])

#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity','national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion_1450','language_group','temp_min','temp_max'])
#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity','national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness_vrm','religion','language_group','temp_min','temp_max'])
#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity','national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','wc_temp_min','wc_temp_max'])

grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity_gaezv4','national_productivity_gaezv4', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','temp_min','temp_max'])


#initialise results grid
#d1, d2 = (2,3)
d1,d2 = (30,500)
final_herf_grid = [[0 for i in range(d2)] for j in range(d1)]
#print(final_herf_grid)
grid = grid1.to_numpy()
#grab some useful values that will be nice to have stored in memory
n = len(grid)
#print(grid)
final_owner_grid = [[0 for i in range(d2)] for j in range(n)]

max_prod = round(np.amax(grid,axis = 0)[3],3)
#beta = 0.000005
beta = 0
india_cells = 0
sea_cells = 0
for i in range(1,n):
    if grid[i][6] == 1:
        india_cells += 1
    if grid[i][7] == 1:
        sea_cells += 1

#get 90th percentiles
x_rugg_90 = np.percentile(grid[:,13], 90, axis=None, out=None)
#print(x_rugg_90)


c_check = ['conflict','no_conflict']
s_outcomes = ['s','f']
w_outcomes = ['i','c','n'] #owner of cell i, the owner of the cell it comes into conflict with, or no winner
dead_nations = list()
river_penalty = 0
rug_penalty = round(2/(x_rugg_90/max(grid[:,13])),3)
#rug_penalty = round(1/(x_rugg_90/max(grid[:,13])),3)
#rug_penalty = 0

print(rug_penalty)
l_penalty = 2
r_penalty = 2


for repeat in range(1,15 + 1):
    print('current repetition is', repeat)

    grid = grid1.to_numpy()
    #
    #print(grid.values)
    #print(grid.values[1][1])


    #initally go through and round off prod, get climate ready

    for i in range(1,n):
        grid[i][3] = round(grid[i][3],3)
        #print(grid[i][3])
        grid[i][4] = round(grid[i][4],3)
        grid[i][13] = round(grid[i][13],3)
        if grid[i][16] <= 80:
            grid[i][16] = round(np.log(9-(grid[i][16])/10),3)
        else:
            grid[i][16] = 0
        if grid[i][17] >= 220:
            grid[i][17] = round(np.log((grid[i][17]/10)-21),3)
        else:
            grid[i][17] = 0
        #print(grid[i][17])

    hot_rugg_90 = np.percentile(grid[:,17], 90, axis=None, out=None)
    print(hot_rugg_90)
    cold_rugg_90 = np.percentile(grid[:,16], 90, axis=None, out=None)
    hot_penalty = round(2/(hot_rugg_90),3)
    #hot_penalty = 0
    #print('hot penalty is',hot_penalty)
    #cold_penalty = 0
    cold_penalty = round(2/(cold_rugg_90),3)
    for t in range(1,500+1):
        print('Current time is',t)
        for i in range(1,n):
            #print(i)
            if grid[i][11] == 1: # if conflict already occuring here
                #print('already conflict')
                continue
            else: #take note that conflict happens
                grid[i][11] = 1
            #print('Cell i is', i)
            p_conflict = round(grid[i][3]/max_prod,3)
            #p_conflict = 1
            conflict_occur = np.random.choice(c_check, p = [p_conflict, 1-p_conflict])

            #determine if conflict actually occurs
            if conflict_occur == 'conflict':
                #print('conflict in cell', i)
                #print("conflict!")
                neighbours = grid[i][1].split(",")
                prod_neighbours = []
                for k in neighbours:
                    prod_neighbours.append(float(grid[int(k)][3]))
                #print(prod_neighbours)
                prod_neighbours_normalised = [float(k)/sum(prod_neighbours) for k in prod_neighbours]
                #now determine conflict cell
                cell_conflict = np.random.choice(neighbours, p = prod_neighbours_normalised).astype(int)

                if grid[cell_conflict][11] == 1:
                    continue
                else:
                    grid[cell_conflict][11] = 1

                if grid[cell_conflict][2] == grid[i][2] and grid[cell_conflict][5] == 1: #check to see if conflict occurs between the same nation and cell is a border cell
                    #print("secession!")
                    #find the nation involved in secession
                    owner_i = grid[i][2]
                    #print(owner_i)
                    #print(grid[cell_conflict][2])
                    #count number of border cells for nation i
                    #count total number of cells for nation i
                    b_length = 0
                    size = 0
                    for j in range(1,n):
                        if grid[j][2] == owner_i and grid[j][5] == 1:
                            b_length = b_length + 1
                        if grid[j][2]== owner_i:
                            size = size + 1
                    r_pen_yes = 0 #religion penalty
                    if grid[owner_i][14] != grid[i][14]:
                        r_pen_yes = 1 #religion penalty
                    #calculate language penalty
                    l_pen_yes=0
                    if grid[owner_i][15] != grid[i][15]:
                        l_pen_yes = 1
                    l_r_pen_secession = r_penalty*r_pen_yes + l_penalty*l_pen_yes
                    geo_penalty = max(river_penalty*grid[i][12] + rug_penalty*grid[i][13],river_penalty*grid[cell_conflict][12]+ rug_penalty*grid[cell_conflict][13])

                    #print(b_length)
                    #print(size)
                    # secession function is a function of geography and national productivity
                    p_secede = beta*b_length*geo_penalty*(1+l_r_pen_secession)
                    winner = np.random.choice(s_outcomes, p = [p_secede, 1-p_secede])#, 1-p_win_i-p_win_cell_conflict])
                    if winner == 's':
                        #print("Secession victory")

                        #reassign newly independent cell to new nation
                        grid[i][2] = dead_nations.pop(0)
                        new_owner = grid[i][2]
                        print(new_owner)
                        #make it a border cell to be safe
                        grid[i][5] = 1
                        #all cells bordering this new nation are by definition border cells
                        neighbour_cellconflict = grid[i][1].split(",")
                        for k in neighbour_cellconflict:
                            grid[int(k)][5] = 1
                            #print(grid[int(k)][5])

                        #now recalculate national productivity
                        grid[new_owner][4] = grid[i][3]
                        grid[owner_i][4] = grid[owner_i][4] - grid[i][3]



                    else: #no change occurs when secession fails
                        pass
                        #print("Secession failure")

                #NOW WAR
                elif grid[cell_conflict][2] == grid[i][2] and grid[cell_conflict][5] == 0:
                    #not border cell so nothing happens
                    pass

                elif grid[cell_conflict][2] != grid[i][2]:
                    #print("war!")
                    #define the three outcomes

                    #call national productivity for the two nations involved
                    owner_i = grid[i][2]
                    #print('owner of i is', owner_i)
                    n_prod_i = grid[owner_i][4]
                #    print('national prod of cell i is', n_prod_i)
                    if n_prod_i == 0:
                        print('error')
                        result_grid = pd.DataFrame(grid, dtype=object)
                        result_grid.to_csv("error_test_grid.csv")

                    owner_c = grid[cell_conflict][2]
                    #print('owner of c is', owner_c)
                    n_prod_cell_conflict = grid[owner_c][4]
                    #print('national prod of cell conflict is', n_prod_cell_conflict)
                    if n_prod_cell_conflict == 0:
                        print('error')
                        result_grid = pd.DataFrame(grid, dtype=object)
                        result_grid.to_csv("error_test_grid.csv")

                    total_prod = round(n_prod_i + n_prod_cell_conflict,3)
                    #print('total prod is', total_prod)
                    geo_penalty = max(river_penalty*grid[i][12] + rug_penalty*grid[i][13],river_penalty*grid[cell_conflict][12]+ rug_penalty*grid[cell_conflict][13])
                    #print(geo_penalty)
                    if geo_penalty <0:
                        geo_penalty = 0
                    #print(geo_penalty)
                    r_pen_yes_owner_i = 0 #religion penalty
                    if grid[owner_i][14] != grid[cell_conflict][14] or grid[owner_i][14] != grid[i][14]:
                        r_pen_yes_owner_i = 1 #religion penalty
                    r_pen_yes_owner_c = 0 #religion penalty
                    if grid[owner_c][14] != grid[i][14] or grid[owner_c][14] != grid[cell_conflict][14]:
                        r_pen_yes_owner_c= 1 #religion penalty

                    l_pen_yes_owner_i = 0 #language penalty
                    if grid[owner_i][15] != grid[cell_conflict][15] or grid[owner_i][15] != grid[i][15]:
                        l_pen_yes_owner_i = 1 #language penalty
                    l_pen_yes_owner_c = 0 #language penalty
                    if grid[owner_c][15] != grid[i][15] or grid[owner_c][15] != grid[cell_conflict][15]:
                        l_pen_yes_owner_c = 1 #language penalty

                    l_r_pen_i = r_penalty*r_pen_yes_owner_i  + l_penalty*l_pen_yes_owner_i

                    l_r_pen_c = r_penalty*r_pen_yes_owner_c  + l_penalty*l_pen_yes_owner_c



                    p_win_i = n_prod_i/(total_prod*(1+geo_penalty+l_r_pen_i))
                    #print('p i win is:', p_win_i)
                    p_win_cell_conflict = n_prod_cell_conflict/(total_prod*(1+geo_penalty+l_r_pen_c))
                    #print('p c win is:', p_win_cell_conflict)

                    p_no_win = 1-p_win_i-p_win_cell_conflict
                    if p_no_win < 0.000000000005:
                        p_no_win = 0
                    #print(p_no_win)

                #    print('p c win is:', p_win_cell_conflict)
                    winner = np.random.choice(w_outcomes, p = [p_win_i, p_win_cell_conflict, p_no_win])


                    if winner == 'i':
                        #print ('i wins')
                        #reassign cell to nation owning cell i
                        grid[cell_conflict][2] = owner_i
                        #print(grid[cell_conflict][2])
                        #now we need to redetermine border cells
                        grid[cell_conflict][5] = 1 # just to be safe

                        neighbour_cellconflict = grid[cell_conflict][1].split(",") #look at neighbours of taken cell
                        for k in neighbour_cellconflict:
                            if grid[int(k)][2] != owner_i: #all cells not belonging to the conquering nation are border cells
                                grid[int(k)][5] = 1

                            if grid[int(k)][2] == owner_i: #check cells belonging to the conquering nation
                                # default to interior
                                grid[int(k)][5] = 0
                                #find neighbours
                                neighbour_winner = grid[int(k)][1].split(",")
                                for j in neighbour_winner:
                                    if grid[int(j)][2] != owner_i:
                                        grid[int(k)][5] = 1
                        #now recalculate national productivity
                        grid[owner_c][4] = grid[owner_c][4] - grid[cell_conflict][3]
                        grid[owner_i][4] = grid[owner_i][4] + grid[cell_conflict][3]
                        if grid[owner_c][4] == 0:
                            dead_nations.append(owner_c) #as this nation is dead


                    if winner == 'c':
                        #print ('c wins')

                        #reassign cell to nation c
                        grid[i][2] = owner_c
                        #print(grid[i][2])

                        #now we need to redetermine border cells
                        grid[i][5] = 1 # just to be safe

                        neighbour_cellconflict = grid[i][1].split(",")
                        for k in neighbour_cellconflict:

                            if grid[int(k)][2] != owner_c: #all cells not belonging to the conquering nation are border cells
                                grid[int(k)][5] = 1

                            if grid[int(k)][2] == owner_c: #check cells belonging to the conquering nation
                                # default to interior
                                grid[int(k)][5] = 0
                                #find neighbours
                                neighbour_winner = grid[int(k)][1].split(",")
                                for j in neighbour_winner:
                                    if grid[int(j)][2] != owner_c:
                                        grid[int(k)][5] = 1
                        #now recalculate national productivity
                        grid[owner_c][4] = grid[owner_c][4] + grid[i][3]
                        grid[owner_i][4] = grid[owner_i][4] - grid[i][3]
                        if grid[owner_i][4] == 0:
                            dead_nations.append(owner_i) #as this nation is dead


                        #All neighbour cells not owned by owner_c become border cells

                    else:
                        #inconclusive, so nothing necessary to consider
                        pass
        #reset everything

        for k in range(1,n):
            grid[k][11] = 0
            #grid[k][4] = 0 # reset national productivity

        for k in range(1,n): #prod and borders
            owner_i = grid[k][2]
            #get national productivity
            #grid[owner_i][4] += grid[k][3]

            #now recalculate borders
            grid[k][5] = 0 # just to be safe
            neighbours = grid[k][1].split(",")
            for l in neighbours:
                if grid[int(l)][2] != owner_i: #all cells not belonging to the conquering nation are border cells
                    grid[k][5] = 1
        for k in range(1,n):
            if grid[k][4] < 0.000005:
                grid[k][4] = 0
                dead_nations.append(k)

        #now calculate herfindahl index

        herf_india = float(0)
        herf_sea = float(0)
        for k in range(1,n):
            size_india = 0
            size_sea = 0
            for j in range(1,n):
                if grid[j][2]== int(k) and grid[j][6] == 1:
                    size_india += 1
                if grid[j][2] == int(k) and grid[j][7] == 1:
                    size_sea += 1
            herf_india = herf_india + (size_india/(india_cells))**2
            herf_sea = herf_sea + (size_sea/(sea_cells))**2
        #print(t)
        #print(repeat)
        final_herf_grid[2*repeat-1][t-1] = herf_india
        final_herf_grid[2*repeat-2][t-1] = herf_sea
        #print(herf_india)
        #print(herf_sea)
        #now reset conflict counter and lists, determine new productivity, redefine border cells

        #for k in range(1,n):
            #final_owner_grid[k-1][t-1] = grid[k][2]




# build collection of cells that constitute a nation
# do state boundaries match what the model says they should be? what cause? cultural or geographic?
# sarah + Hasin + librarian
#digitise map

#convert back to pandas dataframe and save to csv
result_grid = pd.DataFrame(final_herf_grid, dtype=object)
result_grid.to_csv("B122.csv")


result_grid = pd.DataFrame(grid, dtype=object)
result_grid.to_csv("B122_grid.csv")

#result_grid = pd.DataFrame(final_owner_grid, dtype=object)
#result_grid.to_csv("owner_analysis.csv")


#save owners at t=500
