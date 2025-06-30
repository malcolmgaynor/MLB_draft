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
        # First, try to read normally
        df = pd.read_csv(file_path)
        
        # Debug info
        st.write(f"Debug: Raw DataFrame shape: {df.shape}")
        st.write(f"Debug: Raw columns: {list(df.columns)}")
        st.write(f"Debug: First few raw rows:")
        st.write(df.head())
        
        # Check if the first row contains data type information (Any, Float64, etc.)
        if len(df) > 0 and str(df.iloc[0, 0]).strip() in ['Any', 'String', 'Float64', 'Int64']:
            st.info("Detected Julia DataFrame format - removing type row")
            df = df.iloc[1:].reset_index(drop=True)
        
        # Check if columns have expected names
        if df.shape[1] >= 2:
            # Rename columns to standard names if they don't match
            if 'Name' not in df.columns or 'Bonus' not in df.columns:
                df.columns = ['Name', 'Bonus'] + list(df.columns[2:])
        
        # Clean up the data
        df = df.dropna(subset=['Name'])  # Remove rows where Name is NaN
        
        # Convert Bonus column to numeric
        if 'Bonus' in df.columns:
            df['Bonus'] = pd.to_numeric(df['Bonus'], errors='coerce')
        
        st.write(f"Debug: Cleaned DataFrame shape: {df.shape}")
        st.write(f"Debug: Cleaned columns: {list(df.columns)}")
        st.write(f"Debug: Cleaned data:")
        st.write(df.head())
        
        return df
    except FileNotFoundError:
        st.error(f"File not found: output_{team_abbrev}.csv")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_bonus_value(bonus):
    """Format bonus value - handles decimal probability values"""
    try:
        if pd.isna(bonus) or bonus == '' or bonus == 0:
            return "Not disclosed"
        
        # Convert to float
        bonus_float = float(bonus)
        
        # These appear to be probability/optimization values between 0 and 1
        if 0 <= bonus_float <= 1:
            return f"{bonus_float:.6f}"
        
        # If somehow larger than 1, treat as currency
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
                    # Get valid numeric bonuses
                    valid_bonuses = df['Bonus'].dropna()
                    valid_bonuses = valid_bonuses[valid_bonuses != 0]
                    
                    with col2:
                        if len(valid_bonuses) > 0:
                            total_bonus = valid_bonuses.sum()
                            st.metric("Total Optimization Values", f"{total_bonus:.6f}")
                        else:
                            st.metric("Total Values", "N/A")
                    
                    with col3:
                        if len(valid_bonuses) > 0:
                            avg_bonus = valid_bonuses.mean()
                            st.metric("Average Value", f"{avg_bonus:.6f}")
                        else:
                            st.metric("Average Value", "N/A")
                    
                    with col4:
                        if len(valid_bonuses) > 0:
                            max_bonus = valid_bonuses.max()
                            st.metric("Highest Value", f"{max_bonus:.6f}")
                        else:
                            st.metric("Highest Value", "N/A")
                else:
                    with col2:
                        st.metric("Total Values", "No data")
                    with col3:
                        st.metric("Average Value", "No data")
                    with col4:
                        st.metric("Highest Value", "No data")
                
                st.markdown("---")
                
                # Format the dataframe for display
                display_df = df.copy()
                
                # Format bonus column if it exists
                if 'Bonus' in display_df.columns:
                    display_df['Optimization_Value'] = display_df['Bonus'].apply(format_bonus_value)
                
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
                    elif col == 'Optimization_Value':
                        display_columns[col] = st.column_config.TextColumn(
                            "Optimization Value",
                            help="Optimization/probability value",
                            width="medium"
                        )
                    elif col == 'Bonus':
                        display_columns[col] = st.column_config.NumberColumn(
                            "Raw Value",
                            help="Raw optimization value",
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
