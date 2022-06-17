import cartopy
import matplotlib.pyplot as plt
import proplot
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader

from .data import *
from .utils import *


def line_plot(dt, method, suptitle):
    
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
    axs.format(
               suptitle=suptitle,
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
        if method == 'dmsp_lineplot':
            y = province_dt.iloc[:, 1:].transpose().values
            ylabel = 'Percentage of Total (%)'
        
        elif method == 'population_lineplot':
            y = province_dt.iloc[:, 1:].transpose().values/1e6 # pretty visual
            ylabel = 'Population (Mn)'
        
        elif method == 'ratio':
            y = province_dt.iloc[:, 1:].transpose().values
            ylabel = 'Percentage of Total (%)'
            
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
    plt.savefig(fr'../pictures/{method}_fig.jpeg',
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
    plt.savefig(fr'../pictures/corine_{method}_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=300)
    
    
def dmsp_difference_last_first_plot(data_df, method, fig_array, graphic_no,
                                    proj, suptitle, cmap, vmin, vmax,
                                    norm, ticks):

    # Create Figure -------------------------
    fig, axs = proplot.subplots(fig_array, 
                              aspect=4, axwidth=2, proj=proj,
                              hratios=tuple(np.ones(len(fig_array), dtype=int)),
                              includepanels=True, hspace=-0.10, wspace=0.1)

    # format whole figure
    axs.format(
               suptitle=suptitle,
               abcloc='ul',
               abc=True,)
    
    # format lon and lat limits
    axs[0].format(lonlim=(27.7, 30), latlim=(40.5, 41.9), # istanbul
                  labels=False, longrid=False, latgrid = False)
    axs[1].format(lonlim=(26, 28.7), latlim=(37.8, 39.5), # izmir
                  labels=False, longrid=False, latgrid = False) 
    axs[2].format(lonlim=(30.8, 33.9), latlim=(38.5, 40.8), # ankara
                  labels=False, longrid=False, latgrid = False)


    # add shapefiles
    turkey_district_shape = r'data/shapefiles/istanbul_ankara_izmir_shapefile.shp'
    shape_district_turkey = ShapelyFeature(Reader(turkey_district_shape).geometries(),
                                                 cartopy.crs.PlateCarree(), facecolor='none',
                                                 edgecolor = 'black', linewidth = 0.1, zorder = 0.3)

    turkey_province_shape = r'data/shapefiles/Iller_HGK_6360_Kanun_Sonrasi.shp'
    shape_province_turkey = ShapelyFeature(Reader(turkey_province_shape).geometries(),
                                                 cartopy.crs.PlateCarree(), facecolor='none',
                                                 edgecolor = 'black', linewidth = 0.5, zorder = 0.4)

    for i in range(graphic_no):
        axs[i].add_feature(shape_district_turkey)
        axs[i].add_feature(shape_province_turkey)   

    # graphic code
    for i, province in enumerate(['istanbul', 'izmir', 'ankara']):
        
        # plot
        mesh = axs[i].pcolormesh(data_df[province]['x'], data_df[province]['y'],
                                 data_df[province], cmap = cmap,
                                 vmin = vmin, vmax = vmax, norm=norm,
                                 zorder = 0.2)
        
        # Text
        axs[i].set_title(fr'{province}',
                          fontsize = 8, loc = 'left',
                          pad = -14, y = 0.01,
                          x=0.020, weight = 'bold',)


    # cbar ----------------------
    cbar = axs[2].colorbar(mesh, ticks=ticks, loc='r',
                        drawedges = False, shrink=0.7,
                        space = -0.8, aspect = 50, )
    cbar.ax.tick_params(labelsize=7,)
    cbar.set_ticks([])
    cbar.ax.get_children()[4].set_color('black')
    cbar.solids.set_linewidth(1)
    cbar.set_ticks(ticks)
    cbar.ax.set_yticklabels([
                             'decrease',
                             'no change',
                             'increase',
                             ])

    # savefig    
    plt.savefig(fr'../pictures/{method}_fig.jpeg',
                bbox_inches='tight', optimize=False, 
                progressive=True, dpi=300)