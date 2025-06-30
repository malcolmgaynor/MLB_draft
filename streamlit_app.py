import streamlit as st import pandas as pd import os from pathlib import Path # MLB team abbreviations and full names MLB_TEAMS = { 'ARI': 'Arizona Diamondbacks', 'ATL': 'Atlanta Braves', 'BAL': 'Baltimore Orioles', 'BOS': 'Boston Red Sox', 'CHC': 'Chicago Cubs', 'CHW': 'Chi

pasted

I am using this code to make a Strealit app: 

However, the output, for example, looks like this: 

4×2 DataFrame
 Row │ Name            Bonus
     │ Any             Float64
─────┼───────────────────────────
   1 │ Brody Brecht    0.309059
   2 │ Kavares Tears   0.143914
   3 │ David Hagaman   0.0781436
   4 │ Brandon Clarke  0.0478485

And it claims that there is only one player selected for this team.

Looking at your code and the output you're showing, I can see a few issues that are causing the problems you're experiencing:

The data format is different than expected: Your CSV appears to have decimal values (like 0.309059) in the Bonus column, but your code expects actual dollar amounts that it can format as currency.
Row counting issue: The code is counting DataFrame rows correctly with len(df), but if it's showing "only one player selected," there might be an issue with how the data is being loaded or filtered.
Let me create an improved version of your Streamlit app that better handles the data format you're actually working with:


Improved MLB Draft Data Viewer
Code 
The key improvements in this updated version:

Added Debug Information: The load_team_data function now shows the actual DataFrame shape, columns, and first few rows so you can see exactly what's being loaded.
Better Bonus Value Handling: The format_bonus_value function now detects if the bonus values are decimal numbers (like 0.309059) and displays them appropriately rather than trying to format them as currency.
Improved Numeric Processing: The get_numeric_bonus_values function properly extracts numeric values for calculations.
Enhanced Data Display: Shows both raw bonus values and formatted versions, and handles cases where the bonus values appear to be probabilities or percentages rather than dollar amounts.
Better Error Handling: More robust handling of edge cases and data format issues.
The debug information will help you understand exactly what data is being loaded. Based on your example output showing decimal values like 0.309059, it looks like your "Bonus" column might contain probability values or some other metric rather than actual dollar amounts.

Run this updated version and check the debug output to see:

How many rows are actually being loaded
What the column names are
What the actual data



import streamlit as st
import pandas as pd
import os
from pathlib import Path

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

def get_available_teams(data_directory="Optimization_CSVs"):
    """Get list of teams that have CSV files available"""
    available_teams = []
    for abbrev in MLB_TEAMS.keys():
        file_path = Path(data_directory) / f"output_{abbrev}.csv"
        if file_path.exists():
            available_teams.append(abbrev)
    return available_teams

def load_team_data(team_abbrev, data_directory="Optimization_CSVs"):
    """Load CSV data for a specific team"""
    file_path = Path(data_directory) / f"output_{team_abbrev}.csv"
    try:
        df = pd.read_csv(file_path)
        # Debug info
        st.write(f"Debug: Loaded DataFrame shape: {df.shape}")
        st.write(f"Debug: Columns: {list(df.columns)}")
        st.write(f"Debug: First few rows:")
        st.write(df.head())
        return df
    except FileNotFoundError:
        st.error(f"File not found: output_{team_abbrev}.csv")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_bonus_value(bonus):
    """Format bonus value - handles both decimal values and currency amounts"""
    try:
        if pd.isna(bonus) or bonus == '' or bonus == 0:
            return "Not disclosed"
        
        # Convert to float if it's a string
        if isinstance(bonus, str):
            # Remove any currency symbols and commas
            bonus_clean = bonus.replace('$', '').replace(',', '')
            try:
                bonus_float = float(bonus_clean)
            except ValueError:
                return bonus  # Return original if can't convert
        else:
            bonus_float = float(bonus)
        
        # Check if this looks like a decimal probability/percentage (0-1 range)
        if 0 <= bonus_float <= 1:
            return f"{bonus_float:.6f}"  # Show as decimal with more precision
        
        # Otherwise treat as currency
        if bonus_float >= 1000000:
            return f"${bonus_float/1000000:.2f}M"
        elif bonus_float >= 1000:
            return f"${bonus_float/1000:.0f}K"
        else:
            return f"${bonus_float:,.2f}"
    except:
        return str(bonus)

def get_numeric_bonus_values(bonus_series):
    """Extract numeric values from bonus column for calculations"""
    numeric_values = []
    for bonus in bonus_series:
        try:
            if pd.isna(bonus) or bonus == '' or bonus == 0:
                continue
            
            if isinstance(bonus, str):
                bonus_clean = bonus.replace('$', '').replace(',', '')
                try:
                    numeric_values.append(float(bonus_clean))
                except ValueError:
                    continue
            else:
                numeric_values.append(float(bonus))
        except:
            continue
    
    return numeric_values

