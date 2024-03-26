# CSC384-2023Fall
Introduction to Artificial Intelligence

# Assignment 1 The Sokoban Puzzle
Implement a program to solve Sokoban puzzles.

The basic heuristic function used in this task is the Manhattam distance heuristic. However, I also developed an admissible advanced heuristic function that dominates the Manhattan distance heuristic.

# Assignment 2 The Mancala Game
Implement a program to play the Mancala game.

In this task, I also developed an advanced heuristic function, that is used as the bottom player agent in a game, where the top player agent is using the basic heuristic function. The bottom player is tested to have a win rate greater than 50%, and the rate is increased as the size of the game enlarges.

# Assignment 3 The Kropki Sudoku Puzzle
Implement a program to solve the Kropki Sudoku puzzles (6x6 and 9x9) using the knowledge of CSP.

# Assignment 4 Bayes Net
Apply the Variable Elimination Algorithm(VEA) predict the salaries of people who lived in the United States in 1994 by using a variety of attributes. The process includes creating a Naive Bayes model to represent the relationships between people’s salaries and their other attributes such as race, gender, education level, etc. And then implement and use the VEA to calculate probabilities and make salary predictions.

Explored questions:
What percentage of the women in the test data set does our model predict having a salary >= $50K? 
What percentage of the men in the test data set does our model predict having a salary >= $50K?
What percentage of the women in the test data set satisfies the condition: P(Salary=">=$50K" | Evidence) > P(Salary=">=$50K" | Evidence, Gender)
What percentage of the men in the test data set satisfies the condition: P(Salary=">=$50K"|E) > P(Salary=">=$50K"|E, Gender)?
What percentage of the women in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?
What percentage of the men in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K? 
