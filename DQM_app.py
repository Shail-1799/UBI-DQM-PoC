import base64
import datetime
import io
import sys
import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd



new_layout = dbc.Container([
    dbc.Row([
       
           dbc.Col([
            dbc.Card([
            dbc.CardBody(
                [
                    html.H1('UsefulBI DQM PoC'),
                ])#, style={'textAlign':'center'}),
            #className='mt-10',
            #style={'box-shadow':'2px 2px 10px grey', 'height':'120px'}
            ],  style={'textAlign':'center','box-shadow':'2px 2px 10px grey', 'height':'75px',  'background-color': '#ADD8E6'})
       
        ], width=12),
            
     ],className='mb-4 mt-2'),
    
         
    ###  ------------------------------------------- ROW 2 ---------------------------------------------------------    
    
    dbc.Row([dcc.Upload(
            id='upload-data',
            children=html.Div([
                 'Drag & Drop or ',
                html.A('Select a CSV/Excel File to be uploaded')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
               # 'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        )],className='mb-4 mt-2'),
    
    
    ###  ------------------------------------------- ROW 3 --------------------------------------------------------- 
    
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
               # dbc.CardHeader(Lottie(options=options, width="60%", height="60%", url=url_connections)),
                dbc.CardBody([
                    html.H6('Total Columns'),
                    html.H2(id='#columns', children="000")
                ], style={'textAlign':'center'})
            ], style={'box-shadow':'2px 2px 10px grey', 'background-color': '#ADD8E6'}),
        ]),
        
        dbc.Col([
            dbc.Card([
                #dbc.CardHeader(Lottie(options=options, width="60%", height="100%", url=url_companies)),
                dbc.CardBody([
                    html.H6('Total Records'),
                    html.H2(id='#records', children="000")
                ], style={'textAlign':'center'})
            ], style={'box-shadow':'2px 2px 10px grey', 'background-color': '#ADD8E6'}),
        ]),
        
        dbc.Col([
            dbc.Card([
               # dbc.CardHeader(Lottie(options=options, width="60%", height="80%", url=url_msg_in)),
                dbc.CardBody([
                    html.H6('Null Check Passed'),
                    html.H2(id='nullcheck', children="000")
                ], style={'textAlign':'center'})
            ], style={'box-shadow':'2px 2px 10px grey', 'background-color': '#ADD8E6'}),
        ]),
        
        dbc.Col([
            dbc.Card([
                #dbc.CardHeader(Lottie(options=options, width="60%", height="60%", url=url_msg_out)),
                dbc.CardBody([
                    html.H6('Unique Check Passed'),
                    html.H2(id='uniquecheck', children="000")
                ], style={'textAlign': 'center'})
            ], style={'box-shadow':'2px 2px 10px grey', 'background-color': '#ADD8E6'}),
        ]),
        
        
      
    ],className='mb-4'), 
    
    
    ###  ------------------------------------------- ROW 4 --------------------------------------------------------- 
      
    html.Div(id='output-data-upload')
       

    
  ], fluid=True)



# Layout

external_stylesheets =  [dbc.themes.LUX]  #['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
"graphBackground": "#F5F5F5",
"background": "#ffffff",
"text": "#000000"
}


app.layout = new_layout


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

#########################################################

def get_kpi(df_to_process):
    """
    Calculates KPI for the given DataFrame.

    Parameters:
        df_to_process (pandas.DataFrame): The DataFrame containing the data to be processed.

    Returns:
        dict: A dictionary containing the calculated metrics. The keys represent the metric names,
              and the values represent the corresponding metric values.
    """
    
    main_json = {'Column KPI': [],
                'Overall KPI': {}}

    try:

        for i, col in enumerate(df_to_process.columns):

            kpi_json = {}
            
            kpi_json['Sr No.'] = i+1

            kpi_json['Column Name'] = col
            
            kpi_json['Data Type'] = str(df_to_process[col].dtype)


            kpi_json['Total Records'] = df_to_process.shape[0]

            null_count_for_col = df_to_process[col].isnull().sum()

            kpi_json['Null Values'] = null_count_for_col
            
            kpi_json['Null Check'] = 'Fail' if null_count_for_col else "Pass"

            unique_value_count_for_col = df_to_process[col].nunique()

            kpi_json['Unique Values'] = unique_value_count_for_col

            kpi_json['Unique Check'] = 'Pass' if unique_value_count_for_col == df_to_process.shape[0] else 'Fail'

            main_json['Column KPI'].append(kpi_json)

        column_kpi_df = pd.DataFrame(main_json['Column KPI'])

        null_test_pass_count = (column_kpi_df['Null Check'] == 'Pass').sum()
        null_test_fail_count = (column_kpi_df['Null Check'] == 'Fail').sum()

        unique_test_pass_count = (column_kpi_df['Unique Check'] == 'Pass').sum()
        unique_test_fail_count = (column_kpi_df['Unique Check'] == 'Fail').sum()

        over_all_kpi_dict = {
        'Total Columns' : len(df_to_process.columns),
        'Total Rows':df_to_process.shape[0],
        'Null Test Pass' : null_test_pass_count,
        'Null Test Fail': null_test_fail_count,
        'Unique Test Pass' :unique_test_pass_count,
        'Unique Test Fail': unique_test_fail_count        
        }
    

        main_json['Overall KPI'] = over_all_kpi_dict

    except Exception as e:

        line_number = sys.exc_info()[-1].tb_lineno
        error_message = str(e)
    
        print(f"Error while creating KPI from Dataset {line_number}: {error_message}")



    return main_json, column_kpi_df


#############################################################


@app.callback(
            [
                Output('output-data-upload', 'children'),
                Output('#columns', 'children'),
                Output('#records', 'children'),
                Output('nullcheck', 'children'),
                Output('uniquecheck', 'children')
            ],
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()
    cols, rows, nulls, uniques = 0,0,0,0

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        
        
        # ---- Reading the output df -----
        
        op, output_df = get_kpi(df)
        
        # ---------------------------------
        
        
        ## Output DataTable
        
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=output_df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in output_df.columns],
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'black', 'fontWeight': 'bold', 'color':'white'}
            ),
            
            html.Hr(),

        ])
        
        ## KPI Scorecards
        
        cols = op['Overall KPI']['Total Columns']
        rows = op['Overall KPI']['Total Rows']
        nulls = op['Overall KPI']['Null Test Pass']
        uniques = op['Overall KPI']['Unique Test Pass']
        
        

    return table, cols, rows, nulls, uniques


if __name__ == '__main__':
    app.run_server(debug=False)