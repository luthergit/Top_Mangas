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
top_manga_copy = top_manga.copy()

# Replace unknown english titles with the synomims and Japanese

top_manga_copy['English Title'].loc[(
    top_manga_copy['English Title'] == 'Unknown')] = top_manga_copy['Synonims Titles'].copy().str[:25]

top_manga_copy['English Title'].loc[(
    top_manga_copy['English Title'] == 'Unknown')] = top_manga_copy['Japanese Title'].copy()

top_manga_copy['Genres'] = top_manga_copy['Genres'].copy().str.replace(
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

#create dataframe with the count of the most ranked genres, this will be used to get the speific genres for the
# dropdown and the graphs
ranked = top_manga_copy.copy()
ranked.sort_values(by = ['Ranked'], ascending = True, inplace = True)

top_genres_for_rank = {}

for genres in ranked['Genres']:
    for genre in genres:
        if genre in top_genres_for_rank:
            top_genres_for_rank[genre] += 1
        else:
            top_genres_for_rank[genre] = 1

top_genres_for_rank_df = pd.DataFrame.from_dict(
    top_genres_for_rank, orient='index', columns=['count'])

top_genres_for_rank_df.reset_index(inplace = True)
top_genres_for_rank_df.rename(columns={"index": "Genres"},inplace = True)



#Store the published start and end date
Published_Start_Date = []
Published_End_Date = []

# for loop to get the start and end date
for index, row in top_manga_copy.iterrows():
    Published_Start_Date.append(row['Published Dates'][10:20])
    Published_End_Date.append(row['Published Dates'][30:-2])

top_manga_copy['Published_Start_Date'] = Published_Start_Date
top_manga_copy['Published_End_Date'] = Published_End_Date    

# replace "Unknown', " with nan
top_manga_copy['Published_Start_Date'] = top_manga_copy['Published_Start_Date'].copy().replace("Unknown', ",np.nan)

top_manga_copy['Published_Start_Date'] = pd.to_datetime(top_manga_copy['Published_Start_Date'], errors = 'coerce',
                                                       )
top_manga_copy['Published_End_Date'] = top_manga_copy['Published_End_Date'].replace(["Unknown",'','nown'], np.nan)

top_manga_copy['Published_End_Date'] = pd.to_datetime(top_manga_copy['Published_End_Date'], errors = 'coerce',)

# Get the author names with a for loop and store the author names in a list 
authors = []
    
for index, row in top_manga_copy.iterrows():
    authors.append(row['Author'][2:-2])

top_manga_copy['Author'] = authors    

#Get the column names
features_y = top_manga_copy.copy().drop(
    columns = ['Synonims Titles','Status','Serialization','Ranked',
               'Ranked','Published_Start_Date','Published_End_Date',
               'Published Dates','Published','Manga URL',
               'Author']).columns.sort_values(ascending = True)
features_x = top_manga_copy.copy().drop(
    columns = ['Chapters','Favorites','Genres','Manga ID', 'Manga URL',
              'Published','Published Dates', 'Manga URL','Manga ID',
               'Score Voted By']).columns.sort_values(ascending = True)


#Get the genres
genres = top_genres_for_rank_df['Genres'].copy().sort_values(ascending = True).unique()

#Get the authors
authors = top_manga_copy['Author'].copy().sort_values(ascending = True).unique()

#Get the types
types = top_manga_copy['Type'].copy().sort_values(ascending = True).unique()

#Get the status
status = top_manga_copy['Status'].copy().sort_values(ascending = True).unique()

USERNAME_PASSWORD_PAIRS = [
['TopManga', 'Berserk'],['LnD', 'fallenwanderer']
]

app = dash.Dash()
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

app.layout = html.Div([
             html.H1('Manga Analysis Dashboard'),
             html.Div([
                 html.H3('Select X axis column:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'x-axis', 
                              options = [{'label': i, 'value': i} for i in features_x],
                              value = 'Type'),
             ], style = {'width': '15%', 'display': 'inline-block', 'verticalAlign':'top'}), #allows the dropdown to be next to each other
             html.Div([
                 html.H3('Select Y axis column:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'y-axis', 
                              options = [{'label': i, 'value': i} for i in features_y],
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
                html.H3('Select Specific Genre(s) OR Statement:', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'genre-picker', 
                              options = [{'label': i, 'value': i} for i in genres],
                              value = genres,
                              multi = True,
                              ),
                              
             ], style = {'width': '30%', 'display': 'none', 'verticalAlign':'top'}), #allows the dropdown to be next to each other

             html.Div([
                 html.H3('Select Specific  Genre(s):', style={'paddingRight':'30px'}),
                 dcc.Dropdown(id = 'genre-picker-AND', 
                              options = [{'label': i, 'value': i} for i in genres],
                              value = ['Drama'],
                              multi = True
                             ),
                              
             ], style = {'width': '30%', 'display': 'inline', 'verticalAlign':'top'}), #allows the dropdown to be next to each other

            
            dcc.Graph(id='feature-graphic',
                      style = {'width': '50%', 'display': 'inline-block'}),

            dcc.Graph(id='top-rank-genres',
                      style = {'width': '50%', 'display': 'inline-block'}),
             
             dcc.Graph(id='feature-grahic-AND',
                      style = {'width': '50%', 'display': 'inline-block'}),

             dcc.Graph(id='top-popular-genres',
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


    #Allows to select the all the dates from the two time points on the silder including nan values
    df = top_manga_copy.copy()
    date = ((df['Published_Start_Date'] >= start_date) | (df['Published_Start_Date'].isna())) & ((
    df['Published_End_Date'] <= end_date) | (
    df['Published_End_Date'].isna()))

        
    #To select and include all the data for the dates, type and status
    
    filtered_type = df.copy().loc[date]
    filtered_type = filtered_type.copy()[filtered_type["Type"].copy().isin(type_picker)]
    filtered_type = filtered_type.copy()[filtered_type['Status'].copy().isin(status_picker)]

    selected_genres = []
    for x in genre_picker:
        for y in filtered_type['Genres']:

            if x in y:
                selected_genres.append(y)
        
    #Filter by genres, this is an OR statement i.e. it will select Action or Comedy, it is not an AND statement    
    filtered_type = filtered_type[(filtered_type['Genres'].copy().isin(selected_genres))]

    traces = []

    
    for types_unique in filtered_type["Type"].unique():
        df_by_type = filtered_type.copy()[filtered_type["Type"] == types_unique]
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
        "data": traces,
        "layout": go.Layout(
            title="All Genres",
            xaxis={"title": xaxis_name, 'categoryorder':'sum descending'}, #it sorts from descending
            yaxis={"title": yaxis_name},
            barmode="stack",
            hovermode = 'closest'
        ),
    }

# AND Statements
@app.callback(Output(component_id = 'feature-grahic-AND', component_property = 'figure'),
             [Input(component_id = 'x-axis', component_property = 'value')],
             [Input(component_id = 'y-axis', component_property = 'value')],
             [Input(component_id = 'type-picker', component_property = 'value')],
             [Input(component_id = 'year-picker', component_property = 'start_date')],
             [Input(component_id = 'year-picker', component_property = 'end_date')],
             [Input(component_id = 'genre-picker-AND', component_property = 'value')],
             [Input(component_id = 'status-picker', component_property = 'value')])

def update_figure(xaxis_name, yaxis_name,type_picker,start_date, end_date,genre_picker_AND,status_picker):


    #Allows to select the all the dates from the two time points on the silder including nan values
    df = top_manga_copy.copy()
    date = ((df['Published_Start_Date'] >= start_date) | (df['Published_Start_Date'].isna())) & ((
    df['Published_End_Date'] <= end_date) | (
    df['Published_End_Date'].isna()))

        
    #To select and include all the data for the dates, type and status
    
    filtered_type = df.copy().loc[date]
    filtered_type = filtered_type.copy()[filtered_type["Type"].copy().isin(type_picker)]
    
    filtered_type = filtered_type.copy()[filtered_type['Status'].copy().isin(status_picker)]
    
    selected_genres = []
    for genres in filtered_type['Genres']:


# To check that test has genres elements, effectively, this is an AND statement i.e. it will find genres that
# have the specific selected genres.
        check =  all(item in genres for item in genre_picker_AND)

        if check is True:
            selected_genres.append(genres)
        #print("The list {} contains all elements of the list {}".format(genre_picker, genres))
            filtered_test = filtered_type.copy()[filtered_type['Genres'].isin(selected_genres)]
        else:
            filtered_test = filtered_type.copy()[filtered_type['Genres'].isin(selected_genres)]  


    traces = []

    # Sorting the platform by alphabetical order
    
    for types_unique in filtered_test["Type"].unique():
        df_by_type = filtered_test[filtered_test["Type"] == types_unique]
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
        "data": traces,
        "layout": go.Layout(
            title="Specific Genres",
            xaxis={"title": xaxis_name,'categoryorder':'sum descending' }, #it sorts from descending
            yaxis={"title": yaxis_name},
            barmode="stack",
            hovermode = 'closest'
        ),
    }


@app.callback(Output(component_id = 'top-rank-genres', component_property = 'figure'),            
             [Input(component_id = 'genre-picker', component_property = 'value')],
             [Input(component_id = 'type-picker', component_property = 'value')],
             [Input(component_id = 'year-picker', component_property = 'start_date')],
             [Input(component_id = 'year-picker', component_property = 'end_date')],
             [Input(component_id = 'status-picker', component_property = 'value')])
             #[Input(component_id = 'status-picker', component_property = 'value')])

def update_figure_genre(genre_picker, type_picker, start_date, end_date, status_picker):


    #Allows to select the all the dates from the two time points on the silder including nan values
    df = top_manga_copy.copy()
    date = ((df['Published_Start_Date'] >= start_date) | (df['Published_Start_Date'].isna())) & ((
    df['Published_End_Date'] <= end_date) | (
    df['Published_End_Date'].isna()))

        
    #To select and include all the data for the dates, type and status
    
    filtered_type = df.copy().loc[date]
    filtered_type = filtered_type.copy()[filtered_type["Type"].copy().isin(type_picker)]
    filtered_type = filtered_type.copy()[filtered_type['Status'].copy().isin(status_picker)]

    selected_genres = []
    for x in genre_picker:
        for y in filtered_type['Genres']:
#     print(test in i)
            if x in y:
                selected_genres.append(y)
        
        
    filtered_type = filtered_type[(filtered_type['Genres'].copy().isin(selected_genres))]


    #create dataframe with the count of the most ranked genres
    ranked_genre = filtered_type.copy()
    ranked_genre.sort_values(by = ['Ranked'], ascending = True, inplace = True)

    top_rank_genre = {}

    for genres in ranked_genre['Genres']:
        for genre in genres:
            if genre in top_rank_genre:
                top_rank_genre[genre] += 1
            else:
                top_rank_genre[genre] = 1

    top_rank_genre_df = pd.DataFrame.from_dict(
    top_rank_genre, orient='index', columns=['count'])

    top_rank_genre_df.reset_index(inplace = True)
    top_rank_genre_df.rename(columns={"index": "Genres"},inplace = True)

    
    df_ranked = top_rank_genre_df
    
    traces = []

    # Sorting the platform by alphabetical order
    
    for genres_unique in df_ranked["Genres"].sort_values(ascending = False):
        df_by_genre = df_ranked[df_ranked["Genres"] == genres_unique]
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
            title="Top Ranked Genres",
            xaxis={"title": 'Genre', 'categoryorder':'sum descending'}, #it sorts from descending
            yaxis={"title": 'Count'},
            barmode="stack",
            hovermode = 'closest'
        ),
    }

@app.callback(Output(component_id = 'top-popular-genres', component_property = 'figure'),            
             [Input(component_id = 'genre-picker', component_property = 'value')],
             [Input(component_id = 'type-picker', component_property = 'value')],
             [Input(component_id = 'year-picker', component_property = 'start_date')],
             [Input(component_id = 'year-picker', component_property = 'end_date')],
             [Input(component_id = 'status-picker', component_property = 'value')])
             #[Input(component_id = 'status-picker', component_property = 'value')])

def update_figure_genre(genre_picker, type_picker, start_date, end_date, status_picker):

    #Allows to select the all the dates from the two time points on the silder including nan values
    df = top_manga_copy.copy()
    date = ((df['Published_Start_Date'] >= start_date) | (df['Published_Start_Date'].isna())) & ((
    df['Published_End_Date'] <= end_date) | (
    df['Published_End_Date'].isna()))

        
    #To select and include all the data for the dates, type and status
    
    filtered_type = df.copy().loc[date]
    filtered_type = filtered_type.copy()[filtered_type["Type"].copy().isin(type_picker)]
    filtered_type = filtered_type.copy()[filtered_type['Status'].copy().isin(status_picker)]

    selected_genres = []
    for x in genre_picker:
        for y in filtered_type['Genres']:
#     print(test in i)
            if x in y:
                selected_genres.append(y)
        
        
    filtered_type = filtered_type[(filtered_type['Genres'].copy().isin(selected_genres))]


    #create dataframe with the count of the most popular genres
    popular_genre = filtered_type.copy()
    popular_genre.sort_values(by = ['Popularity'], ascending = True, inplace = True)

    top_popular_genre = {}

    for genres in popular_genre['Genres']:
        for genre in genres:
            if genre in top_popular_genre:
                top_popular_genre[genre] += 1
            else:
                top_popular_genre[genre] = 1

    top_popular_genre_df = pd.DataFrame.from_dict(
    top_popular_genre, orient='index', columns=['count'])

    top_popular_genre_df.reset_index(inplace = True)
    top_popular_genre_df.rename(columns={"index": "Genres"},inplace = True)
    
    df_popular = top_popular_genre_df
    
    traces = []

    # Sorting the platform by alphabetical order
    
    for genres_unique in df_popular["Genres"].sort_values(ascending = False):
        df_by_genre = df_popular[df_popular["Genres"] == genres_unique]
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
            title="Top Popular Genres",
            xaxis={"title": 'Genre', 'categoryorder':'sum descending'}, #it sorts from descending
            yaxis={"title": 'Count'},
            barmode="stack",
            hovermode = 'closest'
        ),
    }

if __name__ == "__main__":
    app.run_server(port = '8051', debug = True)
