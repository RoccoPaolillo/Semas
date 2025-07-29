import networkx as nx
import matplotlib.pyplot as plt
import numpy
import random
import os
import csv
import pandas as pd
import plotly.express as px
os.chdir("C:/Users/LENOVO/Desktop/eter/data_eter/")

# Acquire the df and keep_2021, a string of ID of universities who are not fine arts or music institutes
df = pd.read_excel('eter_ita.xlsx')
keep2021 =  pd.read_excel('eter_ita.xlsx', sheet_name= "Sheet4")

# To make sure the university is represent at each year from 2011 to 2021
# Count how many REFYEAR levels exist
refyear_levels = df['BAS.REFYEAR'].unique()

# Group by ETERID and count how many unique REFYEARs each one appears in
eterid_refyear_counts = df.groupby('BAS.ETERID')['BAS.REFYEAR'].nunique()

# Keep only ETERIDs that appear in all REFYEAR levels, than to extract those who are not fine arts or music institutes
eterids_in_all_years = eterid_refyear_counts[eterid_refyear_counts == len(refyear_levels)].index
eterids_in_all_years = eterids_in_all_years[eterids_in_all_years.isin(keep2021["BAS.ETERID"])]


# Filter original DataFrame to keep only those ETERIDs. Filtered_df is the dataframe used
filtered_df = df[df['BAS.ETERID'].isin(eterids_in_all_years)]

# Variable reshapes
# aggregated NUTS

nuts_region_map = {
    'ITC': 'NW',
    'ITF': 'S',
    'ITG': 'I',
    'ITH': 'NE',
    'ITI': 'C'
}


filtered_df['AGG.NUTS'] = filtered_df['GEO.NUTS2'].str[:3].map(nuts_region_map)

# Compute percentage men in PhD from Women in PhD
filtered_df["IND.RES.SHAREMENPHDSTUD"] = filtered_df.apply(
    lambda row: 1 - row["IND.RES.SHAREWOMENPHDSTUD"]
    if pd.notnull(row["IND.RES.SHAREWOMENPHDSTUD"]) else None,
    axis=1)

# Functions for extraction ######

# centrality index


def centralityindex(aggvariable, newvariable):
    tt = filtered_df.groupby('BAS.REFYEAR')[aggvariable].sum()
    filtered_df[newvariable] = filtered_df.apply(
        lambda row: row[aggvariable] / tt[row['BAS.REFYEAR']]
        if pd.notnull(row[aggvariable]) else None,
        axis=1
    )

# interactive plot centrality

def plotinteractive(variable, titleinput, labelinput, ):
    plot_data = filtered_df.dropna(subset=[variable])
    
    fig = px.scatter(
    plot_data,
    x='BAS.REFYEAR',
    y= variable,
    title=titleinput,
    labels={
        'BAS.REFYEAR': 'Reference Year',
        variable: labelinput
    },
    opacity=0.6,
    hover_name ='BAS.INSTNAMEENGL',
    hover_data={
        "CLASS.HEISIZE": True,
        "CLASS.EDUCINTENSITY": True,
        "CLASS.MASTERDEGORIENT": True,
        "CLASS.PHDINTENSITY": True,
        "CLASS.SUBJECTCONC": True,
        "ERA.INCOMING_STUDENTS_TOT": True,
        "ERA.OUTGOING_STUDENTS_TOT": True,
        "EUFP.PROJECTS": True,
        "EUFP.PROJECTSFOE01": True,
        "EUFP.PROJECTSFOE02": True,
        "EUFP.PROJECTSFOE03": True,
        "EUFP.PROJECTSFOE04": True,
        "EUFP.PROJECTSFOE05": True,
        "EUFP.PROJECTSFOE06": True,
        "EUFP.PROJECTSFOE07": True,
        "EUFP.PROJECTSFOE08": True,
        "EUFP.PROJECTSFOE09": True,
        "EUFP.PROJECTSRIA": True,
        "EUFP.PROJECTSIA": True,
        "EUFP.PROJECTSCSA": True,
        "EUFP.PROJECTSERC": True},
    color='AGG.NUTS' ,
    size = "RES.STUDISCED8TOTAL")
    
    fig.update_layout(
    plot_bgcolor='white',      # Plot (chart) background
    paper_bgcolor='white',     # Entire figure background
    xaxis=dict(
        title='Reference Year',
        type='category',
        categoryorder='array',
        categoryarray=sorted(plot_data['BAS.REFYEAR'].unique())
        ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgray'
    )
    )
    
    output = fig.write_html(variable + ".html")
    
    return output


##### boxplot percentage gender enrolled in PhD

# Prepare and reshape the data for combined gender boxplot
female_data = filtered_df[['BAS.REFYEAR', 'IND.RES.SHAREWOMENPHDSTUD']].dropna().copy()
female_data['SHAREGENDER'] = female_data['IND.RES.SHAREWOMENPHDSTUD']
female_data['GENDER'] = 'Female'

