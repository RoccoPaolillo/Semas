import networkx as nx
import matplotlib.pyplot as plt
import numpy
import random
import os
import csv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

os.chdir("C:/Users/LENOVO/Documents/GitHub/Semas/data_eter/")

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
# color mapping
nuts_colors = {
    "S": "red",
    "I": "orange",
    "C": "green",
    "NW": "blue",
    "NE": "violet"
}

# to compose filtered df actually used in analysis
filtered_df['AGG.NUTS'] = filtered_df['GEO.NUTS2'].str[:3].map(nuts_region_map)
# Compute percentage men in PhD from Women in PhD
filtered_df["IND.RES.SHAREMENPHDSTUD"] = filtered_df.apply(
    lambda row: 1 - row["IND.RES.SHAREWOMENPHDSTUD"]
    if pd.notnull(row["IND.RES.SHAREWOMENPHDSTUD"]) else None,
    axis=1)

# Functions for centrality index ######

# centrality index


def centralityindex(dforig, aggvariable, newvariable):
    tt = dforig.groupby('BAS.REFYEAR')[aggvariable].sum()
    dforig[newvariable] = dforig.apply(
        lambda row: row[aggvariable] / tt[row['BAS.REFYEAR']]
        if pd.notnull(row[aggvariable]) else None,
        axis=1
    )

# interactive plot centrality

def plotinteractive(name_df, dforig,variable, titleinput, labelinput, color_map = None):
    plot_data = dforig.dropna(subset=[variable])
    if not pd.api.types.is_string_dtype(plot_data["BAS.REFYEAR"]):
        plot_data["BAS.REFYEAR"] = plot_data["BAS.REFYEAR"].astype(str)
    
    year_totals = plot_data.groupby("BAS.REFYEAR")["RES.STUDISCED8TOTAL"].transform("sum")
    plot_data["prop_RES_STUDISCED8TOTAL"] = plot_data["RES.STUDISCED8TOTAL"] / year_totals
    
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
        "EUFP.PROJECTSERC": True,
        "RES.R&DEXP.EURO": True},
    color='AGG.NUTS' ,
    size="prop_RES_STUDISCED8TOTAL", 
    color_discrete_map=color_map)
    
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
    
    output = fig.write_html(name_df + variable + ".html")
    
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


