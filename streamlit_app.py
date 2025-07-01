### TODO: 
# verify that all findings make some sort of sense (draft number and bonus) 
# make another tab for wider results
# make another tab explaining the modeling
# make a public github (this one should be private, backend only) 






import streamlit as st
import pandas as pd
import os
from pathlib import Path
import re

# MLB team abbreviations and full names
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
    'OAK': 'Oakland Athletics',
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

# Team name mappings for the actual draft data
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
    'Oakland Athletics': 'OAK',
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
        file_path = Path(data_directory) / f"output_{abbrev}.csv"
        if file_path.exists():
            available_teams.append(abbrev)
    return available_teams

def load_actual_draft_data(data_directory="Optimization_CSVs"):
    """Load the actual draft results data"""
    file_path = Path(data_directory) / "data_ba-results.csv"
    try:
        df = pd.read_csv(file_path)
        
        # Add team abbreviation column for easier filtering
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
    file_path = Path(data_directory) / f"output_{team_abbrev}.csv"
    try:
        df = pd.read_csv(file_path)
        
        # Check if this is a Julia-style concatenated format (1 row, 1 column)
        if df.shape == (1, 1):
            # Get the raw string data
            raw_data = str(df.iloc[0, 0])
            
            # Parse the concatenated string
            players = []
            bonuses = []
            
            # Look for pattern: number │ name number
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
        
        # Handle standard CSV format
        elif len(df) > 0 and str(df.iloc[0, 0]).strip() in ['Any', 'String', 'Float64', 'Int64']:
            df = df.iloc[1:].reset_index(drop=True)
        
        # Standardize column names
        if df.shape[1] >= 2:
            if 'Name' not in df.columns or ('Bonus' not in df.columns and 'Optimization_Value' not in df.columns):
                df.columns = ['Name', 'Optimization_Value'] + list(df.columns[2:])
        
        # Clean up the data
        if 'Name' in df.columns:
            df = df.dropna(subset=['Name'])
        
        # Convert optimization value column to numeric
        opt_col = 'Optimization_Value' if 'Optimization_Value' in df.columns else 'Bonus'
        if opt_col in df.columns:
            df[opt_col] = pd.to_numeric(df[opt_col], errors='coerce')
            if opt_col == 'Bonus':
                df = df.rename(columns={'Bonus': 'Optimization_Value'})
        
        return df
    except FileNotFoundError:
        st.error(f"File not found: output_{team_abbrev}.csv")
        return None
    except Exception as e:
        st.error(f"Error loading prediction data: {str(e)}")
        return None

def format_currency(amount):
    """Format currency amounts"""
    try:
        if pd.isna(amount) or amount == '' or amount == 0:
            return "NA"
        
        # Clean the amount if it's a string
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
    
    # Try exact match first
    exact_match = actual_draft_df[actual_draft_df['Name'].str.strip() == player_name.strip()]
    if not exact_match.empty:
        return exact_match.iloc[0]
    
    # Try partial match
    partial_match = actual_draft_df[actual_draft_df['Name'].str.contains(player_name.strip(), case=False, na=False)]
    if not partial_match.empty:
        return partial_match.iloc[0]
    
    return None

