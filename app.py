import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import html, Dash, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_split_pane
import base64
import io
import datetime
from datetime import datetime
from pandas.tseries.offsets import BDay
import plotly.graph_objects as go
from plotly.subplots import make_subplots


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)

columnNames = ["Blood Lactate", "Velocity (km/h)", "Stage Finish Time"]
resultsDF = pd.DataFrame(columns=columnNames)
resultsDF.rename_axis("Stage", inplace=True, axis=0)
columnIds = ["bloodLactate", "velocity", "stageFinishTime"]

# ------------------------------------------------------------------------

input_types = ['number', 'number', 'text']

row1 = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P("Blood Lactate:", style={"margin-left":20}),
                    dcc.Input(
                            id="bloodLactateId",
                            type="number",
                            placeholder="insert Blood Lactate",
                            minLength=0, maxLength=50,          
                            autoComplete='on',
                            disabled=False,                    
                            readOnly=False,                               
                            required=False,                     
                            size=20,   
                            style={"margin-right":20}
                            )
                        ], style=
                         {
                            "display":"flex", 
                            "justify-content":"space-between", 
                            "align-items":"baseline", 
                            "margin-top":20
                            }
            )
                ])
            
        ])

    ] 
                    )

row2 = html.Div(
    [
        dbc.Row([
            dbc.Col([
    html.Div([
        html.P("Velocity (km/h):", style={"margin-left":20}),
        dcc.Input(
            id="velocityId",
            type="number",
            placeholder="insert Velocity",
            minLength=0, maxLength=50,          
            autoComplete='on',
            disabled=False,                     
            readOnly=False,                     
            required=False,                     
            size="20",   
            style={"margin-right":20}
        )
    ], style={
        "display":"flex", 
        "justify-content":"space-between", 
        "align-items":"baseline"})
]),
            
        ])

    ]
                    )

row3 = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P("Stage Finish Time (MM:SS):", 
                           style={"margin-left":20}),
                    dcc.Input(
            id="stageFinishTimeId",
            type="text",
            placeholder="insert (MM:SS)",
            minLength=0, maxLength=50,          
            autoComplete='on',
            disabled=False,                     
            readOnly=False,                    
            required=False,                     
            size="20",
            style={"margin-right":20}
        ) 
    ], style={"display":"flex", 
              "justify-content":"space-between", 
              "align-items":"baseline"})
                ]),
            
        ])

    ]
                    )

row4 = html.Div(
        dbc.Row(
            html.Button('Add Row', 
                        id='add_row',n_clicks=0), 
            style={"text-align":"center"}
         )
        
    )

row5 = html.Div([
        dcc.Upload(
            id="upload-data", children=html.Div([
                'Drag and Drop COSMED file or ', html.A('Select Files')
                ] ),
            style={
                'width':'80%', 
                "lineHeight":"60px", 
                'borderWidth':'1px', 
                'borderStyle':'dashed', 
                'borderRadius':'5px', 
                'text-align':'center', 
                'margin-left':'auto',
                'margin-right':'auto',
                'margin-top':40,
                }
            ) 

], style={"align-content":'center'})


table = html.Div(children=[
dbc.Row([    
        dbc.Col([html.H5('Results',
                         className='text-center', 
                         style={"margin-left":20}),
        dash_table.DataTable(
                id='table-container_3',
                data=[],
                columns=[{"name":i_3,"id":i_3,'type':'numeric'} for i_3 in resultsDF.columns],
                style_table={'overflow':'scroll','height':600},
                style_cell={'textAlign':'center'},
                row_deletable=True,
                editable=True),


                ],width={'size':12,"offset":0,'order':1})
            ]), html.Div(id='output-plot')
 ])





pane1 = html.Div([
    row1,
    html.Br(),
    row2,
    html.Br(),
    row3,
    html.Br(),
    row4,
    html.Br(),
    row5
    ])

pane2 = html.Div(
    table,
    )



app.layout = dash_split_pane.DashSplitPane(
    children=[pane1, pane2],
    id="splitter",
    split="vertical",
    size=500
    )





@app.callback(
Output('table-container_3', 'data'),
Output('bloodLactateId', 'value'),
Output('velocityId', 'value'),
Output('stageFinishTimeId', 'value'),
Input('add_row', 'n_clicks'),
State('table-container_3', 'data'),
State('table-container_3', 'columns'),
State('bloodLactateId', 'value'),
State('velocityId', 'value'),
State('stageFinishTimeId', 'value'))

def add_row(n_clicks, rows, columns, selectedBloodLactate, selectedVelocity,
            selectedStageFinishTime):

    if n_clicks > 0:
        rows.append({c['id']: r for c,r in zip(columns, 
                                               [selectedBloodLactate, 
                                                selectedVelocity, 
                                                selectedStageFinishTime])})
        newDf = pd.DataFrame(rows)
        newDf.index.name = 'Stage'
        newDf.reset_index(inplace=True)
        print(newDf.head())

    return rows, '', '', ''



def parse_contents_plot(HR_df, filename, GUI_df):
    content_type, content_string = HR_df.split(',')

    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            COSMEDdf = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            COSMEDdf = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    athlete_stats_df = cleanTableFunc(COSMEDdf, GUI_df)
    

    return html.Div([
        dcc.Graph(figure=figFunc('HR', 'Blood Lactate')),
        dcc.Graph(figure=figFunc('HR', 'Velocity (km/h)')),
        dcc.Graph(figure=figFunc('HR', 'VO2/Kg')),
        dcc.Graph(figure=figFunc('Blood Lactate', 'Velocity (km/h)')),
        dcc.Graph(figure=figFunc('VO2/Kg', 'Blood Lactate'))
        
    ])




        