centralityindex(filtered_df,'RES.STUDISCED8WOMEN','centrality_womenphd')
plotinteractive("all_", filtered_df,'centrality_womenphd','Centrality of Women PhD by Year. Size = Prop total students in ISCED8','Centrality of Women PhD',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8MEN','centrality_menphd')
plotinteractive("all_", filtered_df,'centrality_menphd','Centrality of Men PhD by Year. Size = Prop total students in ISCED8','Centrality of Men PhD',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE05','centrality_nat05')
plotinteractive("all_", filtered_df,'centrality_nat05','Centrality PhD Natural sciences, mathematics and statistics by Year. Size = Prop total students in ISCED8','Centrality PhD Natural sciences, mathematics and statistics',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE01','centrality_edu01')
plotinteractive("all_", filtered_df,'centrality_edu01','Centrality PhD Education by Year. Size = Prop total students in ISCED8','Centrality PhD Education',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE02','centrality_hum02')
plotinteractive("all_", filtered_df,'centrality_hum02','Centrality PhD Arts and Humanities by Year. Size = Prop total students in ISCED8','Centrality PhD Arts and Humanities',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE03','centrality_soc03')
plotinteractive("all_", filtered_df,'centrality_soc03','Centrality PhD Social Sciences, Journalism and Information by Year. Size = Prop total students in ISCED8','Centrality PhD Social Sciences, Journalism and Information',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE04','centrality_bus04')
plotinteractive("all_", filtered_df,'centrality_bus04','Centrality PhD Business, Administration and Law by Year. Size = Prop total students in ISCED8','Centrality PhD Business, Administration and Law',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE06','centrality_ict06')
plotinteractive("all_", filtered_df,'centrality_ict06','Centrality PhD Information, Communication and Technology by Year. Size = Prop total students in ISCED8','Centrality PhD Information, Communication and Technology',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE07','centrality_eng07')
plotinteractive("all_", filtered_df,'centrality_eng07','Centrality PhD Engineering, manufacturing and construction by Year. Size = Prop total students in ISCED8','Centrality PhD Engineering, manufacturing and construction',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE08','centrality_agr08')
plotinteractive("all_", filtered_df,'centrality_agr08','Centrality PhD Agriculture, forestry, fisheries and veterinary by Year. Size = Prop total students in ISCED8','Centrality PhD Agriculture, forestry, fisheries and veterinary',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE09','centrality_health09')
plotinteractive("all_", filtered_df,'centrality_health09','Centrality PhD Health and welfare by Year. Size = Prop total students in ISCED8','Centrality PhD Health and welfare',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8FOE10','centrality_ser10')
plotinteractive("all_", filtered_df,'centrality_ser10','Centrality PhD Services by Year. Size = Prop total students in ISCED8','Centrality PhD Services',color_map=nuts_colors)

centralityindex(filtered_df,'RES.STUDISCED8TOTAL','centrality_tot')
plotinteractive("all_", filtered_df,'centrality_tot','Centrality Total PhD by Year. Size = Prop total PhD student','Centrality Total PhD',color_map=nuts_colors)



############ Yearly new enrollments
# function used to extract difference year by year

def add_diffyear(dforig,
                            value_col,
                            inst_col="Ateneo_Eter",
                            year_col="BAS.REFYEAR"):
    """
    For each institution, compute value_col(t) - value_col(t-1)
    and write it to a new column named 'ydiff_<value_col>'.
    """
    if dforig is None:
        raise ValueError("Input DataFrame is None. Did you overwrite df with a None object?")

    # Make a copy sorted by institution and year
    dforig = dforig.sort_values([inst_col, year_col]).copy()

    # Define output column name
    out_col = "ydiff_" + value_col

    # Compute year-over-year difference within groups
    dforig[out_col] = dforig.groupby(inst_col)[value_col].diff()

    return dforig

filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8TOTAL" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE01" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE02" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE03" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE04" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE05" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE06" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE07" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE08" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE09" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8FOE10" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8MEN" )
filtered_df = add_diffyear(filtered_df,value_col="RES.STUDISCED8WOMEN" )



## aggregated by NUTS
# variables to include
cols = [
    "RES.STUDISCED8MEN",
    "RES.STUDISCED8WOMEN",
    "RES.STUDISCED8FOE01",
    "RES.STUDISCED8FOE02",
    "RES.STUDISCED8FOE03",
    "RES.STUDISCED8FOE04",
    "RES.STUDISCED8FOE05",
    "RES.STUDISCED8FOE06",
    "RES.STUDISCED8FOE07",
    "RES.STUDISCED8FOE08",
    "RES.STUDISCED8FOE09",
    "RES.STUDISCED8FOE10",
    "RES.STUDISCED8TOTAL",
    "ERA.INCOMING_STUDENTS_TOT",
    "ERA.OUTGOING_STUDENTS_TOT",
    "EUFP.PROJECTS",
    "EUFP.PROJECTSFOE01",
    "EUFP.PROJECTSFOE02",
    "EUFP.PROJECTSFOE03",
    "EUFP.PROJECTSFOE04",
    "EUFP.PROJECTSFOE05",
    "EUFP.PROJECTSFOE06",
    "EUFP.PROJECTSFOE07",
    "EUFP.PROJECTSFOE08",
    "EUFP.PROJECTSFOE09",
    "EUFP.PROJECTSRIA",
    "EUFP.PROJECTSIA",
    "EUFP.PROJECTSCSA",
    "EUFP.PROJECTSERC",
    "ydiff_RES.STUDISCED8MEN",
    "ydiff_RES.STUDISCED8WOMEN",
    "ydiff_RES.STUDISCED8FOE01",
    "ydiff_RES.STUDISCED8FOE02",
    "ydiff_RES.STUDISCED8FOE03",
    "ydiff_RES.STUDISCED8FOE04",
    "ydiff_RES.STUDISCED8FOE05",
    "ydiff_RES.STUDISCED8FOE06",
    "ydiff_RES.STUDISCED8FOE07",
    "ydiff_RES.STUDISCED8FOE08",
    "ydiff_RES.STUDISCED8FOE09",
    "ydiff_RES.STUDISCED8FOE10",
    "ydiff_RES.STUDISCED8TOTAL"

]

# dataset with variables aggregated by NUTS and Year
avg_nuts = (
    filtered_df.groupby(["AGG.NUTS", "BAS.REFYEAR"])[cols]
               .sum()
               .reset_index()
)
# avg_nuts.to_csv("avg_nuts.csv",index= False, sep = ";")

# to compile interactive plots aggregated by NUTS
def plotinteractive_agg(name_df, dforig,variable, titleinput, labelinput, color_map = None ):
    plot_data = dforig.dropna(subset=[variable])
    if not pd.api.types.is_string_dtype(plot_data["BAS.REFYEAR"]):
        plot_data["BAS.REFYEAR"] = plot_data["BAS.REFYEAR"].astype(str)

    year_totals = plot_data.groupby("BAS.REFYEAR")["RES.STUDISCED8TOTAL"].transform("sum")
    plot_data["prop_RES_STUDISCED8TOTAL"] = (plot_data["RES.STUDISCED8TOTAL"] / year_totals)

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
    hover_data={
        "prop_RES_STUDISCED8TOTAL": True,
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
    size = "prop_RES_STUDISCED8TOTAL",
    color_discrete_map=color_map)

    
    # add lines manually
    for nuts, subset in plot_data.groupby("AGG.NUTS"):
        subset = subset.sort_values("BAS.REFYEAR")
        fig.add_trace(
            go.Scatter(
                x=subset["BAS.REFYEAR"],
                y=subset[variable],
                mode="lines",
                line=dict(color=color_map.get(nuts, None)),
                name=f"{nuts} trend",
                showlegend=False  # so legend doesn't duplicate
                )
            )
    
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
    
    output = fig.write_html(name_df + variable + ".html")
    
    return output


centralityindex(avg_nuts,'RES.STUDISCED8WOMEN','nuts_centrality_womenphd')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_womenphd','Centrality of Women PhD by Year. Size = Prop total students in ISCED8','Centrality of Women PhD (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8MEN','nuts_centrality_menphd')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_menphd','Centrality of Men PhD by Year. Size = Prop total students in ISCED8','Centrality of Men PhD (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE05','nuts_centrality_nat05')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_nat05','Centrality PhD Natural sciences, mathematics and statistics by Year. Size = Prop total students in ISCED8','Centrality PhD Natural sciences, mathematics and statistics (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE01','nuts_centrality_edu01')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_edu01','Centrality PhD Education by Year. Size = Prop total students in ISCED8','Centrality PhD Education (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE02','nuts_centrality_hum02')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_hum02','Centrality PhD Arts and Humanities by Year. Size = Prop total students in ISCED8','Centrality PhD Arts and Humanities (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE03','nuts_centrality_soc03')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_soc03','Centrality PhD Social Sciences, Journalism and Information by Year. Size = Prop total students in ISCED8','Centrality PhD Social Sciences, Journalism and Information (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE04','nuts_centrality_bus04')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_bus04','Centrality PhD Business, Administration and Law by Year. Size = Prop total students in ISCED8','Centrality PhD Business, Administration and Law (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE06','nuts_centrality_ict06')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_ict06','Centrality PhD Information, Communication and Technology by Year. Size = Prop total students in ISCED8','Centrality PhD Information, Communication and Technology (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE07','nuts_centrality_eng07')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_eng07','Centrality PhD Engineering, manufacturing and construction by Year. Size = Prop total students in ISCED8','Centrality PhD Engineering, manufacturing and construction (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE08','nuts_centrality_agr08')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_agr08','Centrality PhD Agriculture, forestry, fisheries and veterinary by Year. Size = Prop total students in ISCED8','Centrality PhD Agriculture, forestry, fisheries and veterinary (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE09','nuts_centrality_health09')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_health09','Centrality PhD Health and welfare by Year. Size = Prop total students in ISCED8','Centrality PhD Health and welfare (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8FOE10','nuts_centrality_ser10')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_ser10','Centrality PhD Services by Year. Size = Prop total students in ISCED8','Centrality PhD Services (GEO nuts)',color_map=nuts_colors)

centralityindex(avg_nuts,'RES.STUDISCED8TOTAL','nuts_centrality_tot')
plotinteractive_agg("nuts_", avg_nuts,'nuts_centrality_tot','Centrality Total PhD by Year. Size = Prop total PhD student','Centrality Total PhD (GEO nuts)',color_map=nuts_colors)


# plot difference newenrollment

# Plot


def plotfig(dforig, plotvariable, labeltitle,figlabel,color_map=None):
    plt.figure(figsize=(10,6))
    for nuts, subset in dforig.groupby("AGG.NUTS"):
        color = color_map.get(nuts, None) if color_map else None
        plt.plot(subset["BAS.REFYEAR"], subset[plotvariable], marker="o", label=nuts, color=color)
        
        plt.xlabel("Year")
        plt.title( "Enrollment " + labeltitle)
        plt.legend(title="AGG.NUTS", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.xticks(range(2011, 2022))
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(figlabel + ".png")
        

plotfig(avg_nuts,"ydiff_RES.STUDISCED8MEN","Year Difference Men PhD","diffenr_menphd",color_map=nuts_colors)        
plotfig(avg_nuts,"ydiff_RES.STUDISCED8WOMEN","Year Difference Women PhD","diffenr_womenphd",color_map=nuts_colors)  
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE01","Year Difference PhD Education","diffenr_edu01",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE02","Year Difference PhD Arts and Humanities","diffenr_hum02",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE03","Year Difference PhD Social Sciences, Journalism and Information","diffenr_soc03",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE04","Year Difference PhD Business, Administration and Law","diffenr_bus04",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE05","Year Difference PhD Natural sciences, mathematics and statistics","diffenr_nat05",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE06","Year Difference PhD Information, Communication and Technology","diffenr_ict06",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE07","Year Difference PhD Engineering, manufacturing and construction","diffenr_eng07",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE08","Year Difference PhD Agriculture, forestry, fisheries and veterinary","diffenr_agr08",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE09","Year Difference PhD Health and welfare","diffenr_health09",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8FOE10","Year Difference PhD Services","diffenr_ser10",color_map=nuts_colors)     
plotfig(avg_nuts,"ydiff_RES.STUDISCED8TOTAL","Year Difference Total PhD","diffenr_tot",color_map=nuts_colors)   

plotfig(avg_nuts,"RES.STUDISCED8MEN","Men PhD","enr_menphd",color_map=nuts_colors)        
plotfig(avg_nuts,"RES.STUDISCED8WOMEN","Women PhD","enr_womenphd",color_map=nuts_colors)  
plotfig(avg_nuts,"RES.STUDISCED8FOE01","PhD Education","enr_edu01",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE02","PhD Arts and Humanities","enr_hum02",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE03","PhD Social Sciences, Journalism and Information","enr_soc03",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE04","PhD Business, Administration and Law","enr_bus04",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE05","PhD Natural sciences, mathematics and statistics","enr_nat05",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE06","PhD Information, Communication and Technology","enr_ict06",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE07","PhD Engineering, manufacturing and construction","enr_eng07",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE08","PhD Agriculture, forestry, fisheries and veterinary","enr_agr08",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE09","PhD Health and welfare","enr_health09",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8FOE10","PhD Services","enr_ser10",color_map=nuts_colors)     
plotfig(avg_nuts,"RES.STUDISCED8TOTAL","Total PhD","enr_tot",color_map=nuts_colors)   

########## figures new enrollments faceted

# clean types
avg_nuts["AGG.NUTS"] = avg_nuts["AGG.NUTS"].astype(str).str.strip()
avg_nuts["BAS.REFYEAR"] = pd.to_numeric(avg_nuts["BAS.REFYEAR"], errors="coerce")

# variables and pretty titles
vars_ydiff = [f"ydiff_RES.STUDISCED8FOE{i:02d}" for i in range(1, 11)]
title_map = {
    "ydiff_RES.STUDISCED8FOE01": "01: PhD Education",
    "ydiff_RES.STUDISCED8FOE02": "02: PhD Arts & Humanities",
    "ydiff_RES.STUDISCED8FOE03": "03: PhD Social Sciences, Journalism & Info",
    "ydiff_RES.STUDISCED8FOE04": "04: PhD Business, Administration & Law",
    "ydiff_RES.STUDISCED8FOE05": "05: PhD Natural Sciences, Math & Stats",
    "ydiff_RES.STUDISCED8FOE06": "06: PhD Information & Comm. Tech",
    "ydiff_RES.STUDISCED8FOE07": "07: PhD Engineering, Manufacturing & Construction",
    "ydiff_RES.STUDISCED8FOE08": "08: PhD Agriculture, Forestry, Fisheries & Veterinary",
    "ydiff_RES.STUDISCED8FOE09": "09: PhD Health & Welfare",
    "ydiff_RES.STUDISCED8FOE10": "10: PhD Services",
}

# keep only variables that actually exist in your df
vars_ydiff = [v for v in vars_ydiff if v in avg_nuts.columns]

years = sorted(avg_nuts["BAS.REFYEAR"].dropna().unique().astype(int))
nuts_codes = sorted(avg_nuts["AGG.NUTS"].dropna().unique())

# make the grid
ncols = 2
nrows = int(numpy.ceil(len(vars_ydiff) / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(12, 18), sharex=True, squeeze=False)

for i, var in enumerate(vars_ydiff):
    ax = axes[i // ncols, i % ncols]

    # plot one line per NUTS
    for nuts in nuts_codes:
        g = (avg_nuts
             .loc[avg_nuts["AGG.NUTS"] == nuts, ["BAS.REFYEAR", var]]
             .dropna(subset=["BAS.REFYEAR", var])
             .sort_values("BAS.REFYEAR"))
        if not g.empty:
            ax.plot(g["BAS.REFYEAR"], g[var], marker="o", label=nuts,
                    color=nuts_colors.get(nuts, None))

    ax.set_title(title_map.get(var, var))
    ax.set_ylabel("Difference enrollment")          # your requested y-axis label
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)

# single legend (from first axis that has lines)
handles, labels = axes[0,0].get_legend_handles_labels()
fig.legend(handles, labels, title="AGG.NUTS", loc="upper right", ncol=len(nuts_codes), frameon=True)

plt.suptitle("Yearly Difference Enrollemt")
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("ydiff_faceted.png", dpi=300, bbox_inches="tight")
plt.show()

############## figures enrollment

# clean types
avg_nuts["AGG.NUTS"] = avg_nuts["AGG.NUTS"].astype(str).str.strip()
avg_nuts["BAS.REFYEAR"] = pd.to_numeric(avg_nuts["BAS.REFYEAR"], errors="coerce")

# variables and pretty titles
vars_ydiff = [f"RES.STUDISCED8FOE{i:02d}" for i in range(1, 11)]
title_map = {
    "RES.STUDISCED8FOE01": "01: PhD Education",
    "RES.STUDISCED8FOE02": "02: PhD Arts & Humanities",
    "RES.STUDISCED8FOE03": "03: PhD Social Sciences, Journalism & Info",
    "RES.STUDISCED8FOE04": "04: PhD Business, Administration & Law",
    "RES.STUDISCED8FOE05": "05: PhD Natural Sciences, Math & Stats",
    "RES.STUDISCED8FOE06": "06: PhD Information & Comm. Tech",
    "RES.STUDISCED8FOE07": "07: PhD Engineering, Manufacturing & Construction",
    "RES.STUDISCED8FOE08": "08: PhD Agriculture, Forestry, Fisheries & Veterinary",
    "RES.STUDISCED8FOE09": "09: PhD Health & Welfare",
    "RES.STUDISCED8FOE10": "10: PhD Services",
}

# keep only variables that actually exist in your df
vars_ydiff = [v for v in vars_ydiff if v in avg_nuts.columns]

years = sorted(avg_nuts["BAS.REFYEAR"].dropna().unique().astype(int))
nuts_codes = sorted(avg_nuts["AGG.NUTS"].dropna().unique())

# make the grid
ncols = 2
nrows = int(numpy.ceil(len(vars_ydiff) / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(12, 18), sharex=True, squeeze=False)

for i, var in enumerate(vars_ydiff):
    ax = axes[i // ncols, i % ncols]

    # plot one line per NUTS
    for nuts in nuts_codes:
        g = (avg_nuts
             .loc[avg_nuts["AGG.NUTS"] == nuts, ["BAS.REFYEAR", var]]
             .dropna(subset=["BAS.REFYEAR", var])
             .sort_values("BAS.REFYEAR"))
        if not g.empty:
            ax.plot(g["BAS.REFYEAR"], g[var], marker="o", label=nuts,
                    color=nuts_colors.get(nuts, None))

    ax.set_title(title_map.get(var, var))
    ax.set_ylabel("Affluence")          # your requested y-axis label
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)

# single legend (from first axis that has lines)
handles, labels = axes[0,0].get_legend_handles_labels()
fig.legend(handles, labels, title="AGG.NUTS", loc="upper right", ncol=len(nuts_codes), frameon=True)

plt.suptitle("Yearly Enrollment", y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("enrollment_faceted.png", dpi=300, bbox_inches="tight")
plt.show()



############## research projects

stack_cols = [
    "EUFP.PROJECTSFOE01",
    "EUFP.PROJECTSFOE02",
    "EUFP.PROJECTSFOE03",
    "EUFP.PROJECTSFOE04",
    "EUFP.PROJECTSFOE05",
    "EUFP.PROJECTSFOE06",
    "EUFP.PROJECTSFOE07",
    "EUFP.PROJECTSFOE08",
    "EUFP.PROJECTSFOE09"
]

# --- 3) Set up the faceting (one subplot per AGG.NUTS) ---
nuts_groups = sorted(avg_nuts["AGG.NUTS"].unique())
n = len(nuts_groups)
ncols = 3                     # 3 columns; adjust if you prefer a different grid
nrows = (n + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(18, 10), sharey=True)
axes = axes.flatten()

# We'll use the same x ticks everywhere for alignment
all_years = list(range(2011, 2022))

# --- 4) Make stacked bars per subplot ---
for ax, nuts in zip(axes, nuts_groups):
    subset = avg_nuts[avg_nuts["AGG.NUTS"] == nuts].copy()
    subset = subset.sort_values("BAS.REFYEAR")

    # Build a lookup so we can place values at all years 2011–2021
    # (missing years become 0 so bars align across subplots)
    year_to_row = {int(y): r for y, r in zip(subset["BAS.REFYEAR"], subset.index)}

    bottom = [0] * len(all_years)
    for col in stack_cols:
        values = []
        for y in all_years:
            if y in year_to_row:
                v = subset.loc[year_to_row[y], col]
                v = 0 if pd.isna(v) else v
            else:
                v = 0
            values.append(v)

        ax.bar(all_years, values, bottom=bottom, label=col)
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_title(f"NUTS: {nuts}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_xticks(all_years)
    ax.grid(True, axis="y", alpha=0.3)

# Remove any unused axes if grid > number of groups
for i in range(len(nuts_groups), len(axes)):
    fig.delaxes(axes[i])

# --- 5) Single shared legend on the right ---
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, bbox_to_anchor=(0.65, 0.25),
           loc="center left", title="EUFP Components")

fig.suptitle("EU-FP Projects aggregated by NUTS", fontsize=16)
plt.tight_layout(rect=[0, 0, 0.85, 0.95])
plt.savefig("euprojects.png", dpi=300, bbox_inches="tight")
plt.show()

#### for faceted centrality index (affluence) aggregated by NUTS
 
foe_cols = [
    "RES.STUDISCED8FOE01",
    "RES.STUDISCED8FOE02",
    "RES.STUDISCED8FOE03",
    "RES.STUDISCED8FOE04",
    "RES.STUDISCED8FOE05",
    "RES.STUDISCED8FOE06",
    "RES.STUDISCED8FOE07",
    "RES.STUDISCED8FOE08",
    "RES.STUDISCED8FOE09",
    "RES.STUDISCED8FOE10"
]

def centralityindex_multi(df, value_cols, year_col="BAS.REFYEAR", prefix="centr_"):
    """
    For each variable in value_cols, compute:
        row_value / sum_of_that_variable_in_same_year
    and append it as a new column.
    """
    for col in value_cols:
        if col in df.columns:
            # total for this variable per year
            year_totals = df.groupby(year_col)[col].transform("sum").replace(0, pd.NA)
            # new column name
            new_col = f"{prefix}{col}"
            # compute centrality
            df[new_col] = df[col] / year_totals
    return df

csv_nuts_centr = centralityindex_multi(avg_nuts, foe_cols, year_col="BAS.REFYEAR", prefix="centr_")
csv_nuts_centr.to_csv("avg_nuts_with_centrality.csv", index=False, sep=";")

##########

#csv_nuts_centr["BAS.REFYEAR"] = pd.to_numeric(df["BAS.REFYEAR"], errors="coerce").astype("Int64").astype(str)

# Centrality columns to facet
# Ensure clean types
csv_nuts_centr["AGG.NUTS"] = csv_nuts_centr["AGG.NUTS"].astype(str).str.strip()
csv_nuts_centr["BAS.REFYEAR"] = pd.to_numeric(csv_nuts_centr["BAS.REFYEAR"], errors="coerce")
csv_nuts_centr["centr_RES.STUDISCED8FOE03"] = pd.to_numeric(
    csv_nuts_centr["centr_RES.STUDISCED8FOE03"], errors="coerce"
)

# Drop rows where either x or y is NA and sort for nicer lines
plot_df = (csv_nuts_centr
           .dropna(subset=["BAS.REFYEAR", "centr_RES.STUDISCED8FOE03"])
           .sort_values(["AGG.NUTS", "BAS.REFYEAR"]))

plt.figure(figsize=(10, 6))
for nuts, group in plot_df.groupby("AGG.NUTS"):
    plt.plot(group["BAS.REFYEAR"].values,
             group["centr_RES.STUDISCED8FOE03"].values,
             label=nuts)

plt.xlabel("BAS.REFYEAR")
plt.ylabel("centr_RES.STUDISCED8FOE03")
plt.title("Centrality of RES.STUDISCED8FOE03 over time by AGG.NUTS")
plt.legend(title="AGG.NUTS")
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

##############################

csv_nuts_centr["AGG.NUTS"] = csv_nuts_centr["AGG.NUTS"].astype(str).str.strip()
year_totals = csv_nuts_centr.groupby("BAS.REFYEAR")["RES.STUDISCED8TOTAL"].transform("sum")
csv_nuts_centr["prop_RES_STUDISCED8TOTAL"] = csv_nuts_centr["RES.STUDISCED8TOTAL"] / year_totals
csv_nuts_centr["BAS.REFYEAR"] = pd.to_numeric(csv_nuts_centr["BAS.REFYEAR"], errors="coerce")


# Melt to long format
centrality_vars = [f"centr_RES.STUDISCED8FOE{i:02d}" for i in range(1, 11)]
df_long = csv_nuts_centr.melt(
    id_vars=["AGG.NUTS", "BAS.REFYEAR","prop_RES_STUDISCED8TOTAL" ],
    value_vars=centrality_vars,
    var_name="CentralityType",
    value_name="Value"
)
years = sorted(df_long["BAS.REFYEAR"].unique())
# Drop NA values
df_long = df_long.dropna(subset=["Value"])

# Faceted lineplot
g = sns.FacetGrid(df_long, col="CentralityType", col_wrap=2, hue="AGG.NUTS", sharey=False, aspect = 2, height = 3)
g.map(sns.lineplot, "BAS.REFYEAR", "Value").add_legend()

g.map(
    sns.scatterplot,
    "BAS.REFYEAR",
    "Value",
    "prop_RES_STUDISCED8TOTAL",   # size variable
    alpha=0.7
)

plt.subplots_adjust(top=0.9)
g.fig.suptitle("Centrality Trends by AGG.NUTS and FOE")
plt.xticks(years)
plt.savefig("AGGcentfac.png", dpi=300, bbox_inches="tight")
plt.show()

###############

title_map = {
    "centr_RES.STUDISCED8FOE01": "01: PhD Education",
    "centr_RES.STUDISCED8FOE02": "02: PhD Arts and Humanities",
    "centr_RES.STUDISCED8FOE03": "03: PhD Social Sciences, Journalism and Information",
    "centr_RES.STUDISCED8FOE04": "04: PhD Business, Administration and Law",
    "centr_RES.STUDISCED8FOE05": "05: PhD Natural sciences, Mathematics and Statistics",
    "centr_RES.STUDISCED8FOE06": "06: PhD Information, Communication and Technology",
    "centr_RES.STUDISCED8FOE07": "07: PhD Engineering, Manufacturing and Construction",
    "centr_RES.STUDISCED8FOE08": "08: PhD Agriculture, Forestry, Fisheries and Veterinary",
    "centr_RES.STUDISCED8FOE09": "09: PhD Health and Welfare",
    "centr_RES.STUDISCED8FOE10": "10: PhD Services",
}


# Long format as before
centrality_vars = [f"centr_RES.STUDISCED8FOE{i:02d}" for i in range(1, 11)]
df_long = csv_nuts_centr.melt(
    id_vars=["AGG.NUTS", "BAS.REFYEAR", "prop_RES_STUDISCED8TOTAL"],
    value_vars=centrality_vars,
    var_name="CentralityType",
    value_name="Value"
).dropna(subset=["Value"])

years = sorted(df_long["BAS.REFYEAR"].unique())

# Facet grid
g = sns.FacetGrid(
    df_long,
    col="CentralityType",
    col_wrap=2,
    hue="AGG.NUTS",
    sharey=False,
    height=3.5,
    aspect=1.5
)

for ax in g.axes.flatten():
    facet_var = ax.get_title().split(" = ")[-1]   # current facet name (e.g. "centr_RES.STUDISCED8FOE01")
    if facet_var in title_map:
        ax.set_title(title_map[facet_var])

# Plot lines
g.map(sns.lineplot, "BAS.REFYEAR", "Value")

# Overlay points with size ∝ prop_RES_STUDISCED8TOTAL
g.map_dataframe(
    sns.scatterplot,
    x="BAS.REFYEAR",
    y="Value",
    size="prop_RES_STUDISCED8TOTAL",
    sizes=(20, 200),   # min/max bubble size in points^2
    legend=False,      # suppress size legend
    alpha=0.7)

# Add legend for color and size
g.add_legend()
g.set_ylabels("Affluence (Centrality index)")

plt.subplots_adjust(top=0.92)
g.fig.suptitle("Affluence PhD enrollments per area; Size = yearly relative size total PhD students (RES_STUDSCED8TOTAL)")
plt.xticks(years)
plt.savefig("AGGcentfacsize.png", dpi=300, bbox_inches="tight")
plt.show()
