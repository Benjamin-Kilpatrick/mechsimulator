class PlotterFormat:
    def __init__(self):
        self.plot_points:bool = True
        self.xunit = None
        self.yunit = None
        self.ylimit = [0.0, 0.0055] # TODO! where did this come from
        self.xlimit = None
        self.omit_targs = None
        self.exp_on_top = True
        self.rows = 4
        self.cols = 3
        self.marker_size = 15
        self.group_by = 'cond'
        self.exp_color = 'black'
        self.xscale = 'linear'
        self.yscale = 'linear'

    def get_num_plots_per_page(self) -> int:
        return self.rows * self.cols