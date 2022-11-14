import pandas as pd
import numpy as np

data = pd.read_csv (r'grid_language_religions.csv')
#print(data)
grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','productivity','national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','temp_min','temp_max'])
#grid1 = pd.DataFrame(data, columns=['cell_number','neighbours','nation','uniform_productivity','uniform_national_productivity', 'border_cell', 'India','SEA','cell_into_conflict', 'nation_in_conflict', 'prod_faced','already_conflict','river', 'ruggedness','religion','language_group','temp_min','temp_max'])
d1,d2 = (10,500)
final_herf_grid = [[0 for i in range(d2)] for j in range(d1)]
grid = grid1.to_numpy()
#print(grid.values[1][1])

#grab some useful values that will be nice to have stored in memory
n = len(grid)
max_prod = round(np.amax(grid,axis = 0)[3],3)
beta = 0.000005
#beta = 0
x_rugg_90 = np.percentile(grid[:,13], 90, axis=None, out=None)
#print(x_rugg_90)
c_check = ['conflict','no_conflict']
s_outcomes = ['s','f']
w_outcomes = ['i','c','n'] #owner of cell i, the owner of the cell it comes into conflict with, or no winner
dead_nations = list()
river_penalty = 0
#rug_penalty = round(3/(x_rugg_90/max(grid[:,13])),3)
rug_penalty = round(2/(x_rugg_90),3)

#rug_penalty = 0
print(rug_penalty)
l_and_r_penalty = 0
india_cells = 0
sea_cells = 0
for i in range(1,n):
    if grid[i][6] == 1:
        india_cells += 1
    if grid[i][7] == 1:
        sea_cells += 1


