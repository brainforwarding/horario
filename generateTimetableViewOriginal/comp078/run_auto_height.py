import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.sparse

from constants import *


def prepare_data(data_path):
    with open(data_path, 'r') as dsf:
        # generates a 2D data frame from the dataset using pandas
        ds_frame = dsf.read()
        ds_frame = pd.DataFrame([l.split() for l in ds_frame.split('\n')])

        # converts the data frame to a numpy 2d array and omit redundant columns
        ds_tmp = np.asarray(ds_frame)[: -1, 1: -1]

        # generate list of redundant rows indices
        redundant_rows = np.array([[i, i + 1, i + 2] for i in range(-1, ds_tmp.shape[0], 18)]).flatten()[1:]

        # remove obtained rows from the array
        ds_tmp = (np.delete(ds_tmp, redundant_rows, 0))

        # convert to integer from string
        ds_tmp = ds_tmp.astype(int)

        # Strings with zeroes. The length 20 since we got 5 days with 4 time periods each
        ds = np.zeros((numOfCourses, numOfRooms, 20))

        # The output from AMPL is in the form of a large matrix.This matrix is
        #  here rewritten to a three - dimensional tensor.This is done for X, Y and Z.
        # will then contain sub-matrices representing all the time-periods.
        for i in range(19):
            ds[:, :, i] = ds_tmp[numOfCourses * i: numOfCourses * (i + 1), :]

        return ds

def draw_timetable(height_ratios):
    f = plt.figure()
    axs = f.add_gridspec(len(periods), len(days), height_ratios = height_ratios)
    f.subplots_adjust(hspace=0)
    f.subplots_adjust(wspace=0)
    cells = [[None for i in range(len(days))] for i in range(len(periods))]

    for p in range(len(periods)):
        for d in range(len(days)):
            ax = f.add_subplot(axs[p, d])
            ax.set_xticks([])
            ax.set_yticks([])
            cells[p][d] = ax

    for n, day in enumerate(days):
        cells[0][n].set_title(day, weight='demibold')

    for n, period in enumerate(periods):
        cells[n][0].text(-0.15, 0.5, period,
                         va='center',
                         ha='right',
                         fontsize=11, weight='demibold')

    return cells

def plot_courses(desired_courses=[]):
    y_offset = .1 if not desired_courses else .16

    coursecol = coursecol1 if not desired_courses else coursecol2

    # 2d list that holds timetable items
    entries = [[[] for i in range(len(days))] for j in range(len(periods))]

    # Loop through all time periods and store in a matrix
    for k in range(20):

        # Find which day we are at
        day = int(np.ceil((k + 1) / 4) - 1)

        # Find which period we are at
        period = int(np.mod(k, 4))

        for ds, course_codes in [(x, lectures), (y, exercises), (z, comlabs)]:
            # Choose one time period at each iteration and
            # find the non-zero indexes from this matrix
            a = scipy.sparse.csc_matrix(ds[:, :, k])

            # i and j are vectors with the indexes
            i, j = np.nonzero(a)

            if i.shape[0] != 0:
                for ii, ij in zip(list(i), list(j)):
                    if not desired_courses or ii in desired_courses:
                        entries[period][day].append([ii, '{}  ---  {}'.format(course_codes[ii], rooms[ij])])


    # generates a list representing rows height ratios (for full timetables only)
    if not desired_courses:
        height_ratios = list(map(lambda h: len(max(h, key=lambda l: len(l))), entries))
    else:
        height_ratios = [1 for i in range(len(entries))]

    # draws the empty timetable
    cells = draw_timetable(height_ratios)

    height_ratios = np.asarray(height_ratios) / max(height_ratios)

    for period in range(len(periods)):
        for day in range(len(days)):
            y_disp = 0

            for entry in entries[period][day]:
                cells[period][day].text(.5, (1 - .08 / height_ratios[period]) - y_disp,
                                        entry[1],
                                        va='center',
                                        ha='center',
                                        fontsize=9,
                                        bbox=dict(boxstyle="round",
                                                  ec=coursecol[entry[0]],
                                                  fc=coursecol[entry[0]],
                                                  )
                                        )
                y_disp += y_offset / height_ratios[period]

    # draws the colors legend in top-left corner cell
    if desired_courses:
        cells[0][0].text(.4, .8, 'Color 1:', va='center', ha='center', fontsize=9)
        cells[0][0].text(.4, .6, 'Color 2:', va='center', ha='center', fontsize=9)
        cells[0][0].text(.6, .8,
                         '     ', va='center', ha='center', fontsize=9,
                         bbox=dict(boxstyle="round", ec=color1, fc=color1)
                         )
        cells[0][0].text(.6, .6,
                         '     ', va='center', ha='center', fontsize=9,
                         bbox=dict(boxstyle="round", ec=color2, fc=color2)
                         )


if __name__ == '__main__':
    # Getting AMPL data, that is lectures(x), exercises(y) and computer labs(z).
    x = prepare_data('ds/x.txt')
    y = prepare_data('ds/y.txt')
    z = prepare_data('ds/z.txt')

    plot_courses()

    # NOTICE: indices start from 0
    plot_courses(desired_courses=[3, 14, 4, 12])

    # shows the final plot
    plt.show()