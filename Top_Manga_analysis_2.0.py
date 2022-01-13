import dash
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
import datetime
import dash_auth
from datetime import datetime
from dash.dependencies import Input, Output

top_manga = pd.read_csv('top500mangaMAL.csv')
top_manga_copy = top_manga

# Replace unknown english titles with the synomims and Japanese

top_manga_copy['English Title'].loc[(
    top_manga_copy['English Title'] == 'Unknown')] = top_manga_copy['Synonims Titles'].str[:25]

top_manga_copy['English Title'].loc[(
    top_manga_copy['English Title'] == 'Unknown')] = top_manga_copy['Japanese Title']

top_manga_copy['Genres'] = top_manga_copy['Genres'].str.replace(
    '[', '').str.replace(']', '').str.replace("'", '').str.replace(' ', '').str.split(',')


top_manga_copy['Genres']
unique_genres_dict = []
for unique_genres in top_manga_copy['Genres']:
#     print(unique_genres)
    unique_genres = list(set(unique_genres))
    unique_genres_dict.append(unique_genres)


# Drop and replace the Genres column with just unique values
top_manga_copy.drop(columns = 'Genres',inplace = True)
top_manga_copy['Genres'] = unique_genres_dict


top_genres_for_rank = {}

for genres in top_manga_copy['Genres']:
    for genre in genres:
        if genre in top_genres_for_rank:
            top_genres_for_rank[genre] += 1
        else:
            top_genres_for_rank[genre] = 1

top_genres_for_rank_df = pd.DataFrame.from_dict(
    top_genres_for_rank, orient='index', columns=['count'])

top_genres_for_rank_df.reset_index(inplace = True)
top_genres_for_rank_df.rename(columns={"index": "Genres"},inplace = True)

Published_Start_Date = []
Published_End_Date = []


for index, row in top_manga_copy.iterrows():
    Published_Start_Date.append(row['Published Dates'][10:20])
    Published_End_Date.append(row['Published Dates'][30:-2])

top_manga_copy['Published_Start_Date'] = Published_Start_Date
top_manga_copy['Published_End_Date'] = Published_End_Date    

# replace "Unknown', " with nan
top_manga_copy['Published_Start_Date'] = top_manga_copy['Published_Start_Date'].replace("Unknown', ",np.nan)

top_manga_copy['Published_Start_Date'] = pd.to_datetime(top_manga_copy['Published_Start_Date'], errors = 'coerce',
                                                       )
top_manga_copy['Published_End_Date'] = top_manga_copy['Published_End_Date'].replace(["Unknown",'','nown'], np.nan)

top_manga_copy['Published_End_Date'] = pd.to_datetime(top_manga_copy['Published_End_Date'], errors = 'coerce',
                                                       )
authors = []
    
for index, row in top_manga_copy.iterrows():
    authors.append(row['Author'][2:-2])

top_manga_copy['Author'] = authors    

features = top_manga_copy.columns.sort_values(ascending = True)

genres = top_genres_for_rank_df['Genres'].sort_values(ascending = True).unique()

authors = top_manga_copy['Author'].sort_values(ascending = True).unique()

types = top_manga_copy['Type'].sort_values(ascending = True).unique()

status = top_manga_copy['Status'].sort_values(ascending = True).unique()

app = dash.Dash()


app.layout = html.Div([
             html.H1('Manga Analysis Dashboard'),
             html.Div([
                 html.H3('Select X axis column:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'x-axis', 
                              options = [{'label': i, 'value': i} for i in features],
                              value = 'Type'),
             ], style = {'width': '15%', 'display': 'inline-block', 'verticalAlign':'top'}), #allows the dropdown to be next to each other
             html.Div([
                 html.H3('Select Y axis column:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'y-axis', 
                              options = [{'label': i, 'value': i} for i in features],
                              value = 'Members'), 
                              
             ], style = {'width': '15%', 'display': 'inline-block', 'verticalAlign':'top'}), #allows the dropdown to be next to each other

             html.Div([
                 html.H3('Select Date Range:', style={'paddingRight':'30px'}),
                 dcc.DatePickerRange(
                                    id='year-picker',
                                    min_date_allowed=top_manga_copy['Published_Start_Date'].min(),
                                    max_date_allowed=top_manga_copy['Published_End_Date'].max(),
                                    #step=1,
                                    start_date = top_manga_copy['Published_Start_Date'].min(),
                                    end_date = top_manga_copy['Published_End_Date'].max(),
                                    display_format = 'D-M-Y'
                                    #tooltip={"placement": "bottom", "always_visible": True},
                                    #updatemode = 'drag',
                                    # value=[top_manga_copy['Published_Start_Date'].min(), top_manga_copy['Published_End_Date'].max()]
    ),
            # multi=True,
            ], style = {'display': 'inline-block'}),
             html.Div([
                 html.H3('Select Type:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'type-picker', 
                              options = [{'label': i, 'value': i} for i in types],
                              value = types,
                              multi = True),
                              
             ], style = {'width': '20%', 'display': 'inline-block', 'verticalAlign':'top'}), #allows the dropdown to be next to each other

            html.Div([
                 html.H3('Select Status:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'status-picker', 
                              options = [{'label': i, 'value': i} for i in status],
                              value = status,
                              multi = True
                              ),
                              
             ], style = {'width': '20%', 'display': 'inline-block', 'verticalAlign':'top'}), #allows the dropdown to be next t
             
            
            html.Div([
                 html.H3('Select Genre(s):', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'genre-picker', 
                              options = [{'label': i, 'value': i} for i in genres],
                              value = genres,
                              multi = True
                              ),
                              
             ], style = {'width': '30%', 'display': 'inline', 'verticalAlign':'top'}), #allows the dropdown to be next to each other 

            
            dcc.Graph(id='feature-graphic',
                      style = {'width': '50%', 'display': 'inline-block'}),

            dcc.Graph(id='genre-graphic',
                      style = {'width': '50%', 'display': 'inline-block'}),
             
], style = {'padding': 10})


