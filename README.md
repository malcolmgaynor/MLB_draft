# MLB_draft
Modeling the 2024 MLB draft using an iterative integer optimization approach which includes simulation and ML modeling (CoxPH and MARS models). Please view the Streamlit dashboard: https://mlbdraft.streamlit.app/

This project was created by Malcolm Gaynor, and was inspired by and is an extension of a project done at MIT with Atharva Navaratne for Prof Alex Jacquillat's 15.083: Integer Optimization class

The process involved three separate models:

1. ML model (Multivariate Adaptive Regression Spline) to predict signing bonuses
2. Statistical model (CoxPH survivorship model) to predict when each player will be available
3. Optimization model (iterative Integer Optimization formulations) to optimize selections

Framework: For each selection, the model simulated 100 future player availabilities. For example, at a team's first round selection, the model will simulate who will be available at each of their future selections as well. These simulations were based on the results of the CoxPH survivorship model. Thus, the model can optimize the first round's selection in a global sense. After the 100 simulations of the entire draft, the player who the model selects for the first round is selected. Then, the process continues for the next selection. Each selection also includes the signing bonus, which is predicted for each player at each potential selection using the MARS model.

ML model for predicting signing bonus: The inputs of this model were Fangraph's scouting report data, including FV (future Value) and Risk. Also, the model took into account position, school level (high school or college), and pick number. The output is a predicted signing bonus, as a proportion of that year's largest signing bonus. This is done to ensure consistency in the training data, which were the 2021, 2022, and 2023 draft. When applied on the 2024 draft, the model performed well. A MARS model with degree 2 terms had an out of sample R-squared of 0.93 when applied to the players at their actual pick numbers. This model was applied to each possible combination of player and draft pick selection for the optimization model.

Statistical survivorship model for predicting likelihood of player availability at each pick: The inputs of this model were Fangraph's scouting report data, including FV (future Value) and Risk, along with position and school level (high school or college). The CoxPH model predicts the probability that each player survives (is not drafted) until each possible pick. The model was trained on the 2021, 2022, and 2023 draft, and applied to the 2024 draft data. When applied to the real results from the 2024 draft, the model had a test set C-index score of 0.787, implying relatively strong predictive power, compared to a baseline C-index of 0.5, which corresponds to no better than random guessing. This model is used to create accurate simulations of future player availabilities.

Integer Optimization formulation: The integer optimization model was run 100 times for each selection, to separately optimize each pick under 100 simulations of future player availabilities. The decision variable was whether each player was selected at each pick. The objective function involved maximizing a player's Future Value, as defined by Fangraph's scouting metrics, with a penalty term for the Risk metric, along with a penalty term that discriminated against selecting high school players. This high school penalty was small, and only applied to teams in the playoff hunt in 2024, who would be less likely to draft a player who is further away from making an impact in MLB. The model was constrained to not exceed the team's real spending within the first 4 rounds, as well as to select at most two players from the same position (note: right handed pitchers and left handed pitchers are classified as different positions, but left fielders and right fielders, for example, are just classified as outfielders).

Next steps/limitations:

- Players who don't sign: the model does not include any predictions about which players may not sign, and therefore also fails to take into account the hypothetical value of compensatory picks when this occurs.

- More rounds: the model only takes into account rounds 1-4, as a result of limited player data. This means that the model is constrained in how creative its strategies can be. For example, drafting players and signing them well above slot value, which is a phenomenon that mostly occurs later in the draft, is not a strategy utilized by this model.

- More robust iterations: For example, if a very valuable player is available the second round about 40% of the time, it may be worth it to save the necessary money in the first round in case they are available, even if it is not the most probable outcome. In other words, the model could be improved by including weighting on the value of certain simulations depending on the reward that selection achieved. This would make teams less likely to miss out on valuable players who may potentially fall to them in the next round, even if that is relatively unlikely.

Sources: Fangraphs - https://www.fangraphs.com/prospects/the-board/2024-mlb-draft and Baseball America - https://www.baseballamerica.com/draft-results/

In this repository, the Code file includes all of the models built (Integer Optimization in Julia, MARS in R, and CoxPH in Python). The Optimization_CSVs are the results of the optimization model, the Original_CSVs are the downloaded (raw) data, and the Intermediary_CSVs are inputs to the optimization model.  