def main():
    st.set_page_config(
        page_title="MLB Draft Data Viewer",
        page_icon="⚾",
        layout="wide"
    )
    
    st.title("⚾ MLB Draft Data Viewer")
    st.markdown("View MLB draft picks and signing bonuses by team")
    
    # Get available teams
    available_teams = get_available_teams()
    
    if not available_teams:
        st.error("No CSV files found in the 'Optimization_CSVs' folder. Please ensure your CSV files are named 'output_[TEAM].csv' and located in the Optimization_CSVs directory.")
        st.info("Expected file format: Optimization_CSVs/output_ARI.csv, Optimization_CSVs/output_BOS.csv, etc.")
        return
    
    # Create dropdown options with team names
    team_options = {f"{MLB_TEAMS[abbrev]} ({abbrev})": abbrev for abbrev in sorted(available_teams)}
    
    # Team selection dropdown
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_team_display = st.selectbox(
            "Select a team:",
            options=list(team_options.keys()),
            index=0
        )
        
        selected_team_abbrev = team_options[selected_team_display]
    
    # Load and display data
    if selected_team_abbrev:
        with st.spinner(f"Loading data for {MLB_TEAMS[selected_team_abbrev]}..."):
            df = load_team_data(selected_team_abbrev)
            
            if df is not None:
                # Check if DataFrame is actually empty or has issues
                if len(df) == 0:
                    st.warning(f"No data found for {MLB_TEAMS[selected_team_abbrev]}")
                    return
                
                st.success(f"Loaded {len(df)} draft picks for {MLB_TEAMS[selected_team_abbrev]}")
                
                # Display summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Players", len(df))
                
                # Handle bonus statistics if Bonus column exists
                if 'Bonus' in df.columns:
                    numeric_bonuses = get_numeric_bonus_values(df['Bonus'])
                    
                    with col2:
                        if numeric_bonuses:
                            total_bonus = sum(numeric_bonuses)
                            # Check if values look like probabilities (all between 0-1)
                            if all(0 <= val <= 1 for val in numeric_bonuses):
                                st.metric("Total Bonus Values", f"{total_bonus:.6f}")
                            else:
                                st.metric("Total Bonuses", format_bonus_value(total_bonus))
                        else:
                            st.metric("Total Bonuses", "N/A")
                    
                    with col3:
                        if numeric_bonuses:
                            avg_bonus = sum(numeric_bonuses) / len(numeric_bonuses)
                            if all(0 <= val <= 1 for val in numeric_bonuses):
                                st.metric("Average Bonus Value", f"{avg_bonus:.6f}")
                            else:
                                st.metric("Average Bonus", format_bonus_value(avg_bonus))
                        else:
                            st.metric("Average Bonus", "N/A")
                    
                    with col4:
                        if numeric_bonuses:
                            max_bonus = max(numeric_bonuses)
                            if all(0 <= val <= 1 for val in numeric_bonuses):
                                st.metric("Highest Bonus Value", f"{max_bonus:.6f}")
                            else:
                                st.metric("Highest Bonus", format_bonus_value(max_bonus))
                        else:
                            st.metric("Highest Bonus", "N/A")
                else:
                    with col2:
                        st.metric("Total Bonuses", "No bonus data")
                    with col3:
                        st.metric("Average Bonus", "No bonus data")
                    with col4:
                        st.metric("Highest Bonus", "No bonus data")
                
                st.markdown("---")
                
                # Format the dataframe for display
                display_df = df.copy()
                
                # Format bonus column if it exists
                if 'Bonus' in display_df.columns:
                    display_df['Bonus_Formatted'] = display_df['Bonus'].apply(format_bonus_value)
                
                # Display the data
                st.subheader(f"{MLB_TEAMS[selected_team_abbrev]} Draft Picks")
                
                # Add search functionality
                if len(df) > 10:
                    search_term = st.text_input("🔍 Search players:", placeholder="Enter player name...")
                    if search_term and 'Name' in display_df.columns:
                        mask = display_df['Name'].str.contains(search_term, case=False, na=False)
                        display_df = display_df[mask]
                        st.info(f"Found {len(display_df)} players matching '{search_term}'")
                
                # Prepare columns for display
                display_columns = {}
                for col in display_df.columns:
                    if col == 'Name':
                        display_columns[col] = st.column_config.TextColumn(
                            "Player Name",
                            help="Name of the drafted player",
                            width="large"
                        )
                    elif col == 'Bonus_Formatted':
                        display_columns[col] = st.column_config.TextColumn(
                            "Signing Bonus",
                            help="Signing bonus amount",
                            width="medium"
                        )
                    elif col == 'Bonus':
                        display_columns[col] = st.column_config.NumberColumn(
                            "Bonus (Raw)",
                            help="Raw bonus value",
                            width="medium",
                            format="%.6f"
                        )
                
                # Display table with better formatting
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config=display_columns,
                    height=400
                )
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {selected_team_abbrev} data as CSV",
                    data=csv,
                    file_name=f"output_{selected_team_abbrev}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
