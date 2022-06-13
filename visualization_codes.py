import matplotlib.pyplot as plt
import proplot

from data import *
from utils import *


def population_line_plot(dt, province):
    
    # start figure
    f, axs = proplot.subplots(array=[[1, 1],
                                     [2, 2],
                                     [3, 3]],
                              hratios=(1, 1, 1),
                              hspace=0.20,
                              figsize=(6,4),
                              share=3,
                              axwidth=1.5,
                              tight=False)
    
    # format whole figure
    axs.format(xlabel='xlabel',
               ylabel='ylabel',
               suptitle='Population Change',
               abcloc='ul',
               abc=True,)
    
    # lineplot
    color_match = {
        'istanbul': 'purple',
        'ankara': 'orange',
        'izmir': 'darkgreen'
    }
    
    for i, province in enumerate(color_match.keys()):
            
        # x and y from dataset
        province_dt = dt.query(f'Province == "{province}"')\
                        .reset_index(drop=True)
        
        # omit Province column
        x = province_dt.columns[1:].values.astype(str)
        y = province_dt.iloc[:, 1:].transpose().values/1e6 # pretty visual
        #return x,y
        axs[i].plot(x, y,
                    lw=3,
                    linestyle='dashed',
                    color=color_match[province])

        # lineplot formatting
        axs[i].format(ylabel='Population (Mn)',
                      xlabel='Year',
                      ygridminor=True,
                      ygrid=True,
                      title=province,
                      titleloc='lr',
                      xrotation=45,
                     )
        
    # savefig    
    plt.savefig(fr'Pictures/population_lineplot_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=300)