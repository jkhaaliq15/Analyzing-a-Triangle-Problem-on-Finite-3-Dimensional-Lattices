# Look into making the dots smaller especially for larger dimensions

import itertools
import random 
import numpy as np 
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output, State 
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H2("3D Lattice Triangle Generator"),

    html.H4("Grid Dimension"),

    dcc.Input(id="nx", type="number", value=3, placeholder="nx"),
    dcc.Input(id="ny", type="number", value=3, placeholder="ny"),
    dcc.Input(id="nz", type="number", value=3, placeholder="nz"),

    html.Br(),

    html.H4("Spacing"),

    dcc.Input(id="dx", type="number", value=1, placeholder="dx"),
    dcc.Input(id="dy", type="number", value=1, placeholder="dy"),
    dcc.Input(id="dz", type="number", value=1, placeholder="dz"),

    html.Br(), html.Br(),

    html.Button("Generate Triangle", id="generate", n_clicks=0),

    html.Br(), html.Br(),

    dcc.Checklist(
        id="manual_mode",
        options=[{"label": "Use manual triangle coordinates", "value": "manual"}],
        value = []
    ),

    html.H4("Manual Triangle Coordinates"),

    html.Div([
        html.Label("A"),
        dcc.Input(id="ax", type="number", placeholder="Ax"),
        dcc.Input(id="ay", type="number", placeholder="Ay"),
        dcc.Input(id="az", type="number", placeholder="Az"),
    ]),

    html.Div([
        html.Label("B"),
        dcc.Input(id="bx", type="number", placeholder="Bx"),
        dcc.Input(id="by", type="number", placeholder="By"),
        dcc.Input(id="bz", type="number", placeholder="Bz"),
    ]),

    html.Div([
        html.Label("C"),
        dcc.Input(id="cx", type="number", placeholder="Cx"),
        dcc.Input(id="cy", type="number", placeholder="Cy"),
        dcc.Input(id="cz", type="number", placeholder="Cz"),
    ]),

    html.Br(),


    html.Div(id="triangle-info"),

    dcc.Graph(id="lattice-plot")
])

@app.callback(
    [Output("lattice-plot", "figure"),
     Output("triangle-info", "children")],

    Input("generate", "n_clicks"),

    State("nx", "value"),
    State("ny", "value"),
    State("nz", "value"),

    State("dx", "value"),
    State("dy", "value"),
    State("dz", "value"),

    State("manual_mode", "value"),

    State("ax", "value"), State("ay", "value"), State("az", "value"),
    State("bx", "value"), State("by", "value"), State("bz", "value"),
    State("cx", "value"), State("cy", "value"), State("cz", "value"),
)

def update_triangle(n_clicks, nx, ny, nz, dx, dy, dz,
                    manual_mode,
                    ax, ay, az, bx, by, bz, cx, cy, cz):

    if None in [nx, ny, nz, dx, dy, dz]:
        return go.Figure(), "Enter grid values."

    # Generate lattice
    points = [(i*dx, j*dy, k*dz)
              for i,j,k in itertools.product(range(nx), range(ny), range(nz))]
    
    warnings = []

    use_manual = "manual" in manual_mode

    if use_manual:

        coords = [ax, ay, az, bx, by, bz, cx, cy, cz]

        if None in coords:
            return go.Figure(), "Enter all triangle coordinates."
        
        A = np.array([ax,ay,az])
        B = np.array([bx,by,bz])
        C = np.array([cx,cy,cz])

        mode = "Manual"
    else:
        if len(points) < 3:
            return go.Figure(), "Grid must contain at least 3 points."
        
        A, B, C = map(np.array, random.sample(points, 3))

        mode = "Random"

    # Calculate Side Lengths and Area
    AB = np.linalg.norm(B-A)
    BC = np.linalg.norm(C-B)
    CA = np.linalg.norm(A-C)

    area = 0.5 * np.linalg.norm(np.cross(B-A, C-A))

    tol = 1e-6

    a, b, c = sorted([AB, BC, CA])

    # Determine Type of Triangle or if Non-triangle
    if area < tol:
        triangle_type = "Degenerate (collinear)"
    else:
        if abs(c**2 - (a**2 + b**2)) < tol:
            triangle_type = "Right"
        elif c**2 > a**2 + b**2:
            triangle_type = "Obtuse"
        else:
            triangle_type = "Acute"

    # User Warnings
    if np.array_equal(A,B) or np.array_equal(A,C) or np.array_equal(B,C):
        warnings.append("Two vertices are identical")

    if tuple(A) not in points:
        warnings.append("Point A is outside lattice")

    if tuple(B) not in points:
        warnings.append("Point B is outside lattice")

    if tuple(C) not in points:
        warnings.append("Point C is outside lattice")


    fig = go.Figure()

    # Lattice points
    fig.add_trace(go.Scatter3d(
        x=[p[0] for p in points], 
        y=[p[1] for p in points],
        z=[p[2] for p in points],
        mode='markers',
        marker=dict(size=4),
        name="Lattice"
    ))

    tri = np.vstack([A, B, C, A])

    # Triangle
    fig.add_trace(go.Scatter3d(
        x=tri[:,0],
        y=tri[:,1],
        z=tri[:,2],
        mode='lines+markers',
        line=dict(width=6),
        marker=dict(size=7),
        name="Triangle"
    ))

    fig.update_layout(scene=dict(aspectmode="data"))

    info = html.Div([
        html.P(f"Mode: {mode}"),
        html.P(f"Side Lengths: AB={AB:.3f}, BC={BC:.3f}, CA={CA:.3f}"),
        html.P(f"Area: {area:.6f}"),
        html.P(f"Triangle Type: {triangle_type}"),

        html.H4("Warnings"),
        html.Ul([html.Li(w) for w in warnings]) if warnings else html.P("None")
    ])

    return fig, info 

if __name__=="__main__":
    app.run(debug=True)