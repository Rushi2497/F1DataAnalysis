from matplotlib import rcParams
from fastf1 import plotting

def setup_plot(cs='fastf1', xyticksize=16, axeslabel=18, figtitle=24, legendfont=16, legendtitle=18, grid=True):
    """
    Sets up Matplotlib rcParams with preferred styles
    and applies FastF1 color scheme.
    """
    # FastF1 default color scheme
    plotting.setup_mpl(color_scheme=cs)

    # Font sizes
    rcParams['xtick.labelsize'] = xyticksize
    rcParams['ytick.labelsize'] = xyticksize
    rcParams['axes.labelsize'] = axeslabel
    rcParams['axes.titlesize'] = figtitle
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