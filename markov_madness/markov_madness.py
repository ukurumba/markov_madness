# -*- coding: utf-8 -*-
def predictor(regseasonstats,teams,vars,coefficients):
    '''This function takes in multiple different constraints and outputs the teams most likely to win the NCAA tournament and 
    their probabilities of winning.     
    
    Example
    -------
    predictor(2013_2014_Regular_Season_Stats,teams2014,coeffs,result[0])
    
    Inputs
    ------
    regseasonstats = uploaded CSV file containing statistics for all teams as a Pandas Dataframe
    teams = a list of the row numbers of the aforementioned Dataframe associated with the 64 teams in the NCAA bracket that year
    vars = the numerical values of the column headers of the variables you used in your regression
    coefficients = the associated regression coefficients (calculated based off 2015 data) for each variable in vars.
    
    Returns
    -------
    A table that shows the internal team number in the first column, the probability the team wins the tournament in the second column,
    and the team name in the third column, for the top 16 teams. 
    '''
    
    

    #renaming columns, forming 'per game' data, turning it all into a matrix. The usual stuff.
    col_numbers=[]
    for i in range(0,34,1):
        col_numbers.append(i)
    regseasonstats.columns=[col_numbers]
    bracket_with_headers = regseasonstats.iloc[teams,:]
    Bracket_without_headers = np.zeros((64,32))
    for j in range (0,64,1):
        for i in range(3,34,1):
            val = float(bracket_with_headers.iat[j,i])/float(bracket_with_headers.iat[j,2])
            Bracket_without_headers[j,i-3]=val
            
    #selecting only the data we want and computing the predicted rankings
    only_relevant_data = []
    for i in vars:
        only_relevant_data.append(Bracket_without_headers[:,i])
    data_matrix = np.asarray(only_relevant_data)
    coefficients = np.asarray(coefficients)
    predicted_rankings = np.dot(np.transpose(coefficients),data_matrix)
    predicted_rankings_adjusted = np.zeros((1,64))
    for i in range(0,64,1):
        if predicted_rankings[0,i] < 0:
            predicted_rankings_adjusted[0,i] = 1
        else:
            predicted_rankings_adjusted[0,i] = predicted_rankings[0,i]
    
    #Making the Markov transition matrix
    transition_matrix = np.zeros((64,64))
    def diagvalue(i):
        a=0
        for j in range(0,64,1):
            a = a + predicted_rankings_adjusted[0,i]/(predicted_rankings_adjusted[0,i]+predicted_rankings_adjusted[0,j])
        return 1/(64*.9921875)*a
    for i in range(0,64,1):
        for j in range(0,64,1):
            if i != j:
                transition_matrix[i,j] = 1/(64*.9921875) * predicted_rankings_adjusted[0,j]/(predicted_rankings_adjusted[0,i] + predicted_rankings_adjusted[0,j])
            if i == j:
                transition_matrix[i,i] = diagvalue(i)
    
    #Calculating steady state probabilities with our little math trick and printing results.
    transition_matrix_transpose = np.transpose(transition_matrix)
    xmatrix = np.zeros((64,64))
    for i in range(0,64,1):
        for j in range(0,64,1):
            if i == j:
                xmatrix[i,j] = transition_matrix_transpose[i,i] - 1
            if i != j:
                xmatrix[i,j] = transition_matrix_transpose[i,j]

    for i in range(0,64,1):
        xmatrix[63,i] = 1

    b = np.zeros((64,1))
    b[63,0] = 1
    probabilities = []
    teamnames = []

    for i in range(0,64,1):
        solutions = np.linalg.solve(xmatrix,b)[i,0]
        probabilities.append(solutions)
        teamnames.append(bracket_with_headers.iat[i,1])

    teamname = pd.Series(teamnames)
    probability = pd.Series(probabilities)


    predictions = pd.DataFrame({ 'Team Name' : teamname,
                                 'Steady State Probability' : probability})
    finalpredictions = predictions.sort_values(by = 'Steady State Probability')
    return(finalpredictions[48:65])
                        

