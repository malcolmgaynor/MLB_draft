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

def load_team_data(team_abbrev, data_directory="."):
    """Load CSV data for a specific team"""
    file_path = Path(data_directory) / f"output_{team_abbrev}.csv"
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"File not found: output_{team_abbrev}.csv")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_bonus(bonus):
    """Format bonus amount as currency"""
    try:
        if pd.isna(bonus) or bonus == '' or bonus == 0:
            return "Not disclosed"
        
        # Convert to float if it's a string
        if isinstance(bonus, str):
            # Remove any currency symbols and commas
            bonus_clean = bonus.replace('$', '').replace(',', '')
            try:
                bonus = float(bonus_clean)
            except ValueError:
                return bonus  # Return original if can't convert
        
        if bonus >= 1000000:
            return f"${bonus/1000000:.2f}M"
        elif bonus >= 1000:
            return f"${bonus/1000:.0f}K"
        else:
            return f"${bonus:,.2f}"
    except:
        return str(bonus)

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
        st.error("No CSV files found. Please ensure your CSV files are named 'output_[TEAM].csv' and located in the same directory as this script.")
        st.info("Expected file format: output_ARI.csv, output_BOS.csv, etc.")
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
                st.success(f"Loaded {len(df)} draft picks for {MLB_TEAMS[selected_team_abbrev]}")
                
                # Display summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Players", len(df))
                
                with col2:
                    if 'Bonus' in df.columns:
                        # Calculate total bonus (excluding non-numeric values)
                        numeric_bonuses = pd.to_numeric(df['Bonus'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
                        total_bonus = numeric_bonuses.sum()
                        if total_bonus > 0:
                            st.metric("Total Bonuses", format_bonus(total_bonus))
                        else:
                            st.metric("Total Bonuses", "N/A")
                
                with col3:
                    if 'Bonus' in df.columns:
                        avg_bonus = numeric_bonuses.mean()
                        if not pd.isna(avg_bonus) and avg_bonus > 0:
                            st.metric("Average Bonus", format_bonus(avg_bonus))
                        else:
                            st.metric("Average Bonus", "N/A")
                
                with col4:
                    if 'Bonus' in df.columns:
                        max_bonus = numeric_bonuses.max()
                        if not pd.isna(max_bonus) and max_bonus > 0:
                            st.metric("Highest Bonus", format_bonus(max_bonus))
                        else:
                            st.metric("Highest Bonus", "N/A")
                
                st.markdown("---")
                
                # Format the dataframe for display
                display_df = df.copy()
                
                # Format bonus column if it exists
                if 'Bonus' in display_df.columns:
                    display_df['Bonus'] = display_df['Bonus'].apply(format_bonus)
                
                # Display the data
                st.subheader(f"{MLB_TEAMS[selected_team_abbrev]} Draft Picks")
                
                # Add search functionality
                if len(df) > 10:
                    search_term = st.text_input("🔍 Search players:", placeholder="Enter player name...")
                    if search_term:
                        mask = display_df['Name'].str.contains(search_term, case=False, na=False)
                        display_df = display_df[mask]
                        st.info(f"Found {len(display_df)} players matching '{search_term}'")
                
                # Display table
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
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
