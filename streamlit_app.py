### TODO: 

import streamlit as st
import pandas as pd
import os
from pathlib import Path
import re

#MLB team abbreviatoins 
MLB_TEAMS = {
    'ARI': 'Arizona Diamondbacks',
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Guardians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals',
    'LAA': 'Los Angeles Angels',
    'LAD': 'Los Angeles Dodgers',
    'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers',
    'MIN': 'Minnesota Twins',
    'NYM': 'New York Mets',
    'NYY': 'New York Yankees',
    'ATH': 'Athletics',
    'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'SFG': 'San Francisco Giants',
    'SEA': 'Seattle Mariners',
    'STL': 'St. Louis Cardinals',
    'TBR': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'
}

# name mappings in ou rdata
TEAM_NAME_MAPPING = {
    'Arizona Diamondbacks': 'ARI',
    'Atlanta Braves': 'ATL',
    'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS',
    'Chicago Cubs': 'CHC',
    'Chicago White Sox': 'CHW',
    'Cincinnati Reds': 'CIN',
    'Cleveland Guardians': 'CLE',
    'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET',
    'Houston Astros': 'HOU',
    'Kansas City Royals': 'KCR',
    'Los Angeles Angels': 'LAA',
    'Los Angeles Dodgers': 'LAD',
    'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL',
    'Minnesota Twins': 'MIN',
    'New York Mets': 'NYM',
    'New York Yankees': 'NYY',
    'Athletics': 'ATH',
    'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT',
    'San Diego Padres': 'SDP',
    'San Francisco Giants': 'SFG',
    'Seattle Mariners': 'SEA',
    'St. Louis Cardinals': 'STL',
    'Tampa Bay Rays': 'TBR',
    'Texas Rangers': 'TEX',
    'Toronto Blue Jays': 'TOR',
    'Washington Nationals': 'WSN'
}

def get_available_teams(data_directory="Optimization_CSVs"):
    """Get list of teams that have CSV files available"""
    available_teams = []
    for abbrev in MLB_TEAMS.keys():
        # Athletics are ATH sometimes and OAK other times...
        if abbrev == 'ATH':
            file_path = Path(data_directory) / f"output_OAK.csv"
        else:
            file_path = Path(data_directory) / f"output_{abbrev}.csv"
        
        if file_path.exists():
            available_teams.append(abbrev)
    return available_teams

def load_actual_draft_data(data_directory="Optimization_CSVs"):
    """Load the actual draft results data"""
    file_path = Path(data_directory) / "data_ba-results.csv"
    try:
        df = pd.read_csv(file_path)
        
        # add abbreviations to make filtering more user friendly 
        df['Team_Abbrev'] = df['Team'].map(TEAM_NAME_MAPPING)
        
        return df
    except FileNotFoundError:
        st.error("data_ba-results.csv file not found")
        return None
    except Exception as e:
        st.error(f"Error loading actual draft data: {str(e)}")
        return None