for repeat in range(1, 1+ 1):
    print('current repetition is', repeat)
    grid = grid1.to_numpy()

    #initalise lists
    for i in range(1,n):
        grid[i][9] = [] #nations faced
        grid[i][10] = [] #national productivity faced
        #round the numbers off
        grid[i][3] = round(grid[i][3],5)
        #print(grid[i][9])
        grid[i][4] = round(grid[i][4],5)
        #print(grid[i][17])
        #climate data is in degrees*10, so divide by 10
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
    #print(hot_rugg_90)
    cold_rugg_90 = np.percentile(grid[:,16], 90, axis=None, out=None)
    #hot_penalty = round(2/(hot_rugg_90),3)
    hot_penalty = 0
    #print('hot penalty is',hot_penalty)
    cold_penalty = 0
    #cold_penalty = round(2/(cold_rugg_90),3)

    for t in range(1,250+1):
        print(t)
        for i in range(1,n):
            #print(i)
            #cell can only come into conflict with one other cell at most
            if grid[i][11] == 1: # if conflict already occuring here
                    #print('already conflict')
                continue

            p_conflict = round(grid[i][3]/max_prod,3)
            #p_conflict = 1
            #print(p_conflict)

            conflict_occur = np.random.choice(c_check, p = [p_conflict, 1-p_conflict])
            #print(conflict_occur)

            if conflict_occur == 'conflict':
                #print('conflict in cell', i)
                #find the cell that i is in conflict with
                neighbours = grid[i][1].split(",")
                prod_neighbours = []
                for k in neighbours:
                    prod_neighbours.append(float(grid[int(k)][3]))
                prod_neighbours_normalised = [float(k)/sum(prod_neighbours) for k in prod_neighbours]
                #print(neighbours)
                #print(prod_neighbours_normalised)
                #now determine conflict cell
                cell_conflict = np.random.choice(neighbours, p = prod_neighbours_normalised).astype(int)

                if grid[cell_conflict][11]==1:
                    continue

                grid[i][8] = cell_conflict
                #cell_conflict = grid[i][8]

                #note that cell_conflict is in conflict with i
                grid[cell_conflict][8] = i

                #print('cell conflict is', cell_conflict)
                #set conflict happens to 1
                grid[i][11] = 1
                grid[cell_conflict][11] = 1
                #find owners of the two cells
                owner_i = grid[i][2]
                #print(owner_i)
                owner_cell_conflict = grid[cell_conflict][2]
                if owner_i != owner_cell_conflict: #since we only care about war not secession
                    #print(owner_cell_conflict)
                    #now append to the list of nations in conflict with:
                    #print(owner_cell_conflict)
                    grid[owner_i][9].append(owner_cell_conflict)
                    #print(grid[owner_i][9])
                    grid[owner_cell_conflict][9].append(owner_i)
                #    print(owner_i)
                    #print(grid[owner_cell_conflict][9])
                    #get national productivities
                    prod_owner_i = grid[owner_i][4]
                    prod_owner_cell_conflict = grid[owner_cell_conflict][4]
                    #append to list of productivity faced
                    grid[owner_i][10].append(prod_owner_cell_conflict)
                    #print(prod_owner_cell_conflict)
                    #print(grid[owner_i][10])
                #    print(prod_owner_i)
                    grid[owner_cell_conflict][10].append(prod_owner_i)
                    #print(grid[owner_cell_conflict][10])

                    #print('neighbour is', grid[i][8])

        #print('now normalise')
        for i in range(1,n):
            #grid[i][9].append(i)
            #print(grid[i][9])

            #remove duplicate nations
            #print('owner is', grid[i][2])
            grid[i][9] = list(dict.fromkeys(grid[i][9]))
            #print('nations against are', grid[i][9])
            #print(grid[i][10])
            prod_faced_grid = grid[i][10]
            #normalise the productivity faced vector
            grid[i][10] = [float(k)/sum(prod_faced_grid) for k in prod_faced_grid]
            #print(grid[i][10])
        #now resolve conflict
        for i in range(1,n):
            #print(grid[i][9])
            #skip cells that have no conflict occuring
            if grid[i][11] == 0:
                #print('no conflict ')
                continue
            #get owners of cells
            owner_i = grid[i][2]
            cell_conflict = grid[i][8]
            owner_cell_conflict = grid[cell_conflict][2]
            #get productivities of owners
            prod_owner_i = grid[owner_i][4]
            prod_owner_cell_conflict = grid[owner_cell_conflict][4]
            #print(total_prod)
            #print(grid[owner_i][9])
            #print(grid[owner_cell_conflict][9])
        #    print('owner is', owner_i)
            #print('cell conflict is', cell_conflict)
        #    print('owner c is', owner_cell_conflict)
            #print(owner_i, owner_cell_conflict)
            #calculate geo_penalty
            r_penalty = 0 #religion penalty
            if grid[cell_conflict][14] != grid[i][14]:
                r_penalty = 1 #religion penalty
            #calculate language penalty
            l_penalty=0
            if grid[cell_conflict][15] != grid[i][15]:
                l_penalty = 1
            geo_penalty = max(rug_penalty*grid[i][13] + hot_penalty*grid[i][17]+cold_penalty*grid[i][16],rug_penalty*grid[cell_conflict][13] + hot_penalty*grid[cell_conflict][17] + cold_penalty*grid[cell_conflict][16]) + (l_penalty+r_penalty)*l_and_r_penalty
            #print(hot_penalty*grid[i][17])
            #print(geo_penalty)
            if owner_i == owner_cell_conflict and grid[i][5] == 1: #SECESSION ON BORDER CELL
                b_length = 0
                size = 0
                for j in range(1,n):
                    if grid[j][2] == owner_i and grid[j][5] == 1:
                        b_length = b_length + 1
                    if grid[j][2]== owner_i:
                        size = size + 1
                #print(b_length)
                p_secede = round(beta*geo_penalty*b_length,5)
                winner = np.random.choice(s_outcomes, p = [p_secede, 1-p_secede])
                if winner == 's':
                    #print("Secession victory")
                    #reassign newly independent cell to new nation
                    #print(grid[i][2])
                    grid[i][2] = dead_nations.pop(0)
                    #print(grid[i][2])
                    new_owner = grid[i][2]

            elif owner_i != owner_cell_conflict: #WAR
                #see how much they actually commit
                #print(grid[owner_i][9])
                #print(owner_cell_conflict)
            #    print(grid[owner_i][10])

                #print(grid[owner_cell_conflict][9])
                #print(grid[i][9].index(cell_conflict))
                index_i_of_cell_conflict = grid[owner_i][9].index(owner_cell_conflict)
                #print('index is', index_i_of_cell_conflict)
                index_cell_conflict_of_i = grid[owner_cell_conflict][9].index(owner_i)
                #print(index_cell_conflict_of_i)
                i_prod_face = grid[owner_i][10]
                #print(i_prod_face)
                c_prod_face = grid[owner_cell_conflict][10]


                #i faces productivies, use index
                prod_owner_i_comitted = i_prod_face[index_i_of_cell_conflict]*prod_owner_i
                prod_owner_cell_conflict_comitted = c_prod_face[index_cell_conflict_of_i]*prod_owner_cell_conflict
                total_prod_committed = prod_owner_i_comitted + prod_owner_cell_conflict_comitted

                #p_win_i = round(prod_owner_i_comitted/(total_prod_committed*(1+geo_penalty)),3)
                p_win_i = round(prod_owner_i_comitted/(total_prod_committed*(1+geo_penalty)),8)


                #print('p i win is:', p_win_i)
                #p_win_cell_conflict = round(prod_owner_cell_conflict_comitted/(total_prod_committed*(1+geo_penalty)),3)
                p_win_cell_conflict = round(prod_owner_cell_conflict_comitted/(total_prod_committed*(1+geo_penalty)),8)
               # print('p c win is:', p_win_cell_conflict)
                p_no_win = 1 - p_win_i - p_win_cell_conflict
                if p_no_win < 0.000000000005:
                    p_no_win = 0

                #print(p_no_win)
                winner = np.random.choice(w_outcomes, p = [p_win_i, p_win_cell_conflict, p_no_win])
                #print('winner is', winner)
                if winner == 'i':
                    #reassign cell to nation owning cell i
                    grid[cell_conflict][2] = owner_i
                    #Dont update national productivity, dont update border cell
                elif winner == 'c':
                    grid[i][2] = owner_cell_conflict
            #note that conflict is over
            grid[i][11] = 0
            grid[cell_conflict][11] = 0


        #now reset conflict counter and lists, determine new productivity, redefine border cells
        for i in range(1,n):
            grid[i][11] = 0 #conflict happening
            grid[i][4] = 0 # reset national productivity
            grid[i][9] = [] #nations faced
            grid[i][10] = []#national productivity faced

        #print('reset works')

        for i in range(1,n): #prod and borders
            owner_i = grid[i][2]
            #get national productivity
            grid[owner_i][4] += grid[i][3]

            #now recalculate borders
            grid[i][5] = 0 # just to be safe
            neighbours = grid[i][1].split(",")
            for k in neighbours:
                if grid[int(k)][2] != owner_i: #all cells not belonging to the conquering nation are border cells
                    grid[i][5] = 1
        for i in range(1,n):
            if grid[i][4] < 0.000005:
                grid[i][4] = 0
                dead_nations.append(i)
            #if grid[i][4] !=0:
            #    print(grid[i][4])


        herf_india = float(0)
        herf_sea = float(0)
        for i in range(1,n):
            size_india = 0
            size_sea = 0
            for j in range(1,n):
                if grid[j][2]== int(i) and grid[j][6] == 1:
                    size_india += 1
                if grid[j][2] == int(i) and grid[j][7] == 1:
                    size_sea += 1
            herf_india = herf_india + (size_india/(india_cells))**2
            herf_sea = herf_sea + (size_sea/(sea_cells))**2
        #print(t)
        #print(repeat)
        final_herf_grid[2*repeat-1][t-1] = herf_india
        final_herf_grid[2*repeat-2][t-1] = herf_sea
        #print(herf_india)

            #print(herf_sea)
results = pd.DataFrame(final_herf_grid, dtype=object)
results.to_csv("smart_s_3.csv")
result_grid = pd.DataFrame(grid, dtype=object)
result_grid.to_csv("smart_s_3_grid.csv")
