from shiny import App, render, ui
import numpy as np
import pandas as pd
import plotly.express as px

# Create a simple app
app_ui = ui.page_fluid(
    ui.h2("Test d'application Shiny"),
    ui.input_slider("n", "Nombre de points", 0, 100, 20),
    ui.output_plot("plot"),
)


def server(input, output, session):
    @output
    @render.plot
    def plot():
        # Generate random data
        x = np.random.normal(0, 1, input.n())
        y = np.random.normal(0, 1, input.n())

        # Create a scatter plot
        df = pd.DataFrame({"x": x, "y": y})
        fig = px.scatter(df, x="x", y="y", title="Nuage de points aléatoires")
        return fig


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