def load_team_predictions(team_abbrev, data_directory="Optimization_CSVs"):
    """Load optimization predictions for a specific team"""
    # As are a special case again 
    if team_abbrev == 'ATH':
        file_path = Path(data_directory) / f"output_OAK.csv"
    else:
        file_path = Path(data_directory) / f"output_{team_abbrev}.csv"
    
    try:
        df = pd.read_csv(file_path)
        
        # necessary b/c of julia style dataframe outputs...
        if df.shape == (1, 1):
            # raw string data 
            raw_data = str(df.iloc[0, 0])
            
            # Parse concatenated string
            players = []
            bonuses = []
            
            # number │ name number
            pattern = r'(\d+)\s*│\s*([^│]+?)\s+([\d.]+)'
            matches = re.findall(pattern, raw_data)
            
            for match in matches:
                row_num, name, bonus = match
                name = name.strip()
                try:
                    bonus_val = float(bonus)
                    players.append(name)
                    bonuses.append(bonus_val)
                except ValueError:
                    continue
            
            if players:
                df = pd.DataFrame({
                    'Name': players,
                    'Optimization_Value': bonuses
                })
            else:
                return None
        
        # more standard csv format 
        elif len(df) > 0 and str(df.iloc[0, 0]).strip() in ['Any', 'String', 'Float64', 'Int64']:
            df = df.iloc[1:].reset_index(drop=True)
        
        # standard colnames 
        if df.shape[1] >= 2:
            if 'Name' not in df.columns or ('Bonus' not in df.columns and 'Optimization_Value' not in df.columns):
                df.columns = ['Name', 'Optimization_Value'] + list(df.columns[2:])
        
        if 'Name' in df.columns:
            df = df.dropna(subset=['Name'])
        
        # convert this value ot number 
        opt_col = 'Optimization_Value' if 'Optimization_Value' in df.columns else 'Bonus'
        if opt_col in df.columns:
            df[opt_col] = pd.to_numeric(df[opt_col], errors='coerce')
            if opt_col == 'Bonus':
                df = df.rename(columns={'Bonus': 'Optimization_Value'})
        
        return df
    except FileNotFoundError:
        file_name = f"output_OAK.csv" if team_abbrev == 'ATH' else f"output_{team_abbrev}.csv"
        st.error(f"File not found: {file_name}")
        return None
    except Exception as e:
        st.error(f"Error loading prediction data: {str(e)}")
        return None

def format_currency(amount):
    """Format currency amounts"""
    try:
        if pd.isna(amount) or amount == '' or amount == 0:
            return "NA"
        
        # correct format output 
        if isinstance(amount, str):
            amount_clean = amount.replace('$', '').replace(',', '')
            amount_num = float(amount_clean)
        else:
            amount_num = float(amount)
        
        if amount_num >= 1000000:
            return f"${amount_num/1000000:.2f}M"
        elif amount_num >= 1000:
            return f"${amount_num/1000:.0f}K"
        else:
            return f"${amount_num:,.0f}"
    except:
        return str(amount)

def format_optimization_value(value):
    """Format optimization values"""
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.6f}"
    except:
        return str(value)

def find_player_in_actual_draft(player_name, actual_draft_df):
    """Find if a predicted player was actually drafted and return their details"""
    if actual_draft_df is None:
        return None
    
    # exact match (ideal)
    exact_match = actual_draft_df[actual_draft_df['Name'].str.strip() == player_name.strip()]
    if not exact_match.empty:
        return exact_match.iloc[0]
    
    # partial match (try if not exact) 
    partial_match = actual_draft_df[actual_draft_df['Name'].str.contains(player_name.strip(), case=False, na=False)]
    if not partial_match.empty:
        return partial_match.iloc[0]
    
    return None

