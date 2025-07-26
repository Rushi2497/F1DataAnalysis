from matplotlib import rcParams
from fastf1 import plotting

def setup_plot():
    """
    Sets up Matplotlib rcParams with preferred styles
    and applies FastF1 color scheme.
    """
    # FastF1 default color scheme
    plotting.setup_mpl(color_scheme='fastf1')

    # Font sizes
    rcParams['xtick.labelsize'] = 14
    rcParams['ytick.labelsize'] = 14
    rcParams['axes.labelsize'] = 16
    rcParams['axes.titlesize'] = 24
    rcParams['legend.fontsize'] = 14
    rcParams['legend.title_fontsize'] = 16

    # Legend styling
    rcParams['legend.facecolor'] = '#000000'
    rcParams['legend.edgecolor'] = 'white'

    # Grid styling
    rcParams['grid.color'] = '#333333'

    # Optional: set grid visibility by default
    rcParams['axes.grid'] = True

    # Auto layout to mimic tight_layout()
    rcParams['figure.autolayout'] = True    

    # Set animation size limit
    rcParams['animation.embed_limit'] = 200

    # Enable ffmpeg
    rcParams['animation.ffmpeg_path'] = r"C:\Users\rushi\AppData\Local\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

    print("Matplotlib rcParams initialized with custom style.")