@app.callback(Output(component_id = 'feature-graphic', component_property = 'figure'),
             [Input(component_id = 'x-axis', component_property = 'value')],
             [Input(component_id = 'y-axis', component_property = 'value')],
             [Input(component_id = 'type-picker', component_property = 'value')],
             [Input(component_id = 'year-picker', component_property = 'start_date')],
             [Input(component_id = 'year-picker', component_property = 'end_date')],
             [Input(component_id = 'genre-picker', component_property = 'value')],
             [Input(component_id = 'status-picker', component_property = 'value')])

def update_figure(xaxis_name, yaxis_name,type_picker,start_date, end_date,genre_picker,status_picker):


    #Allows to select the all the years from the two time points on the silder, included '+1' to include the next year i.e. 2020 is 2019.
    df = top_manga_copy
    date = ((df['Published_Start_Date'] >= start_date) | (df['Published_Start_Date'].isna())) & ((
    df['Published_End_Date'] <= end_date) | (
    df['Published_End_Date'].isna()))

        
    #To select and include all the data for the years stored in value
    
    filtered_type = df.copy().loc[date]
    filtered_type = filtered_type[filtered_type["Type"].copy().isin(type_picker)]
    filtered_type = filtered_type[filtered_type['Status'].copy().isin(status_picker)]

    selected_genres = []
    for x in genre_picker:
        for y in filtered_type['Genres']:
#     print(test in i)
            if x in y:
                selected_genres.append(y)
        
        
    filtered_type = filtered_type[(filtered_type['Genres'].copy().isin(selected_genres))]

    #filtered_type = filtered_type[filtered_type["Genres"].copy().isin(genre_picker)]
    
    
    
    # filtered_platform = filtered_platform.dropna(subset = [yaxis_name])

    traces = []

    # Sorting the platform by alphabetical order
    
    for types_unique in filtered_type["Type"].unique():
        df_by_type = filtered_type[filtered_type["Type"] == types_unique]
        traces.append(
            go.Bar(
                x=df_by_type[xaxis_name],
                y=df_by_type[yaxis_name],
                # mode = 'markers',
                # opacity = 0.7,
                #hovertext=np.round(df_by_type[yaxis_name].sum(),2),
                #text = np.round(df_by_platform['NA_Sales'].sum(),2),
                # marker = {'size': 15},
                name=types_unique,
                #textposition='auto',
            )
        )

    return {
        "data": traces[:25],
        "layout": go.Layout(
            # title="Top Manga+ Dashboard",
            xaxis={"title": xaxis_name, 'categoryorder':'sum descending'}, #it sorts from descending
            yaxis={"title": yaxis_name},
            barmode="stack",
            hovermode = 'closest'
        ),
    }

@app.callback(Output(component_id = 'genre-graphic', component_property = 'figure'),            
             [Input(component_id = 'genre-picker', component_property = 'value')])
             #[Input(component_id = 'status-picker', component_property = 'value')])

def update_figure_genre(genre_picker):


    #Allows to select the all the years from the two time points on the silder, included '+1' to include the next year i.e. 2020 is 2019.
    df = top_genres_for_rank_df

    df = df[df["Genres"].copy().isin(genre_picker)]
    
    
    
    # filtered_platform = filtered_platform.dropna(subset = [yaxis_name])

    traces = []

    # Sorting the platform by alphabetical order
    
    for genres_unique in df["Genres"].sort_values(ascending = False):
        df_by_genre = df[df["Genres"] == genres_unique]
        traces.append(
            go.Bar(
                x=df_by_genre['Genres'],
                y=df_by_genre['count'],
                # mode = 'markers',
                # opacity = 0.7,
                #hovertext=np.round(df_by_type[yaxis_name].sum(),2),
                #text = np.round(df_by_platform['NA_Sales'].sum(),2),
                # marker = {'size': 15},
                name=genres_unique,
                #textposition='auto',
            )
        )

    return {
        "data": traces,
        "layout": go.Layout(
            title="Top Genres",
            xaxis={"title": 'Genre', 'categoryorder':'sum descending'}, #it sorts from descending
            yaxis={"title": 'Count'},
            barmode="stack",
            hovermode = 'closest'
        ),
    }

if __name__ == "__main__":
    app.run_server(port = '8051', debug = True)