def main():
    st.set_page_config(
        page_title="2024 MLB Draft Analysis: Integer Optimization ModelTEST",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("⚾ 2024 MLB Draft Analysis: Integer Optimization Model")
    #st.markdown("Compare your optimization model's predictions with actual draft results")

    #st.write("This project was created by Malcolm Gaynor, and was inspired by and is an extension of a project done at MIT with Atharva Navaratne for Prof Alex Jacquillat's 15.083: Integer Optimization class")
    st.write("""Using Integer Optimization, Machine Learning, and Statistical Modeling, this program optimizes each team's selections in the 2024 MLB draft, maximizing value for picks in rounds 1 through 4 considering various constraints, including 
             projected future player availabilities, signing bonuses, and budget/position constraints. Select a team in the drop down menu below to compare the model's optimal results to the real draft results. Also,
             view overall takeaways from the results and details about the modeling process in the tabs below the drop down menu. Please don't hesitate to reach out with any questions or comments: malcolm.t.gaynor@gmail.com.""")
    # load actual draft data
    actual_draft_df = load_actual_draft_data()
    
    #available teams
    available_teams = get_available_teams()
    
    if not available_teams:
        st.error("No optimization CSV files found in the 'Optimization_CSVs' folder.")
        return
    
    # dropdown w/ team names
    team_options = {f"{MLB_TEAMS[abbrev]} ({abbrev})": abbrev for abbrev in sorted(available_teams)}
    
    # Select team
    selected_team_display = st.selectbox(
        "Select a team:",
        options=list(team_options.keys()),
        index=0
    )
    
    selected_team_abbrev = team_options[selected_team_display]
    selected_team_name = MLB_TEAMS[selected_team_abbrev]
    
    # Load data
    predictions_df = load_team_predictions(selected_team_abbrev)
    
    if predictions_df is None:
        st.error(f"Could not load prediction data for {selected_team_name}")
        return
    
    # Filter draft data for selected team
    actual_team_df = None
    if actual_draft_df is not None:
        actual_team_df = actual_draft_df[actual_draft_df['Team_Abbrev'] == selected_team_abbrev].copy()
    
    # Display summary
    #col1, col2 = st.columns(2)
    
    #with col1:
    #    st.metric("Model Predictions", len(predictions_df))
    
    #with col2:
    #    if actual_team_df is not None:
    #        st.metric("Actual Draft Picks", len(actual_team_df))
    #    else:
    #        st.metric("Actual Draft Picks", "Data not available")
    
    #st.markdown("---")
    
    # tabs for different views
    tab1, tab2, tab3 = st.tabs(["Optimization Model vs. Real Draft Results", "Overall Takeaways", "Model details (Machine Learning/Integer Optimization)"])

    with tab1:
        st.subheader(f"Comparison for {selected_team_name}")
        
        # Prepare the data
        enhanced_predictions = predictions_df.copy()
        enhanced_predictions['Actually_Drafted'] = False
        enhanced_predictions['Draft_Round'] = ""
        enhanced_predictions['Draft_Pick'] = ""
        enhanced_predictions['Actual_Bonus'] = ""
        enhanced_predictions['Team'] = ""
        enhanced_predictions['Position'] = ""
        
        if actual_draft_df is not None:
            for idx, row in enhanced_predictions.iterrows():
                player_name = row['Name']
                actual_info = find_player_in_actual_draft(player_name, actual_draft_df)
                
                if actual_info is not None:
                    enhanced_predictions.at[idx, 'Actually_Drafted'] = True
                    enhanced_predictions.at[idx, 'Draft_Round'] = actual_info['Round']
                    enhanced_predictions.at[idx, 'Draft_Pick'] = actual_info['Pick']
                    enhanced_predictions.at[idx, 'Actual_Bonus'] = format_currency(actual_info['Bonus'])
                    enhanced_predictions.at[idx, 'Team'] = actual_info['Team']
                    enhanced_predictions.at[idx, 'Position'] = actual_info['Position']
    
        # Prepare actual draft data sorted by pick
        actual_team_df_sorted = None
        if actual_team_df is not None and len(actual_team_df) > 0:
            # Convert Pick to numeric to ensure proper sorting (Round can be non-numeric like CB1)
            actual_team_df_sorted = actual_team_df.copy()
            actual_team_df_sorted['Pick'] = pd.to_numeric(actual_team_df_sorted['Pick'], errors='coerce')
            
            # Sort by pick number (this is always numeric and determines draft order)
            actual_team_df_sorted = actual_team_df_sorted.sort_values('Pick')
            actual_team_df_sorted['predicted'] = actual_team_df_sorted['Name'].isin(predictions_df['Name'].values)
    
        # Get unique rounds from actual draft data, in the order they appear by pick
        rounds = []
        if actual_team_df_sorted is not None:
            # Get rounds in the order they appear (by pick number) - don't sort rounds themselves
            rounds = actual_team_df_sorted['Round'].unique().tolist()
        
        # Display by round
        for round_idx, round_num in enumerate(rounds):
            # Find the pick number for this round to display in header
            round_picks = actual_team_df_sorted[actual_team_df_sorted['Round'] == round_num]
            pick_num = round_picks['Pick'].iloc[0] if len(round_picks) > 0 else "Unknown"
            
            st.markdown(f"### Round {round_num}, Pick {pick_num}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Optimization Model Results**")
                
                if round_idx < len(enhanced_predictions):
                    # Get the prediction by index (0-based)
                    pred_row = enhanced_predictions.iloc[round_idx]
                    
                    with st.container():
                        if pred_row['Actually_Drafted']:
                            st.success(f"**{pred_row['Name']}**")
                            st.write(f"Position: {pred_row['Position']}")
                            
                            bonus = pred_row['Optimization_Value'] * 9250000
                            if bonus >= 1_000_000:
                                formatted_bonus = f"${bonus / 1_000_000:.2f}M"
                            else:
                                formatted_bonus = f"${bonus / 1_000:.0f}K"
                            
                            st.write(f"Actually Drafted: Round {pred_row['Draft_Round']}, Pick {pred_row['Draft_Pick']}, {pred_row['Team']}")
                            st.write(f"Predicted Bonus: {formatted_bonus}")
                            st.write(f"Actual Bonus: {pred_row['Actual_Bonus']}")
                        else:
                            st.info(f"❓ **{pred_row['Name']}**")
                            st.write(f"Optimization Value: {format_optimization_value(pred_row['Optimization_Value'])}")
                            st.write(f"Not drafted by this team in Round {round_num}, Pick {pick_num}")
                else:
                    st.info("Model not applied after Round 4")
            
            with col2:
                st.markdown("**Actual Draft Results**")
                
                # Display actual picks for this round
                round_actual_picks = actual_team_df_sorted[actual_team_df_sorted['Round'] == round_num]
                for idx, row in round_actual_picks.iterrows():
                    player_name = row['Name']
                    predicted = row['predicted']
                    
                    with st.container():
                        if predicted:
                            st.success(f"**{player_name}**")
                        else:
                            st.warning(f"**{player_name}**")
                        
                        st.write(f"Position: {row['Position']}")
                        st.write(f"Actual Pick: Round {row['Round']}, Pick {row['Pick']}, {selected_team_name}")
                        #st.write(f"Round {row['Round']}, Pick {row['Pick']}")
                        st.write(f"Bonus: {format_currency(row['Bonus'])}")
                        st.write(f"Signed: {'Yes' if row['Signed'] == 'Y' else 'No'}")
            
            st.write("---")  # Separator between rounds
    
        # Handle case where there are no actual draft results
        if actual_team_df_sorted is None or len(actual_team_df_sorted) == 0:
            st.info("No actual draft data available for this team")
            
            # Still show predictions
            st.markdown("### Optimization Model Predictions")
            col1, col2 = st.columns(2)
            
            with col1:
                for idx, row in enhanced_predictions.iterrows():
                    with st.container():
                        st.info(f"❓ **{row['Name']}**")
                        st.write(f"Optimization Value: {format_optimization_value(row['Optimization_Value'])}")
                        st.write("Not drafted by this team")
                        st.write("---")
    
        # Download buttons
        st.markdown("---")
        st.markdown("### Download Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if predictions_df is not None:
                csv_predictions = predictions_df.to_csv(index=False)
                st.download_button(
                    label=f"Download Model Predictions ({selected_team_abbrev})",
                    data=csv_predictions,
                    file_name=f"model_predictions_{selected_team_abbrev}.csv",
                    mime="text/csv"
                )
    
        with col2:
            if actual_team_df is not None and len(actual_team_df) > 0:
                csv_actual = actual_team_df.to_csv(index=False)
                st.download_button(
                    label=f"Download Actual Results ({selected_team_abbrev})",
                    data=csv_actual,
                    file_name=f"actual_results_{selected_team_abbrev}.csv",
                    mime="text/csv"
                )

    
    #with tab1:
     #   st.subheader(f"Comparison for {selected_team_name}")
      #  
       # col1, col2 = st.columns(2)
        
        #with col1:
         #   st.markdown("### Optimization Model Results")
            
          #  # enhanced_predictions is waht we want to display 
           # enhanced_predictions = predictions_df.copy()
            #enhanced_predictions['Actually_Drafted'] = False
            #enhanced_predictions['Draft_Round'] = ""
            #enhanced_predictions['Draft_Pick'] = ""
            #enhanced_predictions['Actual_Bonus'] = ""
            #enhanced_predictions['Team'] = ""
            #enhanced_predictions['Position'] =""
            
           # if actual_draft_df is not None:
            #    for idx, row in enhanced_predictions.iterrows():
             #       player_name = row['Name']
              #      actual_info = find_player_in_actual_draft(player_name, actual_draft_df)
               #     
                #    if actual_info is not None:
                 #       enhanced_predictions.at[idx, 'Actually_Drafted'] = True
                  #      enhanced_predictions.at[idx, 'Draft_Round'] = actual_info['Round']
                   #     enhanced_predictions.at[idx, 'Draft_Pick'] = actual_info['Pick']
                    #    enhanced_predictions.at[idx, 'Actual_Bonus'] = format_currency(actual_info['Bonus'])
                     #   enhanced_predictions.at[idx, 'Team'] = actual_info['Team']
                      #  enhanced_predictions.at[idx, 'Position'] = actual_info['Position']


            
            # Display it
           # for idx, row in enhanced_predictions.iterrows():
            #    with st.container():
             #       if row['Actually_Drafted']:
              #          st.success(f"**{row['Name']}**")
               #         st.write(f"Position: {row['Position']}")
#

 #                       bonus = row['Optimization_Value'] * 9250000

  #                      if bonus >= 1_000_000:
   #                         formatted_bonus = f"${bonus / 1_000_000:.2f}M"
    #                    else:
     #                       formatted_bonus = f"${bonus / 1_000:.0f}K"
#
 #                       st.write(f"Actually drafted: Round {row['Draft_Round']}, Pick {row['Draft_Pick']}, {row['Team']}")
  #                      st.write(f"Predicted Bonus: {formatted_bonus}")
#
                        
                        #st.write(f"Predicted Bonus: {format_optimization_value(row['Optimization_Value']*9250000)}")
                        
 #                       st.write(f"Actual bonus: {row['Actual_Bonus']}")
  #                  else:
   #                     st.info(f"❓ **{row['Name']}**")
    #                    st.write(f"Optimization Value: {format_optimization_value(row['Optimization_Value'])}")
     #                   st.write("Not drafted by this team")
      #              st.write("---")
        
       # with col2:
        #    st.markdown("### Actual Draft Results")
            
         #   if actual_team_df is not None and len(actual_team_df) > 0:
          #      # Sort by pick number
           #     actual_team_df_sorted = actual_team_df.sort_values('Pick')
                
            #    for idx, row in actual_team_df_sorted.iterrows():
             #       player_name = row['Name']
              #      predicted = player_name in predictions_df['Name'].values if predictions_df is not None else False
                    
               #     with st.container():
                #        if predicted:
                 #           st.success(f"**{player_name}**")
                            #st.write("This player was predicted by the model!")
                  #      else:
                   #         st.warning(f"**{player_name}**")
                        
                    #    st.write(f"Position: {row['Position']}")
                     #   st.write(f"Round {row['Round']}, Pick {row['Pick']}")
                      #  st.write(f"Bonus: {format_currency(row['Bonus'])}")
                       # st.write(f"Signed: {'Yes' if row['Signed'] == 'Y' else 'No'}")
                        #st.write("---")
            #else:
             #   st.info("No actual draft data available for this team")


                
    with tab2:


        st.markdown("### Model's Strategy")
        st.markdown("""

        One clear pattern is that the model does NOT choose to save money for later rounds, almost always 
        spending the most money for its first round signing bonus, and very rarely spending more money on a
        later round than is spent in any of the rounds before it. That is generally how the draft goes, but 
        it is interesting that the model was traditional in this manner. It is possible that the model would
        choose more diverse strategies if it was applied to more than the first 4 rounds of the draft. 

        The Arizona Diamondbacks were the only team who spent the most money in any round other than the 
        first, spending a very similar amount of money in their first three picks, but spending the most in 
        the third round. This is likely a reflection of that fact that Arizona picked three times within a 
        span of seven selections.""") 
        
        st.markdown("**Teams with multiple model favorites:**")
        
        team_col1, team_col2, team_col3 = st.columns(3)
        
        with team_col1:
            st.container()
            st.markdown("**Colorado Rockies**")
            st.write("• Brody Brecht *(19 teams)*")
            st.write("• Charlie Condon *(3 teams)*")
            
        with team_col2:
            st.container()
            st.markdown("**Boston Red Sox**") 
            st.write("• Brandon Clarke *(6 teams)*")
            st.write("• Braden Montgomery *(5 teams)*")
            
        with team_col3:
            st.container()
            st.markdown("**Cincinnati Reds**")
            st.write("• Luke Hayden *(3 teams)*")
            st.write("• Tyson Lewis *(3 teams)*")
            
        
      
        
        st.info("""
        The San Diego Padres and Texas Rangers both also had picks the model would classify as very valuable, 
        as the model recommended almost every other team take Kavares Tears and David Hagaman earlier than they were drafted in reality.
        """)

        st.write("---")

    
    
        # model's favorite players data
        favorite_players = {
            "Kavares Tears": 29,
            "David Hagaman": 29,
            "Brody Brecht": 19,
            "Wyatt Sanford": 7,
            "Carson DeMartini": 6,
            "Brandon Clarke": 6,
            "Braden Montgomery": 5,
            "Dasan Hill": 4,
            "Braden Davis": 4,
            "Ryan Stafford": 4,
            "Jac Caglianone": 3,
            "Caleb Lomavita": 3,
            "Luke Hayden": 3,
            "Charlie Condon": 3,
            "Tyson Lewis": 3,
            "Cam Smith": 3,
            "Dakota Jordan": 2
        }
        
        st.markdown("### Model's Favorite Players")
        st.markdown("*Players the optimization model selected most frequently across all 30 teams*")
        
        # display favorite players
        for player_name, team_count in favorite_players.items():
            # Find player in real data
            actual_info = find_player_in_actual_draft(player_name, actual_draft_df) if actual_draft_df is not None else None
            
            with st.container():
                if actual_info is not None:
                    st.success(f"**{player_name}**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Selected by model on {team_count} teams**")
                        st.write(f"Position: {actual_info['Position']}")
                        st.write(f"School: {actual_info.get('School', 'N/A')}")
                    
                    with col2:
                        st.write(f"Actually drafted: Round {actual_info['Round']}, Pick #{actual_info['Pick']}")
                        st.write(f"Team: {actual_info['Team']}")
                        st.write(f"Signing bonus: {format_currency(actual_info['Bonus'])}")
                        st.write(f"Signed: {'Yes' if actual_info['Signed'] == 'Y' else 'No'}")
                else:
                    st.warning(f"**{player_name}**")
                    st.write(f"**Selected by model on {team_count} teams**")
                    st.write("❓ Draft information not found in actual results")
                
        
 
        
       
        
            
            
    with tab3:
        st.subheader("Model Details (Machine Learning/Integer Optimization)")
        st.write("This process involved three separate models:")
        st.write("1. ML model (Multivariate Adaptive Regression Spline) to predict signing bonuses")
        st.write("2. Statistical model (CoxPH survivorship model) to predict when each player will be available")
        st.write("3. Optimization model (iterative Integer Optimization formulations) to optimize selections")
    
        st.write("""**Framework:** For each selection, the model simulated 100 future player availabilities. For example, 
        at a team's first round selection, the model will simulate who will be available at each of their
        future selections as well. These simulations were based on the results of the CoxPH survivorship model.
        Thus, the model can optimize the first round's selection in a global sense. After the 100 simulations of 
        the entire draft, the player who the model selects for the first round is selected. Then, the process 
        continues for the next selection. Each selection also includes the signing bonus, which is predicted for 
        each player at each potential selection using the MARS model.""")
    
        st.write("""**ML model for predicting signing bonus:** The inputs of this model were Fangraph's scouting report data, 
        including FV (future Value) and Risk. Also, the model took into account position, school level (high school or 
        college), and pick number. The output is a predicted signing bonus, as a proportion of that year's largest signing bonus. This is done 
        to ensure consistency in the training data, which were the 2021, 2022, and 2023 draft. When applied on the 2024 draft, 
        the model performed well. A MARS model with degree 2 terms had an out of sample R-squared of 0.93 when applied to the 
        players at their actual pick numbers. This model was applied to each possible combination of player and draft pick selection
        for the optimization model.""")
    
        st.write("""**Statistical survivorship model for predicting likelihood of player availability at each pick:** The inputs of this model 
        are the same as the ML model, excluding the input for pick number, as that is what this model will be predicting. Specifically, 
        the CoxPH model predicts the probability that each player survives (is not drafted) until each possible pick. The model 
        was trained on the 2021, 2022, and 2023 draft, and applied to the 2024 draft data. When applied to the real results from the 2024 
        draft, the model had a test set C-index score of 0.787, implying relatively strong predictive power, compared to a baseline C-index of 
        0.5, which corresponds to no better than random guessing. This model is used to create accurate simulations of future player availabilities.""")
    
        st.write("""**Integer Optimization formulation:** The integer optimization model was run 100 times for each selection, to separately optimize each pick 
        under 100 simulations of future player availabilities. The decision variable was whether each player was selected at each pick. The objective function
        involved maximizing a player's Future Value, as defined by Fangraph's scouting metrics, with a penalty term for the Risk metric, along with a penalty term
        that discriminated against selecting high school players. This high school penalty was small, and only applied to teams in the playoff hunt in 2024, who
        would be less likely to draft a player who is further away from making an impact in MLB. The model was constrained to not exceed the team's real spending
        within the first 4 rounds, as well as to select at most two players from the same position (note: right handed pitchers and left handed pitchers are classified
        as different positions, but left fielders and right fielders, for example, are just classified as outfielders).""")
    
        st.write("Next steps/limitations:")
        st.write("**Players who don't sign:** the model does not include any predictions about which players may not sign, and therefore also fails to take into account the hypothetical value of compensatory picks when this occurs.")
        st.write("**More rounds:** the model only takes into account rounds 1-4, as a result of limited player data. This means that the model is constrained in how creative its strategies can be. For example, drafting players and signing them well above slot value, which is a phenomenon that mostly occurs later in the draft, is not a strategy utilized by this model.")
        st.write("""**More robust iterations:** For example, if a very valuable player is available the second round about 40% of the time, it may be worth it to save the necessary money in 
        the first round in case they are available, even if it is not the most probable outcome. In other words, the model could be improved by including weighting on the value
        of certain simulations depending on the reward that selection achieved. This would make teams less likely to miss out on valuable players who may potentially fall to them 
        in the next round, even if that is relatively unlikely.""")
    
        st.write("Sources: Fangraphs - https://www.fangraphs.com/prospects/the-board/2024-mlb-draft and Baseball America - https://www.baseballamerica.com/draft-results/")
    
        st.write("To see more details and documentation for the models, please visit the GitHub Repository: https://github.com/malcolmgaynor/MLB_draft")
        
    st.markdown("---")
    
    st.write("This project was created by Malcolm Gaynor, and was inspired by and is an extension of a project done at MIT with Atharva Navaratne for Prof Alex Jacquillat's 15.083: Integer Optimization class")   
    
    
    
if __name__ == "__main__":
    main()