@app.callback(Output('splitter', 'children'), # change splitter to output-plot and it will work
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('table-container_3', 'data'))
def update_plot(HR_df, filename, GUI_df):
    if filename is not None:
        global pane1
        children = [pane1, [parse_contents_plot(HR_df, filename, GUI_df)]]
        
        return children

    
def col(title): #function for grabbing columns from athlete_stats_df
    return athlete_stats_df[title]

def figFunc(col1, col2): # function for making figures
    figname = str(f"{col1} vs {col2} Fig")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=col('Stage Finish Time'), y=col(f"{col1}"), name=f'{col1}', line_shape='spline'),
        secondary_y=False,
        )

    fig.add_trace(
        go.Scatter(x=col('Stage Finish Time'), y=col(f'{col2}'), name=f'{col2}', line_shape='spline'),
        secondary_y=True
        )

    # Add figure title
    fig.update_layout(
        title_text=figname
    )

    # Set y-axes titles
    fig.update_yaxes(title_text=f"{col1}", secondary_y=False)
    fig.update_yaxes(title_text=f"{col2}", secondary_y=True)
    
    return fig

    








def cleanTableFunc(HR_df, GUI_df): # function for making athlete_stats_df
    GUI_df = pd.DataFrame(GUI_df)
    GUI_df.index.name = 'Stage'
    GUI_df.reset_index(inplace=True)
    
    print(GUI_df)
    HR_df_clean = HR_df.drop([0, 1])
    HR_df_clean = HR_df_clean.reset_index(
        drop=True)  # the index numbers 1 and 2 get removed when I run the above line. I want to keep them,
    # otherwise it interferes with my ability to merge this dataframe with the other dataframe with the GUI data
    # later
    cols = np.r_[0:9, 25:30, 41:45, 46, 49:58, 64, 65, 70, 75:107, 109:117, 119, 121,
            125:128]  # these are all the columns with useless data in HR_df that I want to remove
    global HR_df_cleaner
    HR_df_cleaner = HR_df_clean.drop(HR_df_clean.columns[cols], axis=1)

    global stage_column
    stage_list = ['Stage', '', '']
    stage_column = pd.DataFrame(stage_list)
    global GUI_stage_rows
    GUI_stage_rows = []
    GUI_velocity_rows = []
    global GUI_blood_lactate_rows
    GUI_blood_lactate_rows = []

    global x
    x = 0
    global stage_change_index
    stage_change_index = []
    for i in range(len(HR_df_cleaner)):
        if datetime.strptime(HR_df_cleaner.iloc[i][0], "%H:%M:%S") < datetime.strptime(
                GUI_df.iloc[len(GUI_df) - 1][3],
                "%M:%S"):  # discards all values taken after test was finished
            if x + 1 <= len(GUI_df):
                if datetime.strptime(HR_df_cleaner.iloc[i][0], "%H:%M:%S") <= datetime.strptime(GUI_df.iloc[x][3],
                                                                                                "%M:%S"):
                    GUI_stage_rows.append(GUI_df.iloc[x][0])
                    GUI_velocity_rows.append(GUI_df.iloc[x][2])
                    GUI_blood_lactate_rows.append(GUI_df.iloc[x][1])
                else:
                    x += 1
                    stage_change_index.append(i)
                    GUI_stage_rows.append(GUI_df.iloc[x][0])
                    GUI_velocity_rows.append(GUI_df.iloc[x][2])
                    GUI_blood_lactate_rows.append(GUI_df.iloc[x][1])

    stage_df = pd.DataFrame({'Stage': GUI_stage_rows})
    velocity_df = pd.DataFrame({GUI_df.columns[2]: GUI_velocity_rows})

    blood_lactate_df = pd.DataFrame({'Blood Lactate': GUI_blood_lactate_rows})
    
    # make new dataframe with all of the data merged
    global New_clean_df
    New_clean_df = pd.concat([HR_df_cleaner, stage_df, velocity_df, blood_lactate_df], axis=1)

    global grouped
    New_clean_df['HR'] = pd.to_numeric(New_clean_df['HR'])
    New_clean_df['VO2/Kg'] = pd.to_numeric(New_clean_df['VO2/Kg'])

    grouped = New_clean_df.groupby('Stage', as_index=False).apply(lambda x: x.tail(
        int(0.33 * len(x))))  # group dataframe by stage, then remove everything except the last third of the values
    grouped = grouped.groupby('Stage').mean(numeric_only=True)  # find the mean of all the numeric values

    global athlete_stats_df
    athlete_stats_df = grouped.iloc[:, 0:2].join(GUI_df.iloc[:,
                                                    0:4])  # combine columns from 2 dataframes to create 1 dataframe
                                                        # with useful info for the report
    athlete_stats_df = athlete_stats_df.iloc[:,
                        [2, 4, 1, 0, 3, 5]]  # change the order of the columns to make it easier to understand
    
    print(athlete_stats_df)
    
    return athlete_stats_df






    
if __name__ == '__main__':
    app.run_server(debug=False)
