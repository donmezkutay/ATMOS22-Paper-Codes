import cartopy
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import proplot
import seaborn as sns
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader

from .data import *
from .utils import *


def line_plot(dt, method, fig_array, suptitle):
    
    # start figure
    f, axs = proplot.subplots(array=fig_array,
                              hratios=tuple(np.ones(len(fig_array), dtype=int)),
                              hspace=0.20,
                              figsize=(6,3),
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
        #'izmir': 'darkgreen'
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
        
        elif method == 'population_ratio':
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
    plt.savefig(fr'pictures/{method}_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=300)
    
    
def corine_yearly_pdf_change_plot(dt, method, fig_array, indexes, years, provinces):
    # start figure
    f, axs = proplot.subplots(array=fig_array,
                                  hratios=tuple(np.ones(len(fig_array), dtype=int)),
                                  hspace=0.20,
                                  figsize=(6,4),
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
        
        axs[i].set_ylim([0, 60])
        
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
    axs[1].format(lonlim=(27.5, 30.2), latlim=(40.3, 42), # istanbul
                  labels=False, longrid=False, latgrid = False)
    #axs[1].format(lonlim=(26, 28.7), latlim=(37.8, 39.5), # izmir
    #              labels=False, longrid=False, latgrid = False) 
    axs[0].format(lonlim=(30.8, 33.9), latlim=(38.5, 40.8), # ankara
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
    for i, province in enumerate(['ankara', 'istanbul']):
        
        # plot
        mesh = axs[i].pcolormesh(data_df[province]['x'], data_df[province]['y'],
                                 data_df[province], cmap = cmap,
                                 vmin = vmin, vmax = vmax, norm=norm,
                                 zorder = 0.2)
        
        # Text
        axs[i].set_title(fr'{province}',
                          fontsize = 8, loc = 'right',
                          pad = -14, y = 0.88,
                          x=0.970, weight = 'bold',)


    # cbar ----------------------
    cbar = axs[1].colorbar(mesh, ticks=ticks, loc='b',
                        drawedges = False, shrink=0.7,
                        space = -0.1, aspect = 50, )
    cbar.ax.tick_params(labelsize=7,)
    cbar.set_ticks([])
    cbar.ax.get_children()[4].set_color('black')
    cbar.solids.set_linewidth(1)
    cbar.set_ticks(ticks)
    cbar.ax.set_xticklabels([
                             'decrease',
                             'no change',
                             'increase',
                             ])

    # savefig    
    plt.savefig(fr'pictures/{method}_fig.jpeg',
                bbox_inches='tight', optimize=False, 
                progressive=True, dpi=300)
    
    
def plot_station_mean_difference(dt, mean_types, luses, method, province):
    """
    Plot mean difference between urban and nourban
    """
    
    # create fig and axes
    fig, axes = plt.subplots(1, 3,
                             figsize=(15, 5),
                             sharey=True,
                             constrained_layout=True)
    
    # calculate mean difference between urban and nourban
    for m_type in range(3):
        
        diff_luse = dt[luses[0]][mean_types[m_type]] - dt[luses[1]][mean_types[m_type]]

        # make a dataframe
        diff_luse_df = diff_luse.to_frame(name = '')
        diff_luse_df = diff_luse_df.reset_index().rename(columns = {'Date':mean_types[m_type],
                                                                    'Season':mean_types[m_type]})

        # plot
        sns.set_theme(style="whitegrid")
        colors = ['#56a868', 'salmon', '#65b5ce']
        sns.barplot(ax=axes[m_type], x = mean_types[m_type], y = '',
                    data = diff_luse_df, color=colors[m_type],
                    saturation=.5, linewidth=1, edgecolor="k",
                    dodge=False)
        axes[m_type].set_box_aspect(10/len(axes[m_type].patches)) #change 10 to modify the y/x axis ratio
        
    
    # savefig    
    plt.savefig(fr'pictures/{method}_{mean_types[m_type]}_{province}_fig.jpeg',
                bbox_inches='tight', optimize=False, 
                progressive=True, dpi=300)
    
def station_time_mean_lineplot(monthly_mean_df,
                               seasonal_mean_df,
                               yearly_mean_df,
                               method, 
                               styles,
                               colors,
                               ):

    # start figure
    f, axs = proplot.subplots(array=[[1, 1, 2, 2],
                                     [1, 1, 2, 2],
                                     [3, 3, 3, 3], 
                                     [3, 3, 3, 3]], 
                              hratios=(1,), sharex=False, sharey=True,
                              hspace=3.55, figsize=(9,6), axwidth=1.5, tight=True)
    
    # format whole figure
    axs.format(abcloc='ul', abc=True,)

    # path effect feature
    path_effect = [pe.Stroke(linewidth=3, foreground='#403f3f'),
                    pe.Normal()]

    # plot lines
    lp1 = axs[0].plot(monthly_mean_df, cycle=colors, lw=3,
                      path_effects=path_effect)
    lp2 = axs[1].plot(seasonal_mean_df, cycle=colors, lw=3,
                      path_effects=path_effect)
    lp3 = axs[2].plot(yearly_mean_df, cycle=colors, lw=3,
                      path_effects=path_effect)

    # linestyle
    for i in range(3):
        for j, l in enumerate(axs[i].lines):
            plt.setp(l, ls=styles[j])

    # ax legend
    axs[1].legend(loc='lr', ncols=2, facecolor='white')

    # axis formats
    axs[0].format(ylabel='Temperature (°C)', xlabel='Months',
                      ygridminor=False, ygrid=True, 
                      titleloc='ll', xrotation=0,
                      xlocator=proplot.arange(1, 13, 1), 
                      xtickminor=False, ytickminor=False)

    axs[1].format(xlabel='Seasons',
                      ygridminor=False, ygrid=True, 
                      titleloc='ll', xrotation=0,
                      xtickminor=False, ytickminor=False)

    axs[2].format(ylabel='Temperature (°C)', xlabel='Years',
                      ygridminor=False,
                      titleloc='ll', xrotation=0,
                      xlocator=proplot.arange(2011, 2019, 1),
                      xlim=(2011,2018),
                      xtickminor=False)

    # savefig    
    plt.savefig(fr'pictures/{method}_time_mean_fig.jpeg',
                bbox_inches='tight', optimize=False,
                progressive=True, dpi=1000)