male_data = filtered_df[['BAS.REFYEAR', 'IND.RES.SHAREMENPHDSTUD']].dropna().copy()
male_data['SHAREGENDER'] = male_data['IND.RES.SHAREMENPHDSTUD']
male_data['GENDER'] = 'Male'

# Combine into one DataFrame
combined_data = pd.concat([female_data[['BAS.REFYEAR', 'SHAREGENDER', 'GENDER']],
                           male_data[['BAS.REFYEAR', 'SHAREGENDER', 'GENDER']]])

# Convert REFYEAR to string for proper grouping
combined_data['BAS.REFYEAR'] = combined_data['BAS.REFYEAR'].astype(str)

# Create grouped boxplot
plt.figure(figsize=(14, 6))
years = sorted(combined_data['BAS.REFYEAR'].unique())
positions = range(1, len(years) + 1)

# Boxplot for females
female_plot_data = [combined_data[(combined_data['BAS.REFYEAR'] == year) & (combined_data['GENDER'] == 'Female')]['SHAREGENDER']
                    for year in years]
bplot1 = plt.boxplot(female_plot_data, positions=[p - 0.2 for p in positions], widths=0.35, patch_artist=True,
                     boxprops=dict(facecolor='lightpink'), labels=years)

# Boxplot for males
male_plot_data = [combined_data[(combined_data['BAS.REFYEAR'] == year) & (combined_data['GENDER'] == 'Male')]['SHAREGENDER']
                  for year in years]
bplot2 = plt.boxplot(male_plot_data, positions=[p + 0.2 for p in positions], widths=0.35, patch_artist=True,
                     boxprops=dict(facecolor='lightblue'))

# Axis labels and title
plt.xlabel('Reference Year')
plt.ylabel('Share of PhD Students')
plt.title('Boxplot of Share of PhD Students by Gender and Year')
plt.xticks(ticks=positions, labels=years)
plt.grid(True)
plt.legend([bplot1["boxes"][0], bplot2["boxes"][0]], ['Female', 'Male'], loc='upper right')
plt.tight_layout()
plt.savefig("boxplot_sharegender.png", dpi=300, bbox_inches='tight')
plt.show()



##### Centrality interactive plots ######


centralityindex('RES.STUDISCED8WOMEN','centrality_womenphd')
plotinteractive('centrality_womenphd','Centrality of Women PhD by Year. Size = Total students in ISCED8','Centrality of Women PhD')

centralityindex('RES.STUDISCED8MEN','centrality_menphd')
plotinteractive('centrality_menphd','Centrality of Men PhD by Year. Size = Total students in ISCED8','Centrality of Men PhD')

centralityindex('RES.STUDISCED8FOE05','centrality_nat05')
plotinteractive('centrality_nat05','Centrality PhD Natural sciences, mathematics and statistics by Year. Size = Total students in ISCED8','Centrality PhD Natural sciences, mathematics and statistics')

centralityindex('RES.STUDISCED8FOE01','centrality_edu01')
plotinteractive('centrality_edu01','Centrality PhD Education by Year. Size = Total students in ISCED8','Centrality PhD Education')

centralityindex('RES.STUDISCED8FOE02','centrality_hum02')
plotinteractive('centrality_hum02','Centrality PhD Arts and Humanities by Year. Size = Total students in ISCED8','Centrality PhD Arts and Humanities')

centralityindex('RES.STUDISCED8FOE03','centrality_soc03')
plotinteractive('centrality_soc03','Centrality PhD Social Sciences, Journalism and Information by Year. Size = Total students in ISCED8','Centrality PhD Social Sciences, Journalism and Information')

centralityindex('RES.STUDISCED8FOE04','centrality_bus04')
plotinteractive('centrality_bus04','Centrality PhD Business, Administration and Law by Year. Size = Total students in ISCED8','Centrality PhD Business, Administration and Law')

centralityindex('RES.STUDISCED8FOE06','centrality_ict06')
plotinteractive('centrality_ict06','Centrality PhD Information, Communication and Technology by Year. Size = Total students in ISCED8','Centrality PhD Information, Communication and Technology')

centralityindex('RES.STUDISCED8FOE07','centrality_eng07')
plotinteractive('centrality_eng07','Centrality PhD Engineering, manufacturing and construction by Year. Size = Total students in ISCED8','Centrality PhD Engineering, manufacturing and construction')

centralityindex('RES.STUDISCED8FOE08','centrality_agr08')
plotinteractive('centrality_agr08','Centrality PhD Agriculture, forestry, fisheries and veterinary by Year. Size = Total students in ISCED8','Centrality PhD Agriculture, forestry, fisheries and veterinary')

centralityindex('RES.STUDISCED8FOE09','centrality_health09')
plotinteractive('centrality_health09','Centrality PhD Health and welfare by Year. Size = Total students in ISCED8','Centrality PhD Health and welfare')

centralityindex('RES.STUDISCED8FOE10','centrality_ser10')
plotinteractive('centrality_ser10','Centrality PhD Services by Year. Size = Total students in ISCED8','Centrality PhD Services')
