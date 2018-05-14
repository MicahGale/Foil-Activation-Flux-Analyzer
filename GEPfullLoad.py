
from foilDataParser import *

data=foilExper('fullLoad.xlsx')

PLOT_AXIAL=0x01
PLOT_RADIAL=0x02
REGRESS_AXIAL=0xb0

mode=REGRESS_AXIAL | PLOT_AXIAL

if(PLOT_RADIAL & mode==PLOT_RADIAL):
    fig=plt.gcf()
    fig.set_size_inches(16,9)
    rad=fig.add_subplot(111)
    ax5=fig.add_subplot(2,1,1)
    ax1=fig.add_subplot(2,1,2)

    # Turn off axis lines and ticks of the big subplot
    rad.spines['top'].set_color('none')
    rad.spines['bottom'].set_color('none')
    rad.spines['left'].set_color('none')
    rad.spines['right'].set_color('none')
    rad.tick_params(labelcolor='w', top=False, bottom=False, left=False,right=False)


    font={'size':20}
    data.plotRadial(5,ax5,None,font,False,False,False,'Layer 5')
    rad.set_ylabel("Uncorrected Specific Reaction Rate\n($\\eta\\phi\\Sigma_c/\\rho$)[$s^{-1    }g^{-1}]$", **font)
    data.plotRadial(1,ax1,'radial',font,True,True,False,'Layer 1')

if(REGRESS_AXIAL & mode==REGRESS_AXIAL):
    pile=subCritPile('fullLoad.xlsx',230.5,231.1,294.7)
    

if(PLOT_AXIAL & mode==PLOT_AXIAL):
    fig=plt.gcf()
    fig.clf()
    fig.set_size_inches(16,9)
    ax=fig.add_subplot(111)
    axLog=fig.add_subplot(2,1,1)
    axLin=fig.add_subplot(2,1,2)


    # Turn off axis lines and ticks of the big subplot
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top=False, bottom=False,
              left=False,right=False)
    font={'size':20}

    data.plotAxial(7,axLog,None,font,False,False,False,True)
    pile.plotAxialFunc(7,axLin)

    ax.set_ylabel("Uncorrected Specific Reaction Rate\n($\\eta\\phi\\Sigma_c/\\rho$)[$s^{-1    }g^{-1}]    $",**font)
    pile.plotAxialFunc(7,axLog,False)
    data.plotAxial(7,axLin,'axialRegress',font,save=True,yAxisLabel=False,
        xAxisLabel=True,logLog=False)


if(REGRESS_AXIAL & mode==REGRESS_AXIAL):
    pile=subCritPile('fullLoad.xlsx',230.5,231.1,294.7)
   # fig=plt.gcf()
   # ax=fig.add_subplot(111)
    pile.plotAxialFunc(7,axLin)
