import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import rcParams
from fastf1 import plotting
import os

def setup_plot(cs='fastf1', xyticksize=18, axeslabel=20, figtitle=24, legendfont=18, legendtitle=20, grid=True):
    """
    Configure Matplotlib's global plotting parameters for consistent styling.

    This function sets up Matplotlib `rcParams` with a preferred style,
    font sizes, legend appearance, grid styling, and animation settings.
    By default, it also applies the FastF1 color scheme for F1 data visualization.

    Parameters
    ----------
    cs : str, optional
        Color scheme to apply using `fastf1.plotting.setup_mpl` 
        (default is 'fastf1').
    xyticksize : int, optional
        Font size for x-axis and y-axis tick labels (default is 18).
    axeslabel : int, optional
        Font size for axis labels (default is 20).
    figtitle : int, optional
        Font size for figure titles (default is 24).
    legendfont : int, optional
        Font size for legend labels (default is 18).
    legendtitle : int, optional
        Font size for legend titles (default is 20).
    grid : bool, optional
        Whether to display a grid by default (default is True).

    Notes
    -----
    - Sets `axes.labelweight` and `axes.titleweight` to bold.
    - Configures legend background (`black`) and border (`white`).
    - Uses a dark grid color (`#333333`) if enabled.
    - Enables `figure.autolayout` to avoid overlapping elements.
    - Sets an `ffmpeg` path for animations (user-specific).
    - Increases `animation.embed_limit` to allow larger embedded animations.

    Prints
    ------
    Confirmation message once parameters are initialized.
    """
    # FastF1 default color scheme
    plotting.setup_mpl(color_scheme=cs)

    # Font sizes
    rcParams['xtick.labelsize'] = xyticksize
    rcParams['ytick.labelsize'] = xyticksize
    rcParams['axes.labelsize'] = axeslabel
    rcParams['axes.labelweight'] = 'bold'
    rcParams['axes.titlesize'] = figtitle
    rcParams['axes.titleweight'] = 'bold'
    rcParams['legend.fontsize'] = legendfont
    rcParams['legend.title_fontsize'] = legendtitle

    # Legend styling
    rcParams['legend.facecolor'] = '#000000'
    rcParams['legend.edgecolor'] = 'white'

    # Grid styling
    rcParams['grid.color'] = '#333333'

    # Optional: set grid visibility by default
    rcParams['axes.grid'] = grid

    # Auto layout to mimic tight_layout()
    rcParams['figure.autolayout'] = True    

    # Set animation size limit
    rcParams['animation.embed_limit'] = 200

    # Enable ffmpeg
    rcParams['animation.ffmpeg_path'] = r"C:\Users\rushi\AppData\Local\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

    print("Matplotlib rcParams initialized with custom style.")


def save_fig(fig, name, loc, dpi=300):
    """
    Save a matplotlib figure as a PNG file in a specified directory.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The matplotlib figure object to save.
    name : str
        The filename (without extension) to save the figure as.
    loc : str
        Subdirectory inside ./media/ where the figure will be stored.
        If the directory does not exist, it will be created automatically.
    dpi : int, optional
        Resolution of the saved figure in dots per inch (default is 300).

    Notes
    -----
    - The figure will be saved as a .png file.
    - If a file with the same name exists, it will be overwritten.
    """
    # Build full directory and path
    dir_path = f"./media/{loc}"
    full_path = f"{dir_path}/{name}.png"
    
    # Create directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    
    try:
        fig.savefig(full_path, dpi=dpi, bbox_inches='tight')
        print(f"Figure saved at {full_path}")
    except Exception as e:
        print(f"Error saving figure: {e}")
    return

def plot_track_dominance(points, segments, colors, figsize=(12, 10), linewidth=16):
    """
    Plot track dominance visualization from computed points, segments, and colors.

    Parameters
    ----------
    points : np.ndarray
        Array of (x, y) coordinates reshaped for LineCollection plotting.
    segments : np.ndarray
        Array of line segments for LineCollection.
    colors : np.ndarray
        Array of colors corresponding to which driver is fastest at each point.
    figsize : tuple, optional
        Figure size in inches (default: (12, 10)).
    linewidth : int or float, optional
        Line width for the track segments (default: 16).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.set_facecolor("#000000")
    ax.axis("off")

    # Match segments length (N-1) with colors
    lc = LineCollection(segments, colors=colors[:-1], linewidth=linewidth)

    ax.add_collection(lc)
    ax.autoscale()

    plt.tight_layout()
    plt.show()

    return fig