def main():
    st.set_page_config(
        page_title="2024 MLB Draft Analysis: Integer Optimization Model",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("⚾ 2024 MLB Draft Analysis: Integer Optimization Model")
    #st.markdown("Compare your optimization model's predictions with actual draft results")
    
    # Load actual draft data
    actual_draft_df = load_actual_draft_data()
    
    # Get available teams
    available_teams = get_available_teams()
    
    if not available_teams:
        st.error("No optimization CSV files found in the 'Optimization_CSVs' folder.")
        return
    
    # Create dropdown options with team names
    team_options = {f"{MLB_TEAMS[abbrev]} ({abbrev})": abbrev for abbrev in sorted(available_teams)}
    
    # Team selection
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
    
    # Filter actual draft data for selected team
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
    
    # Create tabs for different views
    #tab1, tab2, tab3 = st.tabs(["📊 Side-by-Side Comparison", "🤖 Model Predictions", "📋 Actual Draft Results"])
    tab1, tab2, tab3 = st.tabs(["Optimization Model vs. Real Draft Results", "Overall Takeaways", "Model details (Machine Learning/Integer Optimization"])

    
    with tab1:
        st.subheader(f"Comparison for {selected_team_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Optimization Model Results")
            
            # Enhanced predictions display with actual draft info
            enhanced_predictions = predictions_df.copy()
            enhanced_predictions['Actually_Drafted'] = False
            enhanced_predictions['Draft_Round'] = ""
            enhanced_predictions['Draft_Pick'] = ""
            enhanced_predictions['Actual_Bonus'] = ""
            enhanced_predictions['Team'] = ""
            enhanced_predictions['Position'] =""
            
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


            
            # Display enhanced predictions
            for idx, row in enhanced_predictions.iterrows():
                with st.container():
                    if row['Actually_Drafted']:
                        st.success(f"**{row['Name']}**")
                        st.write(f"Position: {row['Position']}")


                        bonus = row['Optimization_Value'] * 9250000

                        if bonus >= 1_000_000:
                            formatted_bonus = f"${bonus / 1_000_000:.2f}M"
                        else:
                            formatted_bonus = f"${bonus / 1_000:.0f}K"
                        
                        st.write(f"Predicted Bonus: {formatted_bonus}")

                        
                        #st.write(f"Predicted Bonus: {format_optimization_value(row['Optimization_Value']*9250000)}")
                        st.write(f"Actually drafted: Round {row['Draft_Round']}, Pick {row['Draft_Pick']}, {row['Team']}")
                        st.write(f"Actual bonus: {row['Actual_Bonus']}")
                    else:
                        st.info(f"❓ **{row['Name']}**")
                        st.write(f"Optimization Value: {format_optimization_value(row['Optimization_Value'])}")
                        st.write("Not drafted by this team")
                    st.write("---")
        
        with col2:
            st.markdown("### Actual Draft Results")
            
            if actual_team_df is not None and len(actual_team_df) > 0:
                # Sort by pick number
                actual_team_df_sorted = actual_team_df.sort_values('Pick')
                
                for idx, row in actual_team_df_sorted.iterrows():
                    player_name = row['Name']
                    predicted = player_name in predictions_df['Name'].values if predictions_df is not None else False
                    
                    with st.container():
                        if predicted:
                            st.success(f"**{player_name}**")
                            #st.write("This player was predicted by the model!")
                        else:
                            st.warning(f"**{player_name}**")
                        
                        st.write(f"Round {row['Round']}, Pick {row['Pick']}")
                        st.write(f"Position: {row['Position']}")
                        st.write(f"Bonus: {format_currency(row['Bonus'])}")
                        st.write(f"Signed: {'Yes' if row['Signed'] == 'Y' else 'No'}")
                        st.write("---")
            else:
                st.info("No actual draft data available for this team")
                
    with tab2:
        st.subheader("Overall Takeaways")
        st.write("Details about the overall results")
        # Add your actual content here
        
    with tab3:
        st.subheader("Model Details (Machine Learning/Integer Optimization)")
        st.write("Details about the model")

    
    # Download buttons
    st.markdown("---")
    st.markdown("### Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if predictions_df is not None:
            csv_predictions = predictions_df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download Model Predictions ({selected_team_abbrev})",
                data=csv_predictions,
                file_name=f"model_predictions_{selected_team_abbrev}.csv",
                mime="text/csv"
            )
    
    with col2:
        if actual_team_df is not None and len(actual_team_df) > 0:
            csv_actual = actual_team_df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download Actual Results ({selected_team_abbrev})",
                data=csv_actual,
                file_name=f"actual_results_{selected_team_abbrev}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
