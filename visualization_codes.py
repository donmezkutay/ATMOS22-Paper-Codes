import matplotlib.pyplot as plt
import proplot

from data import *
from utils import *


def population_line_plot(dt, province, method):
    
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
        
        # check the method
        if method == 'lineplot':
            y = province_dt.iloc[:, 1:].transpose().values/1e6 # pretty visual
            ylabel = 'Population (Mn)'
            
        elif method == 'ratio':
            y = province_dt.iloc[:, 1:].transpose().values
            ylabel = 'Ratio to Whole Population (%)'
            
        #return x,y
        axs[i].plot(x, y,
                    lw=3,
                    linestyle='dashed',
                    color=color_match[province])

        # lineplot formatting
        axs[i].format(ylabel=ylabel,
                      xlabel='Year',
                      ygridminor=True,
                      ygrid=True,
                      title=province,
                      titleloc='lr',
                      xrotation=45,
                     )
        
    # savefig    
    plt.savefig(fr'pictures/population_{method}_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=300)
    
    
def corine_yearly_pdf_change_plot(dt, method, indexes, years, provinces):
    # start figure
    f, axs = proplot.subplots(array=[[1, 1],
                                     [2, 2],
                                     [3, 3]],
                                  hratios=(1, 1, 1),
                                  hspace=0.20,
                                  figsize=(4,6),
                                  share=3,
                                  axwidth=1.5,
                                  tight=False)

    # format whole figure
    axs.format(xlabel='xlabel',
                   ylabel='ylabel',
                   suptitle='Land Use Change (1990-2018)',
                   abcloc='ul',
                   abc=True,)

    # legend colorlist
    color_list = ['#c65238',
              '#ffdc00',
              '#009500',
              '#017c64', 
              '#012477']
    
    for i, province in enumerate(provinces):
        
        df = pd.DataFrame(dt[i], 
                 index = list(indexes.keys())[:5],
                 columns = years)
        
        # get transpose of data
        df_tpose = df.transpose().copy(deep=True)
        
        # find total grid of each year
        df_tpose['total'] = df_tpose.sum(axis=1)
        
        # find percentage of each land use relative to total
        for col in df_tpose.columns[:5]:

            df_tpose[fr'perc_{col}'] = df_tpose.apply(
                lambda row: find_percentage(row, col, 'total'), axis=1
            )

        # drop unnecessary columns
        columns_to_drop = list(indexes.keys())[:5] + ['total']
        df_tpose.drop(columns = columns_to_drop, inplace=True)

        # set index as str
        df_tpose.index = df_tpose.index.astype(str)

        # create barplot
        obj = axs[i].bar(
            df_tpose, cycle=color_list, edgecolor='red9', #colorbar='t', colorbar_kw={'frameon': True}
        )
        
        ylabel = 'Percentage of Total (%)'
        xlabel = 'Years'
        axs[i].format(xlocator=1,
                      ytickminor=True,
                      title=province,
                      ylabel=ylabel,
                      titleloc='ur',
                      xlabel = xlabel)
        
    legend_labels = ['Urban', 'Agriculture', 'Forest', 'Wetland', 'Water']
    f.legend(obj, ncols=3, label='Land Use', frame=False, loc='b', space=0.5,
             labels=legend_labels)
    
    # savefig    
    plt.savefig(fr'pictures/corine_{method}_